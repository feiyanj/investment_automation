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
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # Model Configuration
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    # Available models with descriptions
    AVAILABLE_MODELS = {
        "1": {
            "name": "gemini-2.5-flash",
            "description": "Gemini 2.5 Flash - Fast and efficient (Default)",
            "provider": "gemini",
            "rpm": 10,
            "rpd": 250
        },
        "2": {
            "name": "gemini-2.5-flash-lite",
            "description": "Gemini 2.5 Flash Lite - Lighter, faster",
            "provider": "gemini",
            "rpm": 15,
            "rpd": 1500
        },
        "3": {
            "name": "gemini-3-flash-preview",
            "description": "Gemini 3 Flash Preview - Experimental latest version",
            "provider": "gemini",
            "rpm": 15,
            "rpd": 1500
        },
        "4": {
            "name": "deepseek-chat",
            "description": "DeepSeek Chat - Powerful reasoning model",
            "provider": "deepseek",
            "rpm": 60,
            "rpd": 10000
        },
        "5": {
            "name": "deepseek-reasoner",
            "description": "DeepSeek Reasoner (R1) - Advanced reasoning with CoT",
            "provider": "deepseek",
            "rpm": 60,
            "rpd": 10000
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
        if not cls.GEMINI_API_KEY and not cls.DEEPSEEK_API_KEY:
            raise ValueError(
                "No API key found. Please set either GEMINI_API_KEY or DEEPSEEK_API_KEY "
                "in your .env file."
            )
        return True
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if API key is configured without raising error"""
        return cls.GEMINI_API_KEY is not None or cls.DEEPSEEK_API_KEY is not None
    
    @classmethod
    def get_model_provider(cls, model_name: str) -> str:
        """Get the provider (gemini/deepseek) for a given model name"""
        for model_info in cls.AVAILABLE_MODELS.values():
            if model_info["name"] == model_name:
                return model_info["provider"]
        # Default to gemini for backward compatibility
        return "gemini"


# Don't validate on import - validate when needed
