from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from typing import List, Dict, Any, Optional
import logging
from Utils.news_extractor import NewsExtractor
from Utils.sentiment import SentimentAnalyzer
from Utils.comparative import ComparativeAnalyzer
from Utils.tts import TextToSpeech
from Utils.models import CompanyNewsAnalysis, Article, ComparativeSentiment
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="News Sentiment API", description="API for news sentiment analysis and TTS")

# Initialize components
news_extractor = NewsExtractor()
sentiment_analyzer = SentimentAnalyzer()
comparative_analyzer = ComparativeAnalyzer()
text_to_speech = TextToSpeech()

# Models for API requests/responses
class CompanyRequest(BaseModel):
    """Request model for company name."""
    company_name: str
    num_articles: Optional[int] = 10
    use_dummy_data: Optional[bool] = False

# API endpoints
@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "News Sentiment Analysis API is running. Access /docs for API documentation."}

@app.post("/analyze", response_model=CompanyNewsAnalysis)
def analyze_company(request: CompanyRequest):
    """
    Analyze news articles for a company.
    
    Args:
        request: CompanyRequest object with company name
        
    Returns:
        CompanyNewsAnalysis object with results
    """
    try:
        company_name = request.company_name
        
        logger.info(f"Analyzing news for company: {company_name}")
        
        # Extract news articles
        if request.use_dummy_data:
            articles = news_extractor.get_dummy_articles(company_name, request.num_articles)
        else:
            articles = news_extractor.search_news(company_name, request.num_articles)
        
        if not articles:
            raise HTTPException(status_code=404, detail=f"No news articles found for {company_name}")
        
        # Analyze sentiment for each article
        analyzed_articles = []
        for article in articles:
            analyzed_article = sentiment_analyzer.analyze_article(article)
            analyzed_articles.append(analyzed_article)
        
        # Perform comparative analysis
        comparative_sentiment = comparative_analyzer.analyze(analyzed_articles, company_name)
        
        # Generate final sentiment analysis
        final_sentiment = comparative_analyzer.generate_final_sentiment_analysis(
            analyzed_articles, company_name
        )
        
        # Convert articles to proper model format
        article_models = []
        for article in analyzed_articles:
            article_models.append(
                Article(
                    title=article.get('title', 'Untitled'),
                    summary=article.get('summary', ''),
                    sentiment=article.get('sentiment', 'Neutral'),
                    topics=article.get('topics', []),
                    url=article.get('url', ''),
                    date=article.get('date', None),
                    source=article.get('source', None)
                )
            )
        
        # Create the full analysis object
        analysis = CompanyNewsAnalysis(
            company=company_name,
            articles=article_models,
            comparative_sentiment_score=comparative_sentiment,
            final_sentiment_analysis=final_sentiment,
            audio_path=None  # Will be filled by TTS endpoint
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
def generate_tts(request: CompanyRequest):
    """
    Generate Hindi TTS for a company's sentiment analysis.
    
    Args:
        request: CompanyRequest object with company name
        
    Returns:
        Dictionary with path to audio file
    """
    try:
        # First, get the analysis
        analysis = analyze_company(request)
        
        # Extract key points for TTS
        text_for_tts = f"{request.company_name} की समाचार विश्लेषण। {analysis.final_sentiment_analysis}"
        
        # Generate TTS
        audio_path = text_to_speech.text_to_speech(text_for_tts)
        
        return {
            "company": request.company_name,
            "audio_path": audio_path
        }
        
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the API server when executed directly
if __name__ == "__main__":
    uvicorn.run("api_file:app", host="0.0.0.0", port=8000, reload=True)
