"""
Data Fetcher Module - VERSION 3.0
=================================
Comprehensive 5-year financial data collection for deep value investing analysis.

Key Features:
- 5-year financial statements (Income/Balance/Cash Flow)
- Quality indicators (red flags detection)
- Derived metrics (ROE, ROIC, growth rates, margins)
- Multi-query news search with deduplication
- All data formatted for LLM consumption
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from difflib import SequenceMatcher

from config import Config
from .financial_calculator import FinancialCalculator


class DataFetcherV3:
    """
    Enhanced data fetcher following investment analysis guide principles:
    - Collect ALL public data (5 years)
    - Calculate quality indicators
    - Let LLM do the reasoning
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        self.data = {}
        self.calculator = FinancialCalculator()
    
    def fetch_all_data(self) -> Dict:
        """
        Fetch comprehensive 5-year financial data
        
        Returns:
            Dictionary with all financial data, metrics, and news
        """
        print(f"\n📊 [V3.0] Fetching comprehensive 5-year data for {self.ticker}...")
        
        try:
            # Basic info
            self.data['ticker'] = self.ticker
            self.data['company_info'] = self._get_company_info()
            self.data['market_data'] = self._get_market_data()
            
            # 5-year financial statements
            print("  ├─ Fetching 5-year income statements...")
            self.data['income_5y'] = self._get_income_statement_5y()
            
            print("  ├─ Fetching 5-year balance sheets...")
            self.data['balance_5y'] = self._get_balance_sheet_5y()
            
            print("  ├─ Fetching 5-year cash flows...")
            self.data['cashflow_5y'] = self._get_cash_flow_5y()
            
            # Calculate comprehensive metrics
            print("  ├─ Calculating 5-year metrics...")
            self.data['metrics_5y'] = self._calculate_metrics_5y()
            
            # Quality indicators (red flags)
            print("  ├─ Analyzing quality indicators...")
            self.data['quality_indicators'] = self._calculate_quality_indicators()
            
            # Comprehensive news
            print("  ├─ Fetching comprehensive news (8 queries)...")
            self.data['news'] = self._get_comprehensive_news()
            
            # Validate data quality (check for stock splits, unreasonable P/E ratios)
            print("  ├─ Validating data quality...")
            self._validate_data_quality()
            
            print(f"✅ [V3.0] Data collection complete for {self.ticker}")
            print(f"    └─ {len(self.data['news'])} news articles collected")
            
            return self.data
            
        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
            raise
    
    # =========================================================================
    # COMPANY INFO & MARKET DATA
    # =========================================================================
    
    def _get_company_info(self) -> Dict:
        """Get basic company information with current market price"""
        try:
            info = self.stock.info
            hist = self.stock.history(period="5d")  # Last 5 days to get current price
            
            # Get current price from history (more reliable) or info
            current_price = 0
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
            elif 'currentPrice' in info:
                current_price = float(info.get('currentPrice', 0))
            elif 'regularMarketPrice' in info:
                current_price = float(info.get('regularMarketPrice', 0))
            
            # Check for recent stock splits and add warning
            split_warning = None
            try:
                actions = self.stock.actions
                if not actions.empty and 'Stock Splits' in actions.columns:
                    from datetime import timezone
                    six_months_ago = pd.Timestamp.now(tz=actions.index.tz) - pd.Timedelta(days=180)
                    recent_splits = actions[actions.index > six_months_ago]
                    splits = recent_splits[recent_splits['Stock Splits'] > 0]
                    
                    if not splits.empty:
                        for date, row in splits.iterrows():
                            split_ratio = row['Stock Splits']
                            split_warning = f"CRITICAL: {split_ratio}:1 stock split on {date.strftime('%Y-%m-%d')}. Use provided trailingPE and trailingEps values - DO NOT calculate EPS manually from historical financials as they may not be split-adjusted."
            except:
                pass
            
            result = {
                'name': info.get('longName', 'N/A'),
                'longName': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A'),
                'website': info.get('website', 'N/A'),
                'employees': info.get('fullTimeEmployees', 0),
                'country': info.get('country', 'N/A'),
                'city': info.get('city', 'N/A'),
                'currentPrice': current_price,
                'regularMarketPrice': current_price,
                'price': current_price,
                # Add valuation metrics (CRITICAL: prevents agents from miscalculating P/E)
                'trailingPE': info.get('trailingPE'),
                'forwardPE': info.get('forwardPE'),
                'trailingEps': info.get('trailingEps'),
                'forwardEps': info.get('forwardEps'),
                'pegRatio': info.get('pegRatio'),
                'priceToBook': info.get('priceToBook'),
                'priceToSalesTrailing12Months': info.get('priceToSalesTrailing12Months'),
                'enterpriseToRevenue': info.get('enterpriseToRevenue'),
                'enterpriseToEbitda': info.get('enterpriseToEbitda'),
                # Add profitability metrics
                'profitMargins': info.get('profitMargins'),
                'operatingMargins': info.get('operatingMargins'),
                'returnOnAssets': info.get('returnOnAssets'),
                'returnOnEquity': info.get('returnOnEquity')
            }
            
            # Add stock split warning if detected
            if split_warning:
                result['STOCK_SPLIT_WARNING'] = split_warning
            
            return result
        except Exception as e:
            print(f"⚠️  Could not fetch company info: {e}")
            return {}
    
    def _get_market_data(self) -> Dict:
        """Get current market data"""
        try:
            info = self.stock.info
            hist = self.stock.history(period="1y")
            
            current_price = hist['Close'].iloc[-1] if not hist.empty else info.get('currentPrice', 0)
            year_high = hist['High'].max() if not hist.empty else info.get('fiftyTwoWeekHigh', 0)
            year_low = hist['Low'].min() if not hist.empty else info.get('fiftyTwoWeekLow', 0)
            
            return {
                'current_price': current_price,
                'market_cap': info.get('marketCap', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'beta': info.get('beta', 1.0),
                '52_week_high': year_high,
                '52_week_low': year_low,
                'ytd_return': ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100) if not hist.empty else 0
            }
        except Exception as e:
            print(f"⚠️  Could not fetch market data: {e}")
            return {}
    
    # =========================================================================
    # 5-YEAR FINANCIAL STATEMENTS
    # =========================================================================
    
    def _get_income_statement_5y(self) -> List[Dict]:
        """Get 5 years of income statement data"""
        try:
            income_stmt = self.stock.financials  # Annual data
            
            if income_stmt.empty:
                return []
            
            statements = []
            num_years = min(5, len(income_stmt.columns))
            
            for i in range(num_years):
                col = income_stmt.iloc[:, i]
                year = str(income_stmt.columns[i])[:10]
                
                statements.append({
                    'year': year,
                    'revenue': col.get('Total Revenue', 0),
                    'cost_of_revenue': col.get('Cost Of Revenue', 0),
                    'gross_profit': col.get('Gross Profit', 0),
                    'operating_expenses': col.get('Operating Expense', 0),
                    'operating_income': col.get('Operating Income', 0),
                    'interest_expense': abs(col.get('Interest Expense', 0)),  # Make positive
                    'net_income': col.get('Net Income', 0),
                    'rd_expense': col.get('Research And Development', 0),
                    'sga_expense': col.get('Selling General And Administrative', 0),
                    'ebitda': col.get('EBITDA', 0)
                })
            
            return statements
            
        except Exception as e:
            print(f"⚠️  Could not fetch income statements: {e}")
            return []
    
    def _get_balance_sheet_5y(self) -> List[Dict]:
        """Get 5 years of balance sheet data"""
        try:
            balance_sheet = self.stock.balance_sheet  # Annual data
            
            if balance_sheet.empty:
                return []
            
            sheets = []
            num_years = min(5, len(balance_sheet.columns))
            
            for i in range(num_years):
                col = balance_sheet.iloc[:, i]
                year = str(balance_sheet.columns[i])[:10]
                
                sheets.append({
                    'year': year,
                    'total_assets': col.get('Total Assets', 0),
                    'current_assets': col.get('Current Assets', 0),
                    'cash': col.get('Cash And Cash Equivalents', 0),
                    'accounts_receivable': col.get('Accounts Receivable', 0),
                    'inventory': col.get('Inventory', 0),
                    'total_liabilities': col.get('Total Liabilities Net Minority Interest', 0),
                    'current_liabilities': col.get('Current Liabilities', 0),
                    'long_term_debt': col.get('Long Term Debt', 0),
                    'total_debt': col.get('Total Debt', 0),
                    'total_equity': col.get('Stockholders Equity', 0),
                    'retained_earnings': col.get('Retained Earnings', 0),
                    'goodwill': col.get('Goodwill', 0)
                })
            
            return sheets
            
        except Exception as e:
            print(f"⚠️  Could not fetch balance sheets: {e}")
            return []
    
    def _get_cash_flow_5y(self) -> List[Dict]:
        """Get 5 years of cash flow data"""
        try:
            cash_flow = self.stock.cashflow  # Annual data
            
            if cash_flow.empty:
                return []
            
            flows = []
            num_years = min(5, len(cash_flow.columns))
            
            for i in range(num_years):
                col = cash_flow.iloc[:, i]
                year = str(cash_flow.columns[i])[:10]
                
                operating_cf = col.get('Operating Cash Flow', 0)
                capex = col.get('Capital Expenditure', 0)
                fcf = operating_cf - abs(capex)
                
                flows.append({
                    'year': year,
                    'operating_cash_flow': operating_cf,
                    'investing_cash_flow': col.get('Investing Cash Flow', 0),
                    'financing_cash_flow': col.get('Financing Cash Flow', 0),
                    'capex': capex,
                    'free_cash_flow': fcf,
                    'dividends_paid': col.get('Cash Dividends Paid', 0),
                    'stock_buybacks': col.get('Repurchase Of Capital Stock', 0)
                })
            
            return flows
            
        except Exception as e:
            print(f"⚠️  Could not fetch cash flows: {e}")
            return []
    
    # =========================================================================
    # COMPREHENSIVE METRICS (5-YEAR TRENDS)
    # =========================================================================
    
    def _calculate_metrics_5y(self) -> Dict:
        """Calculate all derived metrics over 5 years"""
        income = self.data.get('income_5y', [])
        balance = self.data.get('balance_5y', [])
        cashflow = self.data.get('cashflow_5y', [])
        
        if not income or not balance or not cashflow:
            return {}
        
        metrics = {
            'growth_rates': self._calc_growth_rates(income, cashflow),
            'profitability': self._calc_profitability(income),
            'returns': self._calc_returns(income, balance),
            'leverage': self._calc_leverage(balance),
            'efficiency': self._calc_efficiency(income, balance)
        }
        
        return metrics
    
    def _calc_growth_rates(self, income: List[Dict], cashflow: List[Dict]) -> Dict:
        """Calculate revenue, earnings, and FCF growth rates"""
        revenues = [stmt['revenue'] for stmt in income if stmt['revenue'] > 0]
        earnings = [stmt['net_income'] for stmt in income if stmt['net_income'] != 0]
        fcfs = [cf['free_cash_flow'] for cf in cashflow if cf['free_cash_flow'] != 0]
        
        return {
            'revenue_cagr': self.calculator.calculate_cagr(revenues),
            'earnings_cagr': self.calculator.calculate_cagr(earnings),
            'fcf_cagr': self.calculator.calculate_cagr(fcfs),
            'revenue_trend': revenues[::-1],  # Oldest to newest
            'earnings_trend': earnings[::-1],
            'fcf_trend': fcfs[::-1]
        }
    
    def _calc_profitability(self, income: List[Dict]) -> Dict:
        """Calculate margin trends"""
        margins = []
        for stmt in income:
            if stmt['revenue'] > 0:
                margins.append({
                    'year': stmt['year'],
                    'gross_margin': (stmt['gross_profit'] / stmt['revenue'] * 100) if stmt['revenue'] else 0,
                    'operating_margin': (stmt['operating_income'] / stmt['revenue'] * 100) if stmt['revenue'] else 0,
                    'net_margin': (stmt['net_income'] / stmt['revenue'] * 100) if stmt['revenue'] else 0
                })
        
        return {
            'margins_by_year': margins,
            'avg_gross_margin': np.mean([m['gross_margin'] for m in margins]) if margins else 0,
            'avg_operating_margin': np.mean([m['operating_margin'] for m in margins]) if margins else 0,
            'avg_net_margin': np.mean([m['net_margin'] for m in margins]) if margins else 0
        }
    
    def _calc_returns(self, income: List[Dict], balance: List[Dict]) -> Dict:
        """Calculate ROE, ROA, ROIC"""
        returns = []
        
        for i in range(min(len(income), len(balance))):
            inc = income[i]
            bal = balance[i]
            
            roe = (inc['net_income'] / bal['total_equity'] * 100) if bal['total_equity'] > 0 else 0
            roa = (inc['net_income'] / bal['total_assets'] * 100) if bal['total_assets'] > 0 else 0
            
            # ROIC = NOPAT / Invested Capital
            # NOPAT = Operating Income × (1 - Tax Rate)
            # Simplified: use operating income
            # Invested Capital = Total Assets - Current Liabilities
            invested_capital = bal['total_assets'] - bal['current_liabilities']
            roic = (inc['operating_income'] / invested_capital * 100) if invested_capital > 0 else 0
            
            returns.append({
                'year': inc['year'],
                'roe': roe,
                'roa': roa,
                'roic': roic
            })
        
        return {
            'returns_by_year': returns,
            'avg_roe': np.mean([r['roe'] for r in returns]) if returns else 0,
            'avg_roa': np.mean([r['roa'] for r in returns]) if returns else 0,
            'avg_roic': np.mean([r['roic'] for r in returns]) if returns else 0
        }
    
    def _calc_leverage(self, balance: List[Dict]) -> Dict:
        """Calculate debt ratios"""
        leverage = []
        
        for bal in balance:
            debt_to_equity = (bal['total_debt'] / bal['total_equity']) if bal['total_equity'] > 0 else 0
            current_ratio = (bal['current_assets'] / bal['current_liabilities']) if bal['current_liabilities'] > 0 else 0
            
            leverage.append({
                'year': bal['year'],
                'debt_to_equity': debt_to_equity,
                'current_ratio': current_ratio
            })
        
        return {
            'leverage_by_year': leverage,
            'avg_debt_to_equity': np.mean([l['debt_to_equity'] for l in leverage]) if leverage else 0,
            'avg_current_ratio': np.mean([l['current_ratio'] for l in leverage]) if leverage else 0
        }
    
    def _calc_efficiency(self, income: List[Dict], balance: List[Dict]) -> Dict:
        """Calculate asset turnover, inventory turnover, DSO"""
        efficiency = []
        
        for i in range(min(len(income), len(balance))):
            inc = income[i]
            bal = balance[i]
            
            asset_turnover = (inc['revenue'] / bal['total_assets']) if bal['total_assets'] > 0 else 0
            inventory_turnover = (inc['cost_of_revenue'] / bal['inventory']) if bal['inventory'] > 0 else 0
            dso = (bal['accounts_receivable'] / inc['revenue'] * 365) if inc['revenue'] > 0 else 0
            
            efficiency.append({
                'year': inc['year'],
                'asset_turnover': asset_turnover,
                'inventory_turnover': inventory_turnover,
                'days_sales_outstanding': dso
            })
        
        return {
            'efficiency_by_year': efficiency
        }
    
    # =========================================================================
    # QUALITY INDICATORS (RED FLAGS)
    # =========================================================================
    
    def _calculate_quality_indicators(self) -> Dict:
        """
        Calculate quality indicators and red flags
        Following the investment guide's red flag detection
        """
        income = self.data.get('income_5y', [])
        balance = self.data.get('balance_5y', [])
        cashflow = self.data.get('cashflow_5y', [])
        
        if not income or not balance or not cashflow:
            return {}
        
        red_flags = []
        
        # 1. Receivables growth vs Revenue growth (Revenue Quality)
        if len(income) >= 2 and len(balance) >= 2:
            revenue_growth = (income[0]['revenue'] - income[1]['revenue']) / income[1]['revenue'] if income[1]['revenue'] > 0 else 0
            ar_growth = (balance[0]['accounts_receivable'] - balance[1]['accounts_receivable']) / balance[1]['accounts_receivable'] if balance[1]['accounts_receivable'] > 0 else 0
            
            if ar_growth > revenue_growth and ar_growth > 0.05:  # AR growing faster by >5%
                red_flags.append({
                    'category': 'Revenue Quality',
                    'flag': 'Receivables growing faster than revenue',
                    'severity': 'MEDIUM',
                    'detail': f'AR growth: {ar_growth*100:.1f}% vs Revenue growth: {revenue_growth*100:.1f}%'
                })
        
        # 2. FCF vs Net Income (Profit Quality)
        if cashflow and income:
            fcf = cashflow[0]['free_cash_flow']
            ni = income[0]['net_income']
            
            fcf_to_ni_ratio = (fcf / ni) if ni > 0 else 0
            
            if fcf < ni * 0.8 and ni > 0:  # FCF < 80% of Net Income
                red_flags.append({
                    'category': 'Profit Quality',
                    'flag': 'Free Cash Flow significantly below Net Income',
                    'severity': 'HIGH',
                    'detail': f'FCF/NI ratio: {fcf_to_ni_ratio:.2f} (should be > 0.8)'
                })
        
        # 3. Inventory buildup
        if len(income) >= 2 and len(balance) >= 2:
            revenue_growth = (income[0]['revenue'] - income[1]['revenue']) / income[1]['revenue'] if income[1]['revenue'] > 0 else 0
            inventory_growth = (balance[0]['inventory'] - balance[1]['inventory']) / balance[1]['inventory'] if balance[1]['inventory'] > 0 else 0
            
            if inventory_growth > revenue_growth and inventory_growth > 0.10:  # Inventory growing faster by >10%
                red_flags.append({
                    'category': 'Inventory Quality',
                    'flag': 'Inventory growing faster than revenue',
                    'severity': 'MEDIUM',
                    'detail': f'Inventory growth: {inventory_growth*100:.1f}% vs Revenue growth: {revenue_growth*100:.1f}%'
                })
        
        # 4. Goodwill as % of assets
        if balance:
            goodwill_pct = (balance[0]['goodwill'] / balance[0]['total_assets'] * 100) if balance[0]['total_assets'] > 0 else 0
            
            if goodwill_pct > 30:
                red_flags.append({
                    'category': 'Balance Sheet',
                    'flag': 'High goodwill as % of assets',
                    'severity': 'HIGH',
                    'detail': f'Goodwill: {goodwill_pct:.1f}% of total assets (threshold: 30%)'
                })
        
        # 5. Debt service coverage
        if income and balance:
            interest = income[0]['interest_expense']
            ebit = income[0]['operating_income']
            
            interest_coverage = (ebit / interest) if interest > 0 else float('inf')
            
            if interest_coverage < 3 and interest > 0:
                red_flags.append({
                    'category': 'Debt Coverage',
                    'flag': 'Low interest coverage ratio',
                    'severity': 'HIGH',
                    'detail': f'Interest coverage: {interest_coverage:.1f}x (should be > 3x)'
                })
        
        # 6. Current ratio < 1 (Liquidity risk)
        if balance:
            current_ratio = (balance[0]['current_assets'] / balance[0]['current_liabilities']) if balance[0]['current_liabilities'] > 0 else 0
            
            if current_ratio < 1:
                red_flags.append({
                    'category': 'Liquidity',
                    'flag': 'Current ratio below 1.0',
                    'severity': 'HIGH',
                    'detail': f'Current ratio: {current_ratio:.2f} (should be > 1.0)'
                })
        
        return {
            'red_flags': red_flags,
            'red_flag_count': len(red_flags),
            'fcf_to_ni_ratio': fcf_to_ni_ratio if cashflow and income else 0,
            'goodwill_pct': goodwill_pct if balance else 0,
            'interest_coverage': interest_coverage if income else 0
        }
    
    # =========================================================================
    # COMPREHENSIVE NEWS SEARCH
    # =========================================================================
    
    def _get_comprehensive_news(self) -> List[Dict]:
        """
        Fetch news using 8 targeted queries
        Following the investment guide's multi-query strategy
        """
        try:
            from ddgs import DDGS
            
            # 8 targeted search queries
            queries = [
                f"{self.ticker} earnings",
                f"{self.ticker} quarterly results",
                f"{self.ticker} guidance",
                f"{self.ticker} CEO CFO",
                f"{self.ticker} acquisition merger",
                f"{self.ticker} new product",
                f"{self.ticker} competition",
                f"{self.ticker} SEC filing"
            ]
            
            all_news = []
            ddgs = DDGS()
            
            for query in queries:
                try:
                    results = ddgs.news(query, max_results=5, timelimit='3m')  # Last 3 months
                    
                    for article in results:
                        all_news.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'date': article.get('date', ''),
                            'snippet': article.get('body', ''),
                            'source': article.get('source', ''),
                            'query': query
                        })
                    
                except Exception as e:
                    print(f"  ⚠️  Query '{query}' failed: {e}")
                    continue
            
            # Deduplicate by title similarity
            deduplicated = self._deduplicate_news(all_news)
            
            return deduplicated
            
        except Exception as e:
            print(f"⚠️  Could not fetch news: {e}")
            return []
    
    def _deduplicate_news(self, news: List[Dict]) -> List[Dict]:
        """Remove duplicate news articles based on title similarity"""
        if not news:
            return []
        
        unique_news = []
        seen_titles = []
        
        for article in news:
            title = article['title'].lower()
            is_duplicate = False
            
            # Check similarity with existing titles
            for seen in seen_titles:
                similarity = SequenceMatcher(None, title, seen).ratio()
                if similarity > 0.8:  # 80% similar = duplicate
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_news.append(article)
                seen_titles.append(title)
        
        return unique_news
    
    # =========================================================================
    # FORMAT FOR LLM
    # =========================================================================
    
    def format_for_llm(self) -> str:
        """
        Format all collected data for LLM consumption
        Following the investment guide's data structure
        """
        if not self.data:
            self.fetch_all_data()
        
        output = f"""
{'='*80}
COMPREHENSIVE FINANCIAL DATA - {self.ticker}
DATA COLLECTION VERSION 3.0
{'='*80}

"""
        
        # Company Info
        output += self._format_company_info()
        
        # Market Data
        output += self._format_market_data()
        
        # 5-Year Financial Statements
        output += self._format_financial_statements_5y()
        
        # 5-Year Metrics & Trends
        output += self._format_metrics_5y()
        
        # Quality Indicators (Red Flags)
        output += self._format_quality_indicators()
        
        # News
        output += self._format_news()
        
        return output
    
    def _format_company_info(self) -> str:
        """Format company information"""
        info = self.data.get('company_info', {})
        
        return f"""
## COMPANY OVERVIEW
{'-'*80}
Name:        {info.get('name', 'N/A')}
Ticker:      {self.ticker}
Sector:      {info.get('sector', 'N/A')}
Industry:    {info.get('industry', 'N/A')}
Employees:   {info.get('employees', 0):,}
Location:    {info.get('city', 'N/A')}, {info.get('country', 'N/A')}

Description:
{info.get('description', 'N/A')}

"""
    
    def _format_market_data(self) -> str:
        """Format current market data"""
        market = self.data.get('market_data', {})
        
        return f"""
## CURRENT MARKET DATA
{'-'*80}
Current Price:       ${market.get('current_price', 0):.2f}
Market Cap:          ${market.get('market_cap', 0):,.0f}
Shares Outstanding:  {market.get('shares_outstanding', 0):,.0f}
Beta:                {market.get('beta', 1.0):.2f}
52-Week High:        ${market.get('52_week_high', 0):.2f}
52-Week Low:         ${market.get('52_week_low', 0):.2f}
YTD Return:          {market.get('ytd_return', 0):.2f}%

"""
    
    def _format_financial_statements_5y(self) -> str:
        """Format 5-year financial statements"""
        income = self.data.get('income_5y', [])
        balance = self.data.get('balance_5y', [])
        cashflow = self.data.get('cashflow_5y', [])
        
        output = f"""
## FINANCIAL STATEMENTS (5-YEAR HISTORY)
{'-'*80}

### Income Statement (Annual, Most Recent First)
"""
        
        # Income statement table
        if income:
            output += "\n"
            output += f"{'Year':<12}"
            for stmt in income[:5]:
                output += f"{stmt['year']:<15}"
            output += "\n" + "-" * 80 + "\n"
            
            # Revenues
            output += f"{'Revenue':<12}"
            for stmt in income[:5]:
                output += f"${stmt['revenue']/1e9:>13,.1f}B"
            output += "\n"
            
            # Gross Profit
            output += f"{'Gross Profit':<12}"
            for stmt in income[:5]:
                output += f"${stmt['gross_profit']/1e9:>13,.1f}B"
            output += "\n"
            
            # Operating Income
            output += f"{'Op Income':<12}"
            for stmt in income[:5]:
                output += f"${stmt['operating_income']/1e9:>13,.1f}B"
            output += "\n"
            
            # Net Income
            output += f"{'Net Income':<12}"
            for stmt in income[:5]:
                output += f"${stmt['net_income']/1e9:>13,.1f}B"
            output += "\n"
            
            # R&D
            output += f"{'R&D':<12}"
            for stmt in income[:5]:
                output += f"${stmt['rd_expense']/1e9:>13,.1f}B"
            output += "\n"
        
        output += "\n### Balance Sheet (Annual, Most Recent First)\n"
        
        if balance:
            output += "\n"
            output += f"{'Year':<12}"
            for stmt in balance[:5]:
                output += f"{stmt['year']:<15}"
            output += "\n" + "-" * 80 + "\n"
            
            # Total Assets
            output += f"{'Total Assets':<12}"
            for stmt in balance[:5]:
                output += f"${stmt['total_assets']/1e9:>13,.1f}B"
            output += "\n"
            
            # Cash
            output += f"{'Cash':<12}"
            for stmt in balance[:5]:
                output += f"${stmt['cash']/1e9:>13,.1f}B"
            output += "\n"
            
            # Total Debt
            output += f"{'Total Debt':<12}"
            for stmt in balance[:5]:
                output += f"${stmt['total_debt']/1e9:>13,.1f}B"
            output += "\n"
            
            # Equity
            output += f"{'Equity':<12}"
            for stmt in balance[:5]:
                output += f"${stmt['total_equity']/1e9:>13,.1f}B"
            output += "\n"
            
            # Goodwill
            output += f"{'Goodwill':<12}"
            for stmt in balance[:5]:
                output += f"${stmt['goodwill']/1e9:>13,.1f}B"
            output += "\n"
        
        output += "\n### Cash Flow (Annual, Most Recent First)\n"
        
        if cashflow:
            output += "\n"
            output += f"{'Year':<12}"
            for stmt in cashflow[:5]:
                output += f"{stmt['year']:<15}"
            output += "\n" + "-" * 80 + "\n"
            
            # Operating CF
            output += f"{'Operating CF':<12}"
            for stmt in cashflow[:5]:
                output += f"${stmt['operating_cash_flow']/1e9:>13,.1f}B"
            output += "\n"
            
            # CapEx
            output += f"{'CapEx':<12}"
            for stmt in cashflow[:5]:
                output += f"${stmt['capex']/1e9:>13,.1f}B"
            output += "\n"
            
            # Free Cash Flow
            output += f"{'Free CF':<12}"
            for stmt in cashflow[:5]:
                output += f"${stmt['free_cash_flow']/1e9:>13,.1f}B"
            output += "\n"
            
            # Dividends
            output += f"{'Dividends':<12}"
            for stmt in cashflow[:5]:
                output += f"${stmt['dividends_paid']/1e9:>13,.1f}B"
            output += "\n"
            
            # Buybacks
            output += f"{'Buybacks':<12}"
            for stmt in cashflow[:5]:
                output += f"${stmt['stock_buybacks']/1e9:>13,.1f}B"
            output += "\n"
        
        return output + "\n"
    
    def _format_metrics_5y(self) -> str:
        """Format 5-year metrics and trends"""
        metrics = self.data.get('metrics_5y', {})
        
        if not metrics:
            return "\n## METRICS NOT AVAILABLE\n\n"
        
        growth = metrics.get('growth_rates', {})
        profit = metrics.get('profitability', {})
        returns = metrics.get('returns', {})
        
        output = f"""
## KEY METRICS & TRENDS (5-YEAR)
{'-'*80}

### Growth Rates (CAGR)
Revenue:         {growth.get('revenue_cagr', 0)*100:>6.1f}%
Earnings:        {growth.get('earnings_cagr', 0)*100:>6.1f}%
Free Cash Flow:  {growth.get('fcf_cagr', 0)*100:>6.1f}%

### Profitability (5-Year Average)
Gross Margin:      {profit.get('avg_gross_margin', 0):>6.1f}%
Operating Margin:  {profit.get('avg_operating_margin', 0):>6.1f}%
Net Margin:        {profit.get('avg_net_margin', 0):>6.1f}%

### Returns (5-Year Average)
ROE:   {returns.get('avg_roe', 0):>6.1f}%
ROA:   {returns.get('avg_roa', 0):>6.1f}%
ROIC:  {returns.get('avg_roic', 0):>6.1f}%

"""
        return output
    
    def _format_quality_indicators(self) -> str:
        """Format quality indicators and red flags"""
        quality = self.data.get('quality_indicators', {})
        
        if not quality:
            return "\n## QUALITY INDICATORS NOT AVAILABLE\n\n"
        
        red_flags = quality.get('red_flags', [])
        
        output = f"""
## QUALITY INDICATORS & RED FLAGS
{'-'*80}

Red Flags Detected: {quality.get('red_flag_count', 0)}

"""
        
        if red_flags:
            for flag in red_flags:
                output += f"""
[{flag['severity']}] {flag['category']}: {flag['flag']}
    → {flag['detail']}
"""
        else:
            output += "✅ No significant red flags detected\n"
        
        output += f"""
Key Quality Metrics:
- FCF/Net Income Ratio:  {quality.get('fcf_to_ni_ratio', 0):.2f} (should be > 0.8)
- Goodwill % of Assets:  {quality.get('goodwill_pct', 0):.1f}% (threshold: 30%)
- Interest Coverage:     {quality.get('interest_coverage', 0):.1f}x (should be > 3x)

"""
        return output
    
    def _format_news(self) -> str:
        """Format news articles"""
        news = self.data.get('news', [])
        
        if not news:
            return "\n## NO NEWS AVAILABLE\n\n"
        
        output = f"""
## RECENT NEWS & EVENTS ({len(news)} articles)
{'-'*80}

"""
        
        for i, article in enumerate(news[:30], 1):  # Show max 30
            output += f"""
[{i}] {article['title']}
    Date: {article['date']}
    Source: {article['source']}
    {article['snippet'][:200]}...
    
"""
        
        return output
    
    def _validate_data_quality(self) -> None:
        """
        Validate data quality and warn about potential issues
        
        Checks for:
        - Recent stock splits that may affect historical data
        - Unreasonable P/E ratios (< 3 or > 200)
        - Missing critical valuation metrics
        """
        try:
            company_info = self.data.get('company_info', {})
            
            # Check for recent stock splits (last 6 months)
            try:
                actions = self.stock.actions
                if not actions.empty and 'Stock Splits' in actions.columns:
                    # Get timezone-aware datetime for comparison
                    from datetime import timezone
                    six_months_ago = pd.Timestamp.now(tz=actions.index.tz) - pd.Timedelta(days=180)
                    
                    recent_splits = actions[actions.index > six_months_ago]
                    splits = recent_splits[recent_splits['Stock Splits'] > 0]
                    
                    if not splits.empty:
                        for date, row in splits.iterrows():
                            split_ratio = row['Stock Splits']
                            print(f"    ⚠️  WARNING: Recent {split_ratio}:1 stock split on {date.strftime('%Y-%m-%d')}")
                            print(f"    └─ Historical financials may need manual adjustment")
            except Exception as e:
                # Silently continue if we can't check splits
                pass
            
            # Validate P/E ratio
            trailing_pe = company_info.get('trailingPE')
            current_price = company_info.get('currentPrice', 0)
            
            if trailing_pe is not None:
                if trailing_pe < 3:
                    print(f"    ⚠️  WARNING: Extremely low P/E ratio ({trailing_pe:.1f}x)")
                    print(f"    └─ This may indicate data quality issues or terminal business decline")
                elif trailing_pe > 200:
                    print(f"    ⚠️  WARNING: Extremely high P/E ratio ({trailing_pe:.1f}x)")
                    print(f"    └─ Company may be unprofitable or in hyper-growth phase")
            else:
                print(f"    ⚠️  WARNING: P/E ratio not available from data provider")
                print(f"    └─ Analysts will need to calculate manually from financials")
            
            # Validate EPS data
            trailing_eps = company_info.get('trailingEps')
            if trailing_eps is not None and current_price > 0:
                calculated_pe = current_price / trailing_eps
                if trailing_pe is not None and abs(calculated_pe - trailing_pe) > 1.0:
                    print(f"    ⚠️  WARNING: P/E calculation mismatch")
                    print(f"    └─ Reported P/E: {trailing_pe:.1f}x, Calculated: {calculated_pe:.1f}x")
            
        except Exception as e:
            print(f"    ⚠️  Could not validate data quality: {e}")

    # =========================================================================
    # FORMATTING FOR LLM CONSUMPTION
    # =========================================================================
