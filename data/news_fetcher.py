"""
News Fetcher Module
Fetches live news using DuckDuckGo Search
"""
from typing import List, Dict
from config import Config

try:
    from duckduckgo_search import DDGS
    NEWS_AVAILABLE = True
except ImportError:
    NEWS_AVAILABLE = False
    print("⚠️  duckduckgo-search not installed. Install with: pip install duckduckgo-search")


class NewsFetcher:
    """Fetches live news about stocks"""
    
    @staticmethod
    def fetch_news(ticker: str, max_results: int = None) -> str:
        """
        Fetch live news about a stock
        
        Args:
            ticker: Stock ticker symbol
            max_results: Maximum number of articles (default from config)
            
        Returns:
            Formatted news summary string
        """
        max_results = max_results or Config.MAX_NEWS_ARTICLES
        
        if not NEWS_AVAILABLE:
            return "Live news unavailable (duckduckgo-search not installed)"
        
        try:
            search_query = f"{ticker} stock news analysis catalysts risks 2025 2026"
            print(f"   📰 Searching for live news about {ticker}...")
            
            ddgs = DDGS()
            news_results = list(ddgs.news(
                keywords=search_query,
                max_results=max_results,
                region=Config.NEWS_SEARCH_REGION,
                safesearch='off'
            ))
            
            if not news_results:
                return "No recent news found for this ticker."
            
            news_summary = f"""
Live Market News (Top {len(news_results)} Recent Headlines):
{'='*60}
"""
            
            for idx, article in enumerate(news_results, 1):
                title = article.get('title', 'No title')
                body = article.get('body', 'No description')
                date = article.get('date', 'Unknown date')
                source = article.get('source', 'Unknown source')
                
                news_summary += f"""
[{idx}] {title}
    Source: {source} | Date: {date}
    Summary: {body[:200]}...
"""
            
            print(f"   ✅ Found {len(news_results)} recent news articles")
            return news_summary.strip()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch live news: {str(e)}")
            return f"Live news unavailable (error: {str(e)})"
