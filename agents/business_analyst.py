"""
Business Analyst Module - MODULE 2
===================================
Provides business understanding and key events extraction before agent analysis
"""
from typing import Dict, Tuple
from agents.base_agent import BaseAgent
from agents.business_prompts import (
    BUSINESS_UNDERSTANDING_PROMPT,
    KEY_EVENTS_EXTRACTION_PROMPT,
    format_business_context
)


class BusinessAnalyst:
    """
    Analyzes business fundamentals and extracts key events
    Runs BEFORE the three investment agents to provide context
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize business analyst
        
        Args:
            model_name: Gemini model to use
        """
        self.model_name = model_name
        
        # Create two specialized agents
        self.business_agent = BaseAgent(
            name="Business Analyst",
            role="Business Understanding Expert",
            system_prompt=BUSINESS_UNDERSTANDING_PROMPT,
            model_name=model_name,
            agent_type="business_analyst"
        )
        
        self.events_agent = BaseAgent(
            name="Events Analyst",
            role="Material Events Extraction Expert",
            system_prompt=KEY_EVENTS_EXTRACTION_PROMPT,
            model_name=model_name,
            agent_type="events_analyst"
        )
    
    def analyze_business(self, financial_data: str, company_info: Dict) -> str:
        """
        Perform deep business understanding analysis
        
        Args:
            financial_data: Formatted 5-year financial data
            company_info: Company basic information
            
        Returns:
            Business understanding analysis
        """
        company_name = company_info.get('name', 'Unknown')
        ticker = company_info.get('ticker', 'N/A')
        
        # Prepare prompt with company-specific info
        prompt = BUSINESS_UNDERSTANDING_PROMPT.replace('{COMPANY_NAME}', company_name)
        prompt = prompt.replace('{TICKER}', ticker)
        
        # Add financial data context
        context = f"""
Company: {company_name} ({ticker})
Sector: {company_info.get('sector', 'N/A')}
Industry: {company_info.get('industry', 'N/A')}

{financial_data}

Based on this comprehensive 5-year financial data, provide your business analysis.
"""
        
        print("\n🔍 Analyzing business fundamentals...")
        analysis = self.business_agent.analyze(context)
        
        return analysis
    
    def extract_key_events(self, news_data: list, company_info: Dict) -> str:
        """
        Extract material events from news
        
        Args:
            news_data: List of news articles
            company_info: Company basic information
            
        Returns:
            Structured key events
        """
        company_name = company_info.get('name', 'Unknown')
        ticker = company_info.get('ticker', 'N/A')
        
        if not news_data:
            return "No recent news available for analysis."
        
        # Format news for analysis
        news_text = self._format_news(news_data)
        
        # Prepare prompt with company-specific info
        prompt = KEY_EVENTS_EXTRACTION_PROMPT.replace('{COMPANY_NAME}', company_name)
        prompt = prompt.replace('{TICKER}', ticker)
        prompt = prompt.replace('{NEWS_COUNT}', str(len(news_data)))
        
        context = f"""
Company: {company_name} ({ticker})

NEWS ARTICLES ({len(news_data)} articles):
{'-'*80}

{news_text}

Extract the material events following the framework provided.
"""
        
        print(f"\n📰 Extracting key events from {len(news_data)} news articles...")
        events = self.events_agent.analyze(context)
        
        return events
    
    def _format_news(self, news_data: list) -> str:
        """Format news articles for LLM consumption"""
        formatted = ""
        
        for i, article in enumerate(news_data, 1):
            formatted += f"""
[Article {i}]
Title: {article.get('title', 'N/A')}
Date: {article.get('date', 'N/A')}
Source: {article.get('source', 'N/A')}
Summary: {article.get('snippet', 'N/A')[:300]}...

"""
        
        return formatted
    
    def get_full_context(
        self,
        financial_data: str,
        company_info: Dict,
        news_data: list
    ) -> Tuple[str, str, str]:
        """
        Get complete business context for investment agents
        
        Args:
            financial_data: 5-year financial data
            company_info: Company information
            news_data: Recent news articles
            
        Returns:
            Tuple of (business_understanding, key_events, formatted_context)
        """
        # Analyze business
        business_understanding = self.analyze_business(financial_data, company_info)
        
        # Extract key events
        key_events = self.extract_key_events(news_data, company_info)
        
        # Format for agent consumption
        formatted_context = format_business_context(business_understanding, key_events)
        
        return business_understanding, key_events, formatted_context


def test_business_analyst():
    """Test the business analyst with sample data"""
    print("="*80)
    print("TESTING BUSINESS ANALYST MODULE")
    print("="*80)
    
    # Sample data
    company_info = {
        'name': 'Netflix Inc.',
        'ticker': 'NFLX',
        'sector': 'Communication Services',
        'industry': 'Entertainment'
    }
    
    financial_data = """
5-YEAR FINANCIAL SUMMARY:
- Revenue growth: 12% CAGR
- Gross margin: 40-43%
- Operating margin: 18-22%
- FCF: $3-5B annually
- Debt/Equity: 1.5x
"""
    
    news_data = [
        {
            'title': 'Netflix Q4 earnings beat expectations',
            'date': '2026-01-22',
            'source': 'Reuters',
            'snippet': 'Netflix reported Q4 revenue growth of 17.6%...'
        }
    ]
    
    analyst = BusinessAnalyst()
    business, events, context = analyst.get_full_context(
        financial_data,
        company_info,
        news_data
    )
    
    print("\n" + "="*80)
    print("BUSINESS UNDERSTANDING:")
    print("="*80)
    print(business[:500] + "...")
    
    print("\n" + "="*80)
    print("KEY EVENTS:")
    print("="*80)
    print(events[:500] + "...")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    test_business_analyst()
