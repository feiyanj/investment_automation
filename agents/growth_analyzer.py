"""
Growth Analyzer Agent (V3.0)
Comprehensive growth analysis with quality scoring and scenario modeling
"""
import re
from typing import Dict, Optional, Tuple
from .base_agent import BaseAgent
from .growth_analyzer_prompts import (
    GROWTH_ANALYZER_SYSTEM_PROMPT,
    GROWTH_ANALYZER_ANALYSIS_PROMPT,
    format_growth_context
)


class GrowthAnalyzer(BaseAgent):
    """
    Growth Analyzer agent for evaluating growth quality, market space, 
    and probabilistic scenario modeling
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.5):
        """
        Initialize Growth Analyzer
        
        Args:
            model_name: Which Gemini model to use
            temperature: Controls creativity (0.5 for balanced growth analysis)
        """
        super().__init__(
            name="Growth Analyzer",
            role="Professional Growth Investment Analyst",
            system_prompt=GROWTH_ANALYZER_SYSTEM_PROMPT,
            model_name=model_name,
            temperature=temperature
        )
    
    def analyze(
        self,
        data: Dict,
        info: Dict,
        business_context: str,
        key_events: str
    ) -> str:
        """
        Conduct comprehensive growth analysis
        
        Args:
            data: Complete financial data from DataFetcherV3
            info: Company information
            business_context: Business understanding from BusinessAnalyst
            key_events: Key events from BusinessAnalyst
            
        Returns:
            Comprehensive growth analysis report (3000-5000 words)
        """
        # Add key events to data for context formatting
        data_with_events = data.copy()
        data_with_events['key_events'] = key_events
        
        # Format comprehensive context
        context = format_growth_context(data_with_events, business_context, info)
        
        # Combine prompt with context
        full_prompt = f"{GROWTH_ANALYZER_ANALYSIS_PROMPT}\n\n{context}"
        
        # Generate analysis based on provider
        if self.provider == "deepseek":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
                max_tokens=16384
            )
            return response.choices[0].message.content
        else:
            # Gemini API
            response = self.model.generate_content(full_prompt)
            return response.text
    
    def get_growth_summary(self, full_analysis: str) -> Dict[str, any]:
        """
        Extract key metrics from growth analysis
        Supports both plain text and markdown table formats
        
        Args:
            full_analysis: Complete growth analysis text
            
        Returns:
            Dictionary with extracted metrics
        """
        summary = {
            'historical_quality_score': None,
            'market_space_score': None,
            'sustainability_score': None,
            'recommendation': None,
            'conviction': None,
            'position_size': None,
            'expected_return_5y': None,
            'bull_return': None,
            'base_return': None,
            'bear_return': None
        }
        
        # Parse line by line for better extraction
        lines = full_analysis.split('\n')
        
        for line in lines:
            line_upper = line.upper()
            
            # Extract Historical Growth Quality Score (multiple formats)
            if not summary['historical_quality_score']:
                # Format 1: "HISTORICAL GROWTH QUALITY (7/10)" in header
                if 'HISTORICAL GROWTH QUALITY' in line_upper and '/' in line:
                    match = re.search(r'(\d+)/10', line)
                    if match:
                        summary['historical_quality_score'] = int(match.group(1))
                # Format 2: Table row "| Historical Growth Quality | 7/10 |"
                elif '|' in line and 'HISTORICAL' in line_upper and 'GROWTH' in line_upper:
                    match = re.search(r'(\d+)/10', line)
                    if match:
                        summary['historical_quality_score'] = int(match.group(1))
                # Format 3: Plain text "TOTAL HISTORICAL GROWTH QUALITY SCORE: 7/10"
                elif 'TOTAL HISTORICAL GROWTH QUALITY SCORE:' in line_upper:
                    match = re.search(r'(\d+)/10', line)
                    if match:
                        summary['historical_quality_score'] = int(match.group(1))
            
            # Extract Market Space Score
            if not summary['market_space_score']:
                if 'MARKET SPACE SCORE' in line_upper or ('MARKET SPACE' in line_upper and '/' in line):
                    match = re.search(r'(\d+)/10', line)
                    if match:
                        summary['market_space_score'] = int(match.group(1))
            
            # Extract Sustainability Score
            if not summary['sustainability_score']:
                if 'GROWTH SUSTAINABILITY' in line_upper or 'SUSTAINABILITY SCORE' in line_upper:
                    match = re.search(r'(\d+)/10', line)
                    if match:
                        summary['sustainability_score'] = int(match.group(1))
            
            # Extract Recommendation (table or plain text)
            if not summary['recommendation']:
                # Table format: "| Recommendation | HOLD | Conviction: 6/10 |"
                if '|' in line and 'RECOMMENDATION' in line_upper:
                    if 'STRONG GROWTH BUY' in line_upper or 'STRONG BUY' in line_upper:
                        summary['recommendation'] = 'STRONG GROWTH BUY'
                    elif 'GROWTH BUY' in line_upper or 'BUY' in line_upper:
                        summary['recommendation'] = 'GROWTH BUY'
                    elif 'CAUTION' in line_upper:
                        summary['recommendation'] = 'CAUTION'
                    elif 'AVOID' in line_upper:
                        summary['recommendation'] = 'AVOID'
                    elif 'HOLD' in line_upper:
                        summary['recommendation'] = 'HOLD'
                # Plain text or emoji format
                elif '🟢 STRONG GROWTH BUY' in line or 'STRONG GROWTH BUY' in line_upper:
                    summary['recommendation'] = 'STRONG GROWTH BUY'
                elif '🟢 GROWTH BUY' in line or 'GROWTH BUY' in line_upper:
                    summary['recommendation'] = 'GROWTH BUY'
                elif '🟡 HOLD' in line or 'HOLD/SELECTIVE BUY' in line_upper:
                    summary['recommendation'] = 'HOLD'
                elif '🟠 CAUTION' in line or 'CAUTION' in line_upper:
                    summary['recommendation'] = 'CAUTION'
                elif '🔴 AVOID' in line or 'AVOID' in line_upper:
                    summary['recommendation'] = 'AVOID'
            
            # Extract Conviction Level (from table or plain text)
            if not summary['conviction']:
                # From table row with recommendation: "| HOLD | Conviction: 6/10 |"
                if 'CONVICTION' in line_upper:
                    match = re.search(r'CONVICTION[:\s]+(\d+)/10', line, re.IGNORECASE)
                    if match:
                        summary['conviction'] = int(match.group(1))
            
            # Extract Position Size
            if not summary['position_size']:
                # Table: "| Position Size | 5-7% |" or "| 5-7% | Portfolio Weight |"
                if ('POSITION SIZE' in line_upper or 'PORTFOLIO WEIGHT' in line_upper) and '%' in line:
                    match = re.search(r'(\d+(?:\.\d+)?)-?(?:\d+(?:\.\d+)?)?%', line)
                    if match:
                        summary['position_size'] = float(match.group(1))
                # Plain text: "Your Recommendation: 5%"
                elif 'YOUR RECOMMENDATION:' in line_upper and '%' in line:
                    match = re.search(r'(\d+(?:\.\d+)?)%', line)
                    if match:
                        summary['position_size'] = float(match.group(1))
            
            # Extract Expected 5-Year Return
            if not summary['expected_return_5y']:
                if ('EXPECTED' in line_upper and '5' in line and 'RETURN' in line_upper) or ('5Y RETURN' in line_upper):
                    match = re.search(r'([+-]?\d+(?:\.\d+)?)%', line)
                    if match:
                        summary['expected_return_5y'] = float(match.group(1))
            
            # Extract Bull/Base/Bear returns (table or plain text)
            if not summary['bull_return']:
                if 'BULL' in line_upper and ('CASE' in line_upper or 'RETURN' in line_upper):
                    match = re.search(r'([+-]?\d+(?:\.\d+)?)%', line)
                    if match:
                        summary['bull_return'] = float(match.group(1))
            
            if not summary['base_return']:
                if 'BASE' in line_upper and ('CASE' in line_upper or 'RETURN' in line_upper):
                    match = re.search(r'([+-]?\d+(?:\.\d+)?)%', line)
                    if match:
                        summary['base_return'] = float(match.group(1))
            
            if not summary['bear_return']:
                if 'BEAR' in line_upper and ('CASE' in line_upper or 'RETURN' in line_upper):
                    match = re.search(r'([+-]?\d+(?:\.\d+)?)%', line)
                    if match:
                        summary['bear_return'] = float(match.group(1))
        
        # Fallback to multi-line regex patterns for plain text format
        if not summary['bull_return']:
            bull_match = re.search(
                r'Bull Case.*?Total Return:\s*\+?(\d+(?:\.\d+)?)%',
                full_analysis,
                re.IGNORECASE | re.DOTALL
            )
            if bull_match:
                summary['bull_return'] = float(bull_match.group(1))
        
        if not summary['base_return']:
            base_match = re.search(
                r'Base Case.*?Total Return:\s*\+?(\d+(?:\.\d+)?)%',
                full_analysis,
                re.IGNORECASE | re.DOTALL
            )
            if base_match:
                summary['base_return'] = float(base_match.group(1))
        
        if not summary['bear_return']:
            bear_match = re.search(
                r'Bear Case.*?Total Return:\s*([+-]?\d+(?:\.\d+)?)%',
                full_analysis,
                re.IGNORECASE | re.DOTALL
            )
            if bear_match:
                summary['bear_return'] = float(bear_match.group(1))
        
        return summary
    
    def calculate_scenario_probabilities(
        self,
        data: Dict,
        info: Dict,
        quality_score: int,
        sustainability_score: int
    ) -> Dict[str, float]:
        """
        Calculate probabilistic weights for scenarios based on quality/sustainability
        
        Higher quality/sustainability → Higher base case probability
        Lower quality/sustainability → Higher bear case probability
        
        Args:
            data: Financial data
            info: Company info
            quality_score: Historical growth quality (0-10)
            sustainability_score: Growth sustainability (0-10)
            
        Returns:
            Dictionary with bull/base/bear probabilities
        """
        # Default: Bull 30%, Base 50%, Bear 20%
        
        # Adjust based on combined score
        avg_score = (quality_score + sustainability_score) / 2
        
        if avg_score >= 8:
            # High quality: Bull 35%, Base 55%, Bear 10%
            return {'bull': 0.35, 'base': 0.55, 'bear': 0.10}
        elif avg_score >= 6:
            # Good quality: Bull 30%, Base 55%, Bear 15%
            return {'bull': 0.30, 'base': 0.55, 'bear': 0.15}
        elif avg_score >= 4:
            # Moderate: Bull 25%, Base 50%, Bear 25%
            return {'bull': 0.25, 'base': 0.50, 'bear': 0.25}
        else:
            # Weak: Bull 20%, Base 45%, Bear 35%
            return {'bull': 0.20, 'base': 0.45, 'bear': 0.35}
