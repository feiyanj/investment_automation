"""
Data Package
Handles financial data fetching and processing
"""
from .fetcher_v3 import DataFetcherV3
from .financial_calculator import FinancialCalculator

# Legacy imports (kept for backward compatibility if needed)
try:
    from .fetcher import DataFetcher
except ImportError:
    DataFetcher = None

__all__ = ['DataFetcherV3', 'FinancialCalculator', 'DataFetcher']
