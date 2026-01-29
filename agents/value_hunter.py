"""
Value Hunter Agent Implementation (V3.0)
Professional value investing analysis with quality scoring and dynamic valuation
"""
import google.generativeai as genai
from typing import Dict, Optional, Tuple
from agents.base_agent import BaseAgent
from agents.value_hunter_prompts import (
    VALUE_HUNTER_SYSTEM_PROMPT,
    VALUE_HUNTER_ANALYSIS_PROMPT,
    format_value_context
)
from valuation.dcf_calculator import ValuationEngine


class ValueHunter(BaseAgent):
    """
    Value Hunter Agent - Professional value investing analysis
    
    Responsibilities:
    1. Financial quality assessment (0-10 score)
    2. Capital allocation analysis
    3. Competitive moat rating
    4. Dynamic multi-method valuation
    5. Margin of safety calculation
    6. Investment recommendation
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.4):
        """
        Initialize Value Hunter with specific temperature for balanced analysis
        
        Args:
            model_name: Gemini model to use (default: gemini-2.5-flash)
            temperature: 0.4 for rigorous but not overly conservative analysis
        """
        super().__init__(
            name="Value Hunter",
            role="Professional Value Investor",
            system_prompt=VALUE_HUNTER_SYSTEM_PROMPT,
            model_name=model_name,
            temperature=temperature
        )
        
    def analyze(
        self,
        data: Dict,
        info: Dict,
        business_context: str,
        key_events: str = ""
    ) -> str:
        """
        Conduct comprehensive value investment analysis
        
        Args:
            data: Complete financial data from DataFetcherV3
            info: Company information dictionary
            business_context: Business understanding from BusinessAnalyst
            key_events: Material events from news (optional)
            
        Returns:
            Comprehensive value analysis report
        """
        # Add key events to data if provided
        if key_events:
            data['key_events'] = key_events
        
        # Format context for the agent
        context = format_value_context(data, business_context, info)
        
        # Construct the analysis prompt
        full_prompt = f"""
{VALUE_HUNTER_ANALYSIS_PROMPT}

================================================================================
DATA FOR YOUR ANALYSIS:
================================================================================

{context}

================================================================================
BEGIN YOUR ANALYSIS:
================================================================================

Follow the exact structure outlined above. Calculate the financial quality score,
rate the moat, perform dynamic valuation with multiple methods, and provide a 
clear recommendation with margin of safety analysis.

Remember to:
- Base all assessments on the 5-year data provided
- Show your calculations and reasoning
- Be conservative and rigorous
- Admit when data is insufficient
- Focus on quality first, price second
"""
        
        # Get analysis from LLM
        print(f"\n🔍 {self.name} analyzing (this may take 30-60 seconds)...")
        
        try:
            # Generate response based on provider
            if self.provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=8192
                )
                analysis = response.choices[0].message.content
            else:
                # Gemini API
                response = self.model.generate_content(full_prompt)
                analysis = response.text
            
            print(f"✅ {self.name} completed analysis")
            
            return analysis
            
        except Exception as e:
            error_msg = f"❌ Error during {self.name}'s analysis: {str(e)}"
            print(error_msg)
            return error_msg
    
    def calculate_supplementary_valuation(
        self,
        data: Dict,
        info: Dict,
        quality_score: int,
        growth_rate: float,
        wacc: float
    ) -> Dict[str, any]:
        """
        Calculate supplementary valuation metrics using ValuationEngine
        
        This can be called separately to provide additional valuation data
        to the LLM or for verification purposes.
        
        Args:
            data: Financial data
            info: Company info
            quality_score: Financial quality score (0-10)
            growth_rate: Expected growth rate (as decimal)
            wacc: Weighted average cost of capital (as decimal)
            
        Returns:
            Dictionary with DCF, P/E, and P/FCF valuations
        """
        engine = ValuationEngine(info.get('symbol', 'UNKNOWN'))
        
        results = {
            'ticker': info.get('symbol'),
            'company': info.get('longName'),
            'current_price': info.get('currentPrice', 0)
        }
        
        # Get latest financials
        try:
            # Extract latest FCF if available (DataFetcherV3 format)
            if 'cashflow_5y' in data and data['cashflow_5y']:
                # cashflow_5y is a list of dicts, first item is most recent
                latest_cf = data['cashflow_5y'][0]
                latest_fcf = latest_cf.get('free_cash_flow', 0)
                
                # If FCF is 0, try to calculate it
                if latest_fcf == 0:
                    ocf = latest_cf.get('operating_cash_flow', 0)
                    capex = latest_cf.get('capex', 0)
                    if ocf and capex:
                        latest_fcf = ocf - abs(capex)
            else:
                latest_fcf = None
            
            # DCF Valuation
            if latest_fcf and latest_fcf > 0:
                shares = info.get('sharesOutstanding', 0)
                dcf_result = engine.calculate_dcf(
                    fcf=latest_fcf,
                    growth_rate=growth_rate,
                    discount_rate=wacc,
                    terminal_growth_rate=0.03,
                    high_growth_years=5,
                    shares_outstanding=shares
                )
                results['dcf'] = dcf_result
            else:
                results['dcf'] = {'error': 'FCF not available or negative'}
            
            # P/E Valuation
            trailing_eps = info.get('trailingEps', 0)
            forward_eps = info.get('forwardEps', 0)
            trailing_pe = info.get('trailingPE', 0)
            
            if trailing_eps or forward_eps:
                pe_result = engine.calculate_pe_valuation(
                    trailing_eps=trailing_eps if trailing_eps else 0,
                    forward_eps=forward_eps if forward_eps else 0,
                    historical_pe_5y=trailing_pe if trailing_pe else 20,  # Fallback
                    quality_score=quality_score,
                    growth_rate=growth_rate
                )
                results['pe'] = pe_result
            else:
                results['pe'] = {'error': 'EPS data not available'}
            
            # P/FCF Valuation
            if latest_fcf and latest_fcf > 0:
                shares = info.get('sharesOutstanding', 0)
                if shares > 0:
                    fcf_per_share = latest_fcf / shares
                    pfcf_result = engine.calculate_pfcf_valuation(
                        fcf_per_share=fcf_per_share,
                        historical_pfcf_5y=20,  # Default assumption
                        quality_score=quality_score,
                        growth_rate=growth_rate
                    )
                    results['pfcf'] = pfcf_result
                else:
                    results['pfcf'] = {'error': 'Shares outstanding not available'}
            else:
                results['pfcf'] = {'error': 'FCF not available'}
                
        except Exception as e:
            results['error'] = f"Valuation calculation error: {str(e)}"
        
        return results
    
    def get_analysis_summary(self, full_analysis: str) -> Dict[str, any]:
        """
        Extract key metrics from the full analysis text
        
        Handles multiple output formats from different models (Gemini, DeepSeek).
        Supports plain text, markdown bold, tables, and emojis.
        
        Args:
            full_analysis: Full text output from analyze()
            
        Returns:
            Dictionary with extracted key metrics
        """
        import re
        
        summary = {
            'quality_score': None,
            'moat_rating': None,
            'recommendation': None,
            'conviction': None,
            'margin_of_safety': None,
            'intrinsic_value': None,
            'current_price': None
        }
        
        try:
            # Quality score - multiple patterns
            patterns = [
                r'FINANCIAL QUALITY ASSESSMENT.*?\((\d+)/10',  # (8/10 Score)
                r'TOTAL FINANCIAL QUALITY SCORE[:\s]+\*?\*?(\d+)/10',  # Score: 8/10 or **8/10**
                r'\|\s*Financial Quality Score\s*\|\s*(\d+)/10',  # | Financial Quality Score | 8/10 |
                r'Quality Score[:\s]+\*?\*?(\d+)/10',  # Quality Score: 8/10
                r'\*\*Quality Score\*\*[:\s]+(\d+)/10',  # **Quality Score**: 8/10
            ]
            for pattern in patterns:
                match = re.search(pattern, full_analysis, re.IGNORECASE | re.DOTALL)
                if match:
                    summary['quality_score'] = int(match.group(1))
                    break
            
            # Moat rating
            moat_patterns = [
                (r'MOAT[:\s]+\*?\*?(STRONG|MEDIUM|MODERATE|WEAK|NONE)\*?\*?', 1),
                (r'\|\s*Moat\s*\|\s*(STRONG|MEDIUM|MODERATE|WEAK|NONE)', 1),
                (r'\*\*Moat\*\*[:\s]+(STRONG|MEDIUM|MODERATE|WEAK|NONE)', 1),
            ]
            for pattern, group in moat_patterns:
                match = re.search(pattern, full_analysis, re.IGNORECASE)
                if match:
                    moat = match.group(group).upper()
                    if 'STRONG' in moat:
                        summary['moat_rating'] = 'Strong'
                    elif 'MEDIUM' in moat or 'MODERATE' in moat:
                        summary['moat_rating'] = 'Medium'
                    elif 'WEAK' in moat:
                        summary['moat_rating'] = 'Weak'
                    elif 'NONE' in moat:
                        summary['moat_rating'] = 'None'
                    break
            
            # Recommendation - handles emoji + bold markdown
            rec_patterns = [
                r'RECOMMENDATION[:\s]+\*?\*?(STRONG BUY|BUY|HOLD|REDUCE|SELL|AVOID)\*?\*?',  # Plain
                r'🟢\s*\*\*(STRONG BUY|BUY)\*\*',  # 🟢 **BUY**
                r'🟡\s*\*\*HOLD\*\*',  # 🟡 **HOLD**
                r'🟠\s*\*\*REDUCE\*\*',  # 🟠 **REDUCE**
                r'🔴\s*\*\*(SELL|AVOID)\*\*',  # 🔴 **SELL**
                r'\|\s*Recommendation\s*\|\s*(STRONG BUY|BUY|HOLD|REDUCE|SELL|AVOID)',  # Table
                r'\*\*Recommendation\*\*[:\s]+\*?\*?(STRONG BUY|BUY|HOLD|REDUCE|SELL|AVOID)\*?\*?',  # **Recommendation**: **BUY**
            ]
            for pattern in rec_patterns:
                match = re.search(pattern, full_analysis, re.IGNORECASE)
                if match:
                    rec = match.group(1).upper()
                    if 'STRONG BUY' in rec:
                        summary['recommendation'] = 'STRONG BUY'
                    elif 'BUY' in rec:
                        summary['recommendation'] = 'BUY'
                    elif 'HOLD' in rec:
                        summary['recommendation'] = 'HOLD'
                    elif 'REDUCE' in rec or 'AVOID' in rec:
                        summary['recommendation'] = 'REDUCE'
                    elif 'SELL' in rec:
                        summary['recommendation'] = 'SELL'
                    break
            
            # Conviction - handles "Level" variant
            conv_patterns = [
                r'CONVICTION(?:\s+LEVEL)?[:\s]+\*?\*?(\d+)/10\*?\*?',  # CONVICTION: 8/10 or **8/10**
                r'\*\*Conviction(?:\s+Level)?\*\*[:\s]+(\d+)/10',  # **Conviction Level**: 8/10
                r'\|\s*Conviction\s*\|\s*(\d+)/10',  # | Conviction | 8/10 |
            ]
            for pattern in conv_patterns:
                match = re.search(pattern, full_analysis, re.IGNORECASE)
                if match:
                    summary['conviction'] = int(match.group(1))
                    break
            
            # Margin of safety
            mos_patterns = [
                r'MARGIN OF SAFETY[:\s]+\*?\*?([+-]?\d+(?:\.\d+)?)%',
                r'\*\*Margin of Safety\*\*[:\s]+([+-]?\d+(?:\.\d+)?)%',
                r'\|\s*Margin of Safety\s*\|\s*([+-]?\d+(?:\.\d+)?)%',
            ]
            for pattern in mos_patterns:
                match = re.search(pattern, full_analysis, re.IGNORECASE)
                if match:
                    summary['margin_of_safety'] = float(match.group(1))
                    break
            
            # Intrinsic value
            iv_patterns = [
                r'INTRINSIC VALUE[:\s]+\*?\*?\$(\d+(?:\.\d+)?)\*?\*?',
                r'\*\*Intrinsic Value\*\*[:\s]+\$(\d+(?:\.\d+)?)',
                r'\|\s*Intrinsic Value\s*\|\s*\$(\d+(?:\.\d+)?)',
                r'Fair Value[:\s]+\$(\d+(?:\.\d+)?)',
            ]
            for pattern in iv_patterns:
                match = re.search(pattern, full_analysis, re.IGNORECASE)
                if match:
                    summary['intrinsic_value'] = float(match.group(1))
                    break
            
            # Current price
            price_patterns = [
                r'CURRENT PRICE[:\s]+\*?\*?\$(\d+(?:\.\d+)?)\*?\*?',
                r'\*\*Current Price\*\*[:\s]+\$(\d+(?:\.\d+)?)',
                r'\|\s*Current Price\s*\|\s*\$(\d+(?:\.\d+)?)',
            ]
            for pattern in price_patterns:
                match = re.search(pattern, full_analysis, re.IGNORECASE)
                if match:
                    summary['current_price'] = float(match.group(1))
                    break
                    
        except Exception as e:
            print(f"Warning: Error extracting value summary: {e}")
        
        return summary
