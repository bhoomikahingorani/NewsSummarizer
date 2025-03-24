from typing import List, Dict, Optional, Any
from pydantic import BaseModel

class Article(BaseModel):
    """Model for a single news article."""
    title: str
    summary: str
    sentiment: str
    topics: List[str]
    url: str
    date: Optional[str] = None
    source: Optional[str] = None

class TopicOverlap(BaseModel):
    """Model for topic overlap between articles."""
    common_topics: List[str]
    unique_topics: Dict[str, List[str]]

class Comparison(BaseModel):
    """Model for comparison between articles."""
    comparison: str
    impact: str

class SentimentDistribution(BaseModel):
    """Model for sentiment distribution across articles."""
    positive: int
    negative: int
    neutral: int

class ComparativeSentiment(BaseModel):
    """Model for comparative sentiment analysis."""
    sentiment_distribution: SentimentDistribution
    coverage_differences: List[Comparison]
    topic_overlap: TopicOverlap

class CompanyNewsAnalysis(BaseModel):
    """Complete model for company news analysis."""
    company: str
    articles: List[Article]
    comparative_sentiment_score: ComparativeSentiment
    final_sentiment_analysis: str
    audio_path: Optional[str] = None
