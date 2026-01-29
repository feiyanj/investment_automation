"""
Financial Calculator Module
Calculates derived financial metrics
"""
import numpy as np
from typing import List, Tuple, Dict
import pandas as pd


class FinancialCalculator:
    """Calculates derived financial metrics and ratios"""
    
    @staticmethod
    def calculate_fcf_history(cash_flow: pd.DataFrame) -> List[float]:
        """
        Calculate Free Cash Flow history
        
        Args:
            cash_flow: Cash flow statement DataFrame
            
        Returns:
            List of FCF values (most recent first)
        """
        fcf_history = []
        
        for i in range(min(4, len(cash_flow.columns))):
            col = cash_flow.iloc[:, i]
            
            operating_cf = col.get('Operating Cash Flow', 0)
            capex = col.get('Capital Expenditure', 0)
            
            # Calculate FCF (CapEx is usually negative)
            fcf = operating_cf - abs(capex)
            fcf_history.append(fcf)
        
        return fcf_history
    
    @staticmethod
    def calculate_cagr(values: List[float]) -> float:
        """
        Calculate Compound Annual Growth Rate (CAGR)
        Handles negative start values properly
        
        Args:
            values: List of values (most recent first)
            
        Returns:
            CAGR as decimal (e.g., 0.15 for 15%)
        """
        # Filter out zeros and NaN, but keep negatives
        clean_values = [
            v for v in values 
            if v != 0 and not (isinstance(v, float) and np.isnan(v))
        ]
        
        if len(clean_values) < 2:
            return 0
        
        start_value = clean_values[-1]  # Oldest (list is reversed)
        end_value = clean_values[0]     # Most recent
        num_periods = len(clean_values) - 1
        
        # Handle different scenarios
        if start_value > 0:
            # Normal CAGR: (End/Start)^(1/n) - 1
            cagr = ((end_value / start_value) ** (1 / num_periods)) - 1
        elif start_value < 0 and end_value > 0:
            # Negative to positive turnaround
            cagr = min(((end_value - start_value) / abs(start_value)) / num_periods, 2.0)
        elif start_value < 0 and end_value < 0:
            # Both negative
            cagr = -((abs(start_value) / abs(end_value)) ** (1 / num_periods) - 1)
        else:
            cagr = 0
        
        # Cap at reasonable bounds (-100% to +200%)
        return max(min(cagr, 2.0), -1.0)
    
    @staticmethod
    def calculate_revenue_growth(income_stmt: pd.DataFrame) -> float:
        """
        Calculate Year-over-Year revenue growth
        
        Args:
            income_stmt: Income statement DataFrame
            
        Returns:
            Revenue growth as decimal (e.g., 0.20 for 20%)
        """
        if len(income_stmt.columns) < 2:
            return 0
        
        revenue_current = income_stmt.iloc[:, 0].get('Total Revenue', 0)
        revenue_prior = income_stmt.iloc[:, 1].get('Total Revenue', 0)
        
        if revenue_prior > 0:
            return (revenue_current - revenue_prior) / revenue_prior
        
        return 0
    
    @staticmethod
    def calculate_peg_ratio(pe_ratio: float, revenue_growth: float) -> str:
        """
        Calculate PEG ratio
        
        Args:
            pe_ratio: P/E ratio
            revenue_growth: Revenue growth as decimal
            
        Returns:
            PEG ratio as formatted string or 'N/A'
        """
        if isinstance(pe_ratio, (int, float)) and pe_ratio > 0 and revenue_growth > 0:
            growth_percent = revenue_growth * 100
            peg = pe_ratio / growth_percent
            return f"{peg:.2f}"
        
        return "N/A"
    
    @staticmethod
    def calculate_margins(revenue: float, **kwargs) -> Dict[str, float]:
        """
        Calculate profit margins
        
        Args:
            revenue: Total revenue
            **kwargs: gross_profit, operating_income, net_income
            
        Returns:
            Dictionary of margin percentages
        """
        margins = {}
        
        if revenue > 0:
            for key, value in kwargs.items():
                margin_key = f"{key}_margin"
                margins[margin_key] = (value / revenue * 100) if value else 0
        
        return margins
