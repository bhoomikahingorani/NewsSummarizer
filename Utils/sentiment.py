import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any
import logging
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download NLTK resources
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.error(f"Error downloading NLTK resources: {e}")

class SentimentAnalyzer:
    """Class to analyze sentiment of news articles."""
    
    def __init__(self, use_transformer=False):
        """
        Initialize sentiment analyzer.
        
        Args:
            use_transformer: Whether to use transformer-based model (more accurate but slower)
        """
        self.use_transformer = use_transformer
        
        if use_transformer:
            try:
                # Use a pre-trained transformer model for more accurate sentiment analysis
                model_name = "ProsusAI/finbert"  # Financial news specific model
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
                self.transformer_pipeline = pipeline(
                    "sentiment-analysis", 
                    model=self.model, 
                    tokenizer=self.tokenizer,
                    return_all_scores=True
                )
            except Exception as e:
                logger.error(f"Error loading transformer model: {e}")
                logger.info("Falling back to NLTK's VADER")
                self.use_transformer = False
                self.vader = SentimentIntensityAnalyzer()
        else:
            # Use NLTK's VADER for sentiment analysis
            self.vader = SentimentIntensityAnalyzer()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment label and scores
        """
        if not text.strip():
            return {'label': 'Neutral', 'scores': {'positive': 0, 'negative': 0, 'neutral': 1}}
        
        try:
            if self.use_transformer:
                # Use the transformer model for sentiment analysis
                result = self.transformer_pipeline(text[:512])[0]  # Truncate to fit model's max length
                
                # Extract scores
                pos_score = next((item['score'] for item in result if item['label'] == 'positive'), 0)
                neg_score = next((item['score'] for item in result if item['label'] == 'negative'), 0)
                neu_score = next((item['score'] for item in result if item['label'] == 'neutral'), 0)
                
                scores = {
                    'positive': pos_score,
                    'negative': neg_score,
                    'neutral': neu_score
                }
                
                # Determine the label
                max_score = max(scores.items(), key=lambda x: x[1])
                label = max_score[0].capitalize()
                
            else:
                # Use VADER for sentiment analysis
                sentiment_scores = self.vader.polarity_scores(text)
                
                scores = {
                    'positive': sentiment_scores['pos'],
                    'negative': sentiment_scores['neg'],
                    'neutral': sentiment_scores['neu']
                }
                
                # Determine the sentiment label based on the compound score
                if sentiment_scores['compound'] >= 0.05:
                    label = 'Positive'
                elif sentiment_scores['compound'] <= -0.05:
                    label = 'Negative'
                else:
                    label = 'Neutral'
            
            return {
                'label': label,
                'scores': scores
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            # Default to neutral on error
            return {
                'label': 'Neutral',
                'scores': {'positive': 0, 'negative': 0, 'neutral': 1}
            }
    
    def extract_topics(self, text: str, num_topics: int = 3) -> List[str]:
        """
        Extract main topics from a text.
        
        Args:
            text: Text to analyze
            num_topics: Number of topics to extract
            
        Returns:
            List of topic strings
        """
        try:
            # Simple keyword extraction (in a real implementation, you might want to use
            # a more sophisticated approach like LDA or KeyBERT)
            
            # Tokenize and extract important words
            words = nltk.word_tokenize(text.lower())
            stops = set(nltk.corpus.stopwords.words('english'))
            words = [word for word in words if word.isalpha() and word not in stops]
            
            # Get frequency distribution
            freq_dist = nltk.FreqDist(words)
            
            # Get the most common words as topics
            common_words = [word for word, _ in freq_dist.most_common(num_topics)]
            
            # Capitalize topics
            topics = [word.capitalize() for word in common_words]
            
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return ["General"] * min(num_topics, 3)
    
    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """
        Create a simple extractive summary of a text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summary string
        """
        try:
            # Simple extractive summarization
            # In a real implementation, consider using a proper summarization model
            
            # Split into sentences
            sentences = nltk.sent_tokenize(text)
            
            if not sentences:
                return "No content available for summarization."
            
            # For a simple approach, just take the first few sentences
            # This is a very basic approach - a real implementation would use more sophisticated methods
            summary = " ".join(sentences[:2])
            
            # Truncate to maximum length
            if len(summary) > max_length:
                summary = summary[:max_length].rsplit(' ', 1)[0] + "..."
                
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return text[:100] + "..." if text else "Summary unavailable."
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a news article for sentiment, topics, and create a summary.
        
        Args:
            article: Dictionary containing article data
            
        Returns:
            Dictionary with sentiment analysis, topics, and summary added
        """
        try:
            content = article.get('content', '')
            
            # Get sentiment
            sentiment_result = self.analyze_sentiment(content)
            sentiment_label = sentiment_result['label']
            
            # Extract topics
            topics = self.extract_topics(content)
            
            # Create summary
            if 'summary' not in article or not article['summary']:
                summary = self.summarize_text(content)
            else:
                summary = article['summary']
            
            # Add results to article
            article_analysis = {
                **article,
                'sentiment': sentiment_label,
                'topics': topics,
                'summary': summary
            }
            
            return article_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            # Return original article with defaults
            return {
                **article,
                'sentiment': 'Neutral',
                'topics': ['General'],
                'summary': article.get('content', '')[:100] + "..." if article.get('content') else "Summary unavailable."
            }
