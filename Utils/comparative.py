from typing import List, Dict, Any
import logging
from collections import Counter
from Utils.models import ComparativeSentiment, SentimentDistribution, TopicOverlap, Comparison

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComparativeAnalyzer:
    """Class to perform comparative analysis across multiple news articles."""
    
    def analyze(self, articles: List[Dict[str, Any]], company_name: str) -> ComparativeSentiment:
        """
        Perform comparative analysis across articles.
        
        Args:
            articles: List of article dictionaries with sentiment and topics
            company_name: Name of the company being analyzed
            
        Returns:
            ComparativeSentiment object with analysis results
        """
        try:
            # Check if we have articles to analyze
            if not articles:
                return self._get_default_analysis()
            
            # Calculate sentiment distribution
            sentiment_distribution = self._calculate_sentiment_distribution(articles)
            
            # Analyze topic overlap
            topic_overlap = self._analyze_topic_overlap(articles)
            
            # Generate comparisons between articles
            coverage_differences = self._generate_coverage_differences(articles, company_name)
            
            # Create the comparative sentiment object
            comparative_sentiment = ComparativeSentiment(
                sentiment_distribution=sentiment_distribution,
                topic_overlap=topic_overlap,
                coverage_differences=coverage_differences
            )
            
            return comparative_sentiment
            
        except Exception as e:
            logger.error(f"Error in comparative analysis: {e}")
            return self._get_default_analysis()
    
    def _calculate_sentiment_distribution(self, articles: List[Dict[str, Any]]) -> SentimentDistribution:
        """
        Calculate the sentiment distribution across articles.
        
        Args:
            articles: List of article dictionaries with sentiment
            
        Returns:
            SentimentDistribution object
        """
        # Count sentiments
        sentiment_counts = Counter([article.get('sentiment', 'Neutral') for article in articles])
        
        # Create sentiment distribution
        distribution = SentimentDistribution(
            positive=sentiment_counts.get('Positive', 0),
            negative=sentiment_counts.get('Negative', 0),
            neutral=sentiment_counts.get('Neutral', 0)
        )
        
        return distribution
    
    def _analyze_topic_overlap(self, articles: List[Dict[str, Any]]) -> TopicOverlap:
        """
        Analyze topic overlap across articles.
        
        Args:
            articles: List of article dictionaries with topics
            
        Returns:
            TopicOverlap object
        """
        # Extract all topics
        all_topics = []
        for article in articles:
            all_topics.extend(article.get('topics', []))
        
        # Count topic occurrences
        topic_counts = Counter(all_topics)
        
        # Find common topics (appear in more than one article)
        common_topics = [topic for topic, count in topic_counts.items() if count > 1]
        
        # Find unique topics for each article
        unique_topics = {}
        for i, article in enumerate(articles):
            article_topics = set(article.get('topics', []))
            unique_to_article = article_topics - set(common_topics)
            if unique_to_article:
                unique_topics[f"Article {i+1}"] = list(unique_to_article)
        
        # Create topic overlap object
        topic_overlap = TopicOverlap(
            common_topics=common_topics,
            unique_topics=unique_topics
        )
        
        return topic_overlap
    
    def _generate_coverage_differences(self, articles: List[Dict[str, Any]], company_name: str) -> List[Comparison]:
        """
        Generate comparisons between articles.
        
        Args:
            articles: List of article dictionaries
            company_name: Name of the company being analyzed
            
        Returns:
            List of Comparison objects
        """
        comparisons = []
        
        # Group articles by sentiment
        positive_articles = [a for a in articles if a.get('sentiment') == 'Positive']
        negative_articles = [a for a in articles if a.get('sentiment') == 'Negative']
        neutral_articles = [a for a in articles if a.get('sentiment') == 'Neutral']
        
        # Compare positive vs negative coverage
        if positive_articles and negative_articles:
            pos_topics = set()
            for article in positive_articles:
                pos_topics.update(article.get('topics', []))
                
            neg_topics = set()
            for article in negative_articles:
                neg_topics.update(article.get('topics', []))
            
            comparison = Comparison(
                comparison=f"Positive articles focus on {', '.join(list(pos_topics)[:3])}, while negative articles discuss {', '.join(list(neg_topics)[:3])}.",
                impact=f"This mixed coverage suggests varying perspectives on {company_name}'s current situation."
            )
            comparisons.append(comparison)
        
        # Compare most recent articles (assuming articles are sorted by date)
        if len(articles) >= 2:
            recent_article = articles[0]
            older_article = articles[1]
            
            comparison = Comparison(
                comparison=f"Recent article '{recent_article.get('title', 'Untitled')}' is {recent_article.get('sentiment', 'Neutral').lower()}, while older article '{older_article.get('title', 'Untitled')}' is {older_article.get('sentiment', 'Neutral').lower()}.",
                impact=f"This suggests a potential {self._get_trend_description(recent_article.get('sentiment'), older_article.get('sentiment'))} trend in {company_name}'s news coverage."
            )
            comparisons.append(comparison)
        
        # Compare predominant topics
        all_topics = []
        for article in articles:
            all_topics.extend(article.get('topics', []))
        
        topic_counts = Counter(all_topics)
        most_common_topics = [topic for topic, _ in topic_counts.most_common(3)]
        
        if most_common_topics:
            comparison = Comparison(
                comparison=f"The most discussed topics across all articles are {', '.join(most_common_topics)}.",
                impact=f"This focus indicates the market's primary concerns regarding {company_name}."
            )
            comparisons.append(comparison)
        
        return comparisons
    
    def _get_trend_description(self, recent_sentiment: str, older_sentiment: str) -> str:
        """Get description of sentiment trend."""
        if recent_sentiment == older_sentiment:
            return "stable"
        
        if recent_sentiment == 'Positive' and older_sentiment in ['Neutral', 'Negative']:
            return "improving"
        
        if recent_sentiment == 'Negative' and older_sentiment in ['Neutral', 'Positive']:
            return "deteriorating"
        
        if recent_sentiment == 'Neutral':
            if older_sentiment == 'Positive':
                return "slightly worsening"
            else:
                return "slightly improving"
        
        return "shifting"
    
    def _get_default_analysis(self) -> ComparativeSentiment:
        """Return default analysis when errors occur."""
        return ComparativeSentiment(
            sentiment_distribution=SentimentDistribution(positive=0, negative=0, neutral=0),
            coverage_differences=[],
            topic_overlap=TopicOverlap(common_topics=[], unique_topics={})
        )
        
    def generate_final_sentiment_analysis(self, articles: List[Dict[str, Any]], company_name: str) -> str:
        """
        Generate a final summary of sentiment analysis.
        
        Args:
            articles: List of article dictionaries with sentiment
            company_name: Name of the company being analyzed
            
        Returns:
            String with final sentiment analysis
        """
        try:
            # Count sentiments
            sentiment_counts = Counter([article.get('sentiment', 'Neutral') for article in articles])
            total = sum(sentiment_counts.values())
            
            if total == 0:
                return f"No news coverage found for {company_name}."
            
            # Calculate percentages
            positive_pct = (sentiment_counts.get('Positive', 0) / total) * 100
            negative_pct = (sentiment_counts.get('Negative', 0) / total) * 100
            neutral_pct = (sentiment_counts.get('Neutral', 0) / total) * 100
            
            # Determine overall sentiment
            if positive_pct > negative_pct + 20:
                overall = "predominantly positive"
            elif negative_pct > positive_pct + 20:
                overall = "predominantly negative"
            elif positive_pct > negative_pct:
                overall = "slightly positive"
            elif negative_pct > positive_pct:
                overall = "slightly negative"
            else:
                overall = "neutral"
            
            # Generate insights based on sentiment distribution
            if positive_pct >= 70:
                outlook = "Potential for growth and positive market response is high."
            elif positive_pct >= 50:
                outlook = "Generally favorable outlook with some caution advised."
            elif negative_pct >= 70:
                outlook = "Significant challenges ahead, close monitoring recommended."
            elif negative_pct >= 50:
                outlook = "Some concerns exist that may impact performance."
            else:
                outlook = "Mixed signals with no clear directional trend."
            
            # Create final analysis
            analysis = f"{company_name}'s recent news coverage is {overall}. {outlook}"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating final sentiment analysis: {e}")
            return f"Unable to determine sentiment trend for {company_name} due to insufficient data."
