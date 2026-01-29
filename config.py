"""
Configuration Module
Central configuration for the entire investment analysis system
"""
import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration management"""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Model Configuration
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    # Available models with descriptions
    AVAILABLE_MODELS = {
        "1": {
            "name": "gemini-2.5-flash",
            "description": "Gemini 2.5 Flash - Fast and efficient (Default)",
            "rpm": 10,
            "rpd": 250
        },
        "2": {
            "name": "gemini-2.5-flash-lite",
            "description": "Gemini 2.5 Flash Lite - Lighter, faster",
            "rpm": 15,
            "rpd": 1500
        },
        "3": {
            "name": "gemini-3-flash-preview",
            "description": "Gemini 3 Flash Preview - Experimental latest version",
            "rpm": 15,
            "rpd": 1500
        }
    }
    
    # Rate Limiting (Gemini Free Tier)
    RATE_LIMITS = {
        "default": {
            "rpm": 10,
            "rpd": 250,
            "delay": 10
        }
    }
    
    # Agent Configuration
    AGENT_TEMPERATURE = 0.7
    AGENT_DELAY = 15  # Seconds between agent calls
    
    # Data Fetching Configuration
    PRICE_HISTORY_DAYS = 365
    MAX_NEWS_ARTICLES = 5
    NEWS_SEARCH_REGION = "wt-wt"  # Worldwide
    
    # DCF Valuation Configuration
    DCF_DEFAULTS = {
        "discount_rate": 0.10,  # 10% WACC
        "terminal_growth_rate": 0.03,  # 3% perpetual growth
        "high_growth_years": 5,  # Years of high growth
        "growth_rate_cap": 0.15,  # Maximum 15% growth assumption
        "min_growth_rate": 0.05,  # Minimum 5% for established companies
        "max_growth_rate": 0.30  # Maximum 30% FCF growth
    }
    
    # Display Configuration
    SEPARATOR_WIDTH = 80
    DECIMAL_PLACES = 2
    
    # Validation
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration (call this before using API)"""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please create a .env file with your API key."
            )
        return True
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if API key is configured without raising error"""
        return cls.GEMINI_API_KEY is not None


# Don't validate on import - validate when needed
