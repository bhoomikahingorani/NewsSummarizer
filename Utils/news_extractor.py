import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsExtractor:
    """Class to extract news articles about a company."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def search_news(self, company_name: str, num_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Search for news articles about a company.
        
        Args:
            company_name: Name of the company to search for
            num_articles: Number of articles to retrieve
            
        Returns:
            List of dictionaries containing article information
        """
        # This is a simplified implementation. In a real-world scenario, 
        # you might want to use a proper news API or scrape multiple sources.
        
        # Example search queries to find news articles
        search_urls = [
            f"https://news.google.com/search?q={company_name}",
            f"https://www.reuters.com/search/news?blob={company_name}",
            f"https://economictimes.indiatimes.com/search?searchtext={company_name}"
        ]
        
        article_urls = []
        
        # Get article URLs from search results
        for search_url in search_urls:
            try:
                response = requests.get(search_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Example extraction logic - this will need to be adapted for each site
                links = soup.find_all('a', href=True)
                for link in links:
                    url = link['href']
                    # Filter for likely article URLs (this is a simplified approach)
                    if '/article/' in url or '/story/' in url:
                        if not url.startswith('http'):
                            # Handle relative URLs
                            if url.startswith('/'):
                                base_url = '/'.join(search_url.split('/')[:3])
                                url = base_url + url
                            else:
                                continue
                        
                        if url not in article_urls:
                            article_urls.append(url)
                            
                    if len(article_urls) >= num_articles:
                        break
                        
                if len(article_urls) >= num_articles:
                    break
                    
            except requests.RequestException as e:
                logger.error(f"Error searching {search_url}: {e}")
                continue
                
        # Extract article data
        articles = []
        for url in article_urls[:num_articles]:
            try:
                article_data = self.extract_article(url)
                if article_data:
                    articles.append(article_data)
            except Exception as e:
                logger.error(f"Error extracting article from {url}: {e}")
                continue
                
        return articles
    
    def extract_article(self, url: str) -> Dict[str, Any]:
        """
        Extract information from a news article.
        
        Args:
            url: URL of the article to extract
            
        Returns:
            Dictionary containing article title, content, date, and source
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title = title.text.strip() if title else "No title found"
            
            # Extract date (this is a simplified approach)
            date = None
            date_tags = soup.find_all(['time', 'span', 'div'], class_=re.compile(r'date|time|publish', re.I))
            if date_tags:
                date = date_tags[0].text.strip()
            
            # Extract source
            source = url.split('/')[2]
            
            # Extract content (this is a simplified approach)
            content = ""
            article_tag = soup.find(['article', 'div'], class_=re.compile(r'article|story|content', re.I))
            if article_tag:
                paragraphs = article_tag.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs])
            else:
                # Fallback to all paragraphs
                paragraphs = soup.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs[:10]])  # Limit to first 10 paragraphs
            
            # Remove extra whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'date': date,
                'source': source
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None
            
    def get_dummy_articles(self, company_name: str, num_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Generate dummy articles for testing when web scraping is not possible.
        
        Args:
            company_name: Name of the company
            num_articles: Number of dummy articles to generate
            
        Returns:
            List of dictionaries containing article information
        """
        dummy_articles = []
        
        sentiments = ['Positive', 'Negative', 'Neutral']
        topics = [
            ['Revenue', 'Growth', 'Market Share'],
            ['Innovation', 'Technology', 'R&D'],
            ['Leadership', 'Management', 'CEO'],
            ['Sustainability', 'ESG', 'Climate'],
            ['Regulations', 'Compliance', 'Legal'],
            ['Competition', 'Market', 'Industry'],
            ['Products', 'Services', 'Customer Experience'],
            ['Investments', 'Funding', 'Venture Capital'],
            ['Earnings', 'Financial Results', 'Quarterly Reports'],
            ['Strategy', 'Future Plans', 'Vision']
        ]
        
        for i in range(num_articles):
            sentiment = sentiments[i % len(sentiments)]
            
            if sentiment == 'Positive':
                title = f"{company_name} Reports Strong Growth in Q{(i % 4) + 1}"
                content = f"{company_name} has reported exceptional results for the quarter, exceeding analyst expectations. The company's innovative approach to market challenges has paid off with significant revenue growth. Investors are optimistic about future prospects."
            elif sentiment == 'Negative':
                title = f"{company_name} Faces Challenges in Current Market Environment"
                content = f"{company_name} is struggling with recent market downturns and increasing competition. The company's latest quarterly results fell short of projections, leading to concerns among investors. Analysts suggest a strategic review may be necessary."
            else:
                title = f"{company_name} Announces New Strategic Initiative"
                content = f"{company_name} has announced a new strategic plan that aims to address changing market conditions. While the impact remains to be seen, industry experts are cautiously monitoring the development. The company maintains its annual guidance despite uncertainty."
            
            article_topics = topics[i % len(topics)]
            
            dummy_articles.append({
                'title': title,
                'content': content,
                'summary': content[:100] + "...",
                'url': f"https://example.com/article/{i}",
                'date': f"2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                'source': f"News Source {(i % 5) + 1}",
                'sentiment': sentiment,
                'topics': article_topics
            })
            
        return dummy_articles
