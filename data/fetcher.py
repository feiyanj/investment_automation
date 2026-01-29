"""
Data Fetcher Module - VERSION 3.0
Comprehensive data collection following investment guide principles:
- 5-year financial history
- Quality indicators (FCF/NI, receivables growth, inventory turns)
- Multi-query news search with deduplication
- All derived metrics for deep analysis
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import numpy as np

from config import Config
from .news_fetcher import NewsFetcher
from .financial_calculator import FinancialCalculator


class DataFetcher:
    """
    Fetches and formats comprehensive financial data for deep value analysis.
    Follows the principle: collect all PUBLIC data, let LLM do the reasoning.
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        self.data = {}
        self.calculator = FinancialCalculator()
    
    def fetch_all_data(self) -> Dict:
        """
        Main method to fetch all financial data
        
        Returns:
            Dictionary containing comprehensive 5-year data
        """
        print(f"\n📊 Fetching comprehensive data for {self.ticker}...")
        
        try:
            self.data['ticker'] = self.ticker
            self.data['company_info'] = self._get_company_info()
            self.data['market_data'] = self._get_market_data()
            
            # Get 5-year financial statements
            self.data['income_statement_5y'] = self._get_income_statement_5y()
            self.data['balance_sheet_5y'] = self._get_balance_sheet_5y()
            self.data['cash_flow_5y'] = self._get_cash_flow_5y()
            
            # Calculate key metrics over 5 years
            self.data['key_metrics_5y'] = self._get_key_metrics_5y()
            
            # Get comprehensive news with multiple queries
            self.data['live_news'] = self._get_comprehensive_news()
            
            # Price history
            self.data['price_history'] = self._get_price_history()
            
            print(f"✅ Comprehensive data fetched successfully for {self.ticker}")
            return self.data
            
        except Exception as e:
            print(f"❌ Error fetching data for {self.ticker}: {str(e)}")
            raise
    
    def _get_company_info(self) -> Dict:
        """Get basic company information"""
        try:
            info = self.stock.info
            return {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'employees': info.get('fullTimeEmployees', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A')[:500]
            }
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch company info: {str(e)}")
            return {}
    
    def _get_price_history(self) -> str:
        """Get historical price data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=Config.PRICE_HISTORY_DAYS)
            hist = self.stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                return "No price history available"
            
            current_price = hist['Close'].iloc[-1]
            year_high = hist['High'].max()
            year_low = hist['Low'].min()
            year_start_price = hist['Close'].iloc[0]
            year_return = ((current_price - year_start_price) / year_start_price) * 100
            avg_volume = hist['Volume'].mean()
            
            return f"""
Price History (1 Year):
- Current Price: ${current_price:.2f}
- 52-Week High: ${year_high:.2f}
- 52-Week Low: ${year_low:.2f}
- Year-to-Date Return: {year_return:.2f}%
- Average Daily Volume: {avg_volume:,.0f}
- Price Trend: {'Upward' if year_return > 0 else 'Downward'}
""".strip()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch price history: {str(e)}")
            return "Price history unavailable"
    
    def _get_income_statement(self) -> str:
        """Get income statement data with revenue growth"""
        try:
            income_stmt = self.stock.financials
            
            if income_stmt.empty:
                return "Income statement not available"
            
            latest = income_stmt.iloc[:, 0]
            revenue = latest.get('Total Revenue', 0)
            gross_profit = latest.get('Gross Profit', 0)
            operating_income = latest.get('Operating Income', 0)
            net_income = latest.get('Net Income', 0)
            ebitda = latest.get('EBITDA', 0)
            
            # Calculate revenue growth
            revenue_growth_yoy = self.calculator.calculate_revenue_growth(income_stmt)
            self.data['revenue_growth_yoy'] = revenue_growth_yoy
            
            # Calculate margins
            margins = self.calculator.calculate_margins(
                revenue,
                gross_profit=gross_profit,
                operating_income=operating_income,
                net_income=net_income
            )
            
            return f"""
Income Statement (Most Recent Year):
- Total Revenue: ${revenue:,.0f}
- Revenue Growth YoY: {revenue_growth_yoy * 100:.1f}%
- Gross Profit: ${gross_profit:,.0f} (Margin: {margins.get('gross_profit_margin', 0):.2f}%)
- Operating Income: ${operating_income:,.0f} (Margin: {margins.get('operating_income_margin', 0):.2f}%)
- Net Income: ${net_income:,.0f} (Margin: {margins.get('net_income_margin', 0):.2f}%)
- EBITDA: ${ebitda:,.0f}
""".strip()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch income statement: {str(e)}")
            return "Income statement unavailable"
    
    def _get_balance_sheet(self) -> str:
        """Get balance sheet data"""
        try:
            balance_sheet = self.stock.balance_sheet
            
            if balance_sheet.empty:
                return "Balance sheet not available"
            
            latest = balance_sheet.iloc[:, 0]
            total_assets = latest.get('Total Assets', 0)
            total_liabilities = latest.get('Total Liabilities Net Minority Interest', 0)
            stockholder_equity = latest.get('Stockholders Equity', 0)
            total_debt = latest.get('Total Debt', 0)
            cash = latest.get('Cash And Cash Equivalents', 0)
            current_assets = latest.get('Current Assets', 0)
            current_liabilities = latest.get('Current Liabilities', 0)
            
            # Calculate ratios
            debt_to_equity = (total_debt / stockholder_equity) if stockholder_equity else 0
            current_ratio = (current_assets / current_liabilities) if current_liabilities else 0
            
            return f"""
Balance Sheet (Most Recent Quarter):
- Total Assets: ${total_assets:,.0f}
- Total Liabilities: ${total_liabilities:,.0f}
- Stockholders' Equity: ${stockholder_equity:,.0f}
- Total Debt: ${total_debt:,.0f}
- Cash & Equivalents: ${cash:,.0f}
- Current Ratio: {current_ratio:.2f}
- Debt-to-Equity Ratio: {debt_to_equity:.2f}
""".strip()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch balance sheet: {str(e)}")
            return "Balance sheet unavailable"
    
    def _get_cash_flow(self) -> str:
        """Get cash flow statement data"""
        try:
            cash_flow = self.stock.cashflow
            
            if cash_flow.empty:
                return "Cash flow statement not available"
            
            latest = cash_flow.iloc[:, 0]
            operating_cf = latest.get('Operating Cash Flow', 0)
            investing_cf = latest.get('Investing Cash Flow', 0)
            financing_cf = latest.get('Financing Cash Flow', 0)
            free_cash_flow = latest.get('Free Cash Flow', 0)
            capex = latest.get('Capital Expenditure', 0)
            
            return f"""
Cash Flow Statement (Most Recent Year):
- Operating Cash Flow: ${operating_cf:,.0f}
- Investing Cash Flow: ${investing_cf:,.0f}
- Financing Cash Flow: ${financing_cf:,.0f}
- Free Cash Flow: ${free_cash_flow:,.0f}
- Capital Expenditures: ${capex:,.0f}
- FCF Quality: {'Strong' if free_cash_flow > 0 else 'Weak'}
""".strip()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch cash flow: {str(e)}")
            return "Cash flow statement unavailable"
    
    def _get_key_metrics(self) -> str:
        """Get key valuation metrics and ratios"""
        try:
            info = self.stock.info
            
            pe_ratio = info.get('trailingPE', 'N/A')
            forward_pe = info.get('forwardPE', 'N/A')
            pb_ratio = info.get('priceToBook', 'N/A')
            ps_ratio = info.get('priceToSalesTrailing12Months', 'N/A')
            peg_ratio_api = info.get('pegRatio', 'N/A')
            dividend_yield = info.get('dividendYield', 0)
            beta = info.get('beta', 'N/A')
            roe = info.get('returnOnEquity', 'N/A')
            roa = info.get('returnOnAssets', 'N/A')
            
            # Calculate PEG ratio manually
            revenue_growth_yoy = self.data.get('revenue_growth_yoy', 0)
            peg_calculated = self.calculator.calculate_peg_ratio(pe_ratio, revenue_growth_yoy)
            
            div_yield_pct = f"{dividend_yield * 100:.2f}%" if isinstance(dividend_yield, (int, float)) else "N/A"
            
            return f"""
Key Metrics & Ratios:
- P/E Ratio (Trailing): {pe_ratio}
- P/E Ratio (Forward): {forward_pe}
- Price-to-Book: {pb_ratio}
- Price-to-Sales: {ps_ratio}
- PEG Ratio (API): {peg_ratio_api}
- PEG Ratio (Calculated): {peg_calculated} [PE / (Revenue Growth % × 100)]
- Dividend Yield: {div_yield_pct}
- Beta: {beta}
- Return on Equity (ROE): {roe}
- Return on Assets (ROA): {roa}
""".strip()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch key metrics: {str(e)}")
            return "Key metrics unavailable"
    
    def _calculate_derived_metrics(self) -> str:
        """Calculate derived financial metrics"""
        try:
            cash_flow = self.stock.cashflow
            
            if cash_flow.empty:
                return "Cannot calculate derived metrics (no cash flow data)"
            
            # Calculate FCF history
            fcf_history = self.calculator.calculate_fcf_history(cash_flow)
            years_labels = [str(cash_flow.columns[i])[:10] for i in range(len(fcf_history))]
            
            # Calculate FCF growth rate (CAGR)
            fcf_growth_rate = self.calculator.calculate_cagr(fcf_history) * 100
            
            # Format output
            summary = f"""
Derived Metrics (Manual Calculations):
{'='*60}

FREE CASH FLOW HISTORY (Most Recent First):
"""
            for year, fcf in zip(years_labels, fcf_history):
                summary += f"  {year}: ${fcf:,.0f}\n"
            
            summary += f"""
FCF Growth Rate (CAGR): {fcf_growth_rate:.1f}%
Current FCF: ${fcf_history[0]:,.0f}
Average FCF (3Y): ${sum(fcf_history[:3])/min(3, len(fcf_history)):,.0f}

⚠️  CRITICAL FOR DCF VALUATION:
   - Current FCF will be used as starting point for DCF
   - Historical growth rate informs future projections
   - If FCF is negative, DCF cannot be calculated
"""
            
            # Store for valuation engine
            self.data['fcf_current'] = fcf_history[0] if fcf_history else 0
            self.data['fcf_growth_rate'] = fcf_growth_rate / 100
            
            return summary.strip()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not calculate derived metrics: {str(e)}")
            return f"Derived metrics unavailable (error: {str(e)})"
    
    def format_for_llm(self) -> str:
        """Format all data for LLM consumption"""
        if not self.data:
            self.fetch_all_data()
        
        company_info = self.data.get('company_info', {})
        
        return f"""
================================================================================
INVESTMENT ANALYSIS DATA FOR {self.ticker} - VERSION 2.0
================================================================================

COMPANY OVERVIEW:
-----------------
Name: {company_info.get('name', 'N/A')}
Sector: {company_info.get('sector', 'N/A')}
Industry: {company_info.get('industry', 'N/A')}
Market Cap: ${company_info.get('market_cap', 'N/A'):,}
Employees: {company_info.get('employees', 'N/A'):,}

Description: {company_info.get('description', 'N/A')}

{self.data.get('price_history', '')}

{self.data.get('income_statement', '')}

{self.data.get('balance_sheet', '')}

{self.data.get('cash_flow', '')}

{self.data.get('derived_metrics', '')}

{self.data.get('key_metrics', '')}

================================================================================
📰 LIVE MARKET NEWS & CATALYSTS
================================================================================
{self.data.get('live_news', 'No news available')}

================================================================================
END OF DATA
================================================================================
""".strip()
