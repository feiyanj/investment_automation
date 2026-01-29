"""
Formatting Utilities
Functions for formatting numbers, currencies, and percentages
"""
from typing import Union, Optional


def format_currency(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format a number as currency (USD)
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string (e.g., "$1,234,567.89")
    """
    if not isinstance(value, (int, float)):
        return "N/A"
    
    if decimals == 0:
        return f"${value:,.0f}"
    else:
        return f"${value:,.{decimals}f}"


def format_percentage(value: Union[int, float], decimals: int = 2) -> str:
    """
    Format a number as percentage
    
    Args:
        value: Number to format (e.g., 0.15 for 15%)
        decimals: Number of decimal places
        
    Returns:
        Formatted string (e.g., "15.00%")
    """
    if not isinstance(value, (int, float)):
        return "N/A"
    
    return f"{value * 100:.{decimals}f}%"


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format a number with thousand separators
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string (e.g., "1,234,567")
    """
    if not isinstance(value, (int, float)):
        return "N/A"
    
    if decimals == 0:
        return f"{value:,.0f}"
    else:
        return f"{value:,.{decimals}f}"


def format_large_number(value: Union[int, float]) -> str:
    """
    Format large numbers with B/M/K suffixes
    
    Args:
        value: Number to format
        
    Returns:
        Formatted string (e.g., "$1.23B", "$456.7M")
    """
    if not isinstance(value, (int, float)):
        return "N/A"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1_000_000_000:
        return f"{sign}${abs_value / 1_000_000_000:.2f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}${abs_value / 1_000_000:.2f}M"
    elif abs_value >= 1_000:
        return f"{sign}${abs_value / 1_000:.2f}K"
    else:
        return f"{sign}${abs_value:.2f}"
