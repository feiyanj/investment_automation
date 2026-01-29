"""
Risk Examiner Agent (V3.0)
Comprehensive risk analysis with red flags detection and bear case scenarios
"""
import re
from typing import Dict, Optional
from .base_agent import BaseAgent
from .risk_examiner_prompts import (
    RISK_EXAMINER_SYSTEM_PROMPT,
    RISK_EXAMINER_ANALYSIS_PROMPT,
    format_risk_context
)


class RiskExaminer(BaseAgent):
    """
    Risk Examiner agent for identifying financial red flags, business model risks,
    and developing bear case scenarios
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
        """
        Initialize Risk Examiner
        
        Args:
            model_name: Which Gemini model to use (default: gemini-2.5-flash)
            temperature: Controls creativity (0.3 for conservative risk assessment)
        """
        super().__init__(
            name="Risk Examiner",
            role="Professional Risk Assessment Analyst",
            system_prompt=RISK_EXAMINER_SYSTEM_PROMPT,
            model_name=model_name,
            temperature=temperature
        )
    
    def analyze(
        self,
        data: Dict,
        info: Dict,
        business_context: str,
        key_events: str,
        value_analysis: str = None,
        growth_analysis: str = None
    ) -> str:
        """
        Conduct comprehensive risk analysis
        
        Args:
            data: Complete financial data from DataFetcherV3
            info: Company information
            business_context: Business understanding from BusinessAnalyst
            key_events: Key events from BusinessAnalyst
            value_analysis: Optional Value Hunter analysis to challenge
            growth_analysis: Optional Growth Analyzer analysis to challenge
            
        Returns:
            Comprehensive risk analysis report (4000-6000 words)
        """
        # Add key events to data for context formatting
        data_with_events = data.copy()
        data_with_events['key_events'] = key_events
        
        # Format comprehensive context
        context = format_risk_context(
            data_with_events,
            business_context,
            info,
            value_analysis,
            growth_analysis
        )
        
        # Combine prompt with context
        full_prompt = f"{RISK_EXAMINER_ANALYSIS_PROMPT}\n\n{context}"
        
        # Generate analysis based on provider
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
            return response.choices[0].message.content
        else:
            # Gemini API
            response = self.model.generate_content(full_prompt)
            return response.text
    
    def get_risk_summary(self, full_analysis: str) -> Dict[str, any]:
        """
        Extract key metrics from risk analysis
        Supports both plain text and markdown table formats
        
        Args:
            full_analysis: Complete risk analysis text
            
        Returns:
            Dictionary with extracted metrics
        """
        summary = {
            'red_flags_count': None,
            'business_model_risk': None,
            'management_risk': None,
            'valuation_risk': None,
            'overall_risk_score': None,
            'risk_rating': None,
            'max_position_size': None,
            'bear_case_downside': None,
            'upside_downside_ratio': None,
            'recommendation': None
        }
        
        # Parse line by line for better extraction
        lines = full_analysis.split('\n')
        
        for line in lines:
            line_upper = line.upper()
            
            # Extract Red Flags (table or plain text)
            if not summary['red_flags_count']:
                if ('RED FLAGS' in line_upper or 'RED FLAG' in line_upper) and any(c.isdigit() for c in line):
                    match = re.search(r'(\d+)', line)
                    if match and int(match.group(1)) <= 20:  # Reasonable range
                        summary['red_flags_count'] = int(match.group(1))
            
            # Extract Business Model Risk Score
            if not summary['business_model_risk']:
                if 'BUSINESS MODEL RISK' in line_upper and '/50' in line:
                    match = re.search(r'(\d+)/50', line)
                    if match:
                        summary['business_model_risk'] = int(match.group(1))
                elif '|' in line and 'BUSINESS MODEL RISK' in line_upper:
                    match = re.search(r'(\d+)/50', line)
                    if match:
                        summary['business_model_risk'] = int(match.group(1))
            
            # Extract Management Risk
            if not summary['management_risk']:
                if 'MANAGEMENT' in line_upper and ('RISK' in line_upper or 'GOVERNANCE' in line_upper):
                    for risk_level in ['LOW', 'MEDIUM', 'HIGH', 'MODERATE']:
                        if risk_level in line_upper:
                            summary['management_risk'] = risk_level.capitalize()
                            break
            
            # Extract Valuation Risk
            if not summary['valuation_risk']:
                if 'VALUATION RISK' in line_upper:
                    for risk_level in ['LOW', 'MEDIUM', 'HIGH', 'MODERATE']:
                        if risk_level in line_upper:
                            summary['valuation_risk'] = risk_level.capitalize()
                            break
            
            # Extract Overall Risk Score (table or plain text)
            if not summary['overall_risk_score']:
                if 'OVERALL RISK SCORE' in line_upper or ('OVERALL RISK' in line_upper and '/' in line):
                    # Pattern: "65/100" or "6.5/10"
                    match = re.search(r'(\d+(?:\.\d+)?)/(?:100|10)', line)
                    if match:
                        score = float(match.group(1))
                        # Normalize to 0-10 scale
                        if '/100' in line:
                            score = score / 10.0
                        summary['overall_risk_score'] = score
            
            # Extract Risk Rating (table or plain text)
            if not summary['risk_rating']:
                if '|' in line and 'RISK RATING' in line_upper:
                    if 'EXTREME' in line_upper or 'AVOID' in line_upper:
                        summary['risk_rating'] = 'EXTREME RISK / AVOID'
                    elif 'HIGH RISK' in line_upper:
                        summary['risk_rating'] = 'HIGH RISK'
                    elif 'MODERATE' in line_upper or 'MEDIUM' in line_upper:
                        summary['risk_rating'] = 'MODERATE RISK'
                    elif 'LOW RISK' in line_upper:
                        summary['risk_rating'] = 'LOW RISK'
                # Emoji patterns
                elif '🟢 LOW RISK' in line or ('LOW RISK' in line_upper and 'Risk Score 0-4' in line):
                    summary['risk_rating'] = 'LOW RISK'
                elif '🟡 MODERATE RISK' in line or ('MODERATE RISK' in line_upper and 'Risk Score 5-6' in line):
                    summary['risk_rating'] = 'MODERATE RISK'
                elif '🟠 HIGH RISK' in line or ('HIGH RISK' in line_upper and 'Risk Score 7-8' in line):
                    summary['risk_rating'] = 'HIGH RISK'
                elif '🔴 EXTREME RISK' in line or 'EXTREME' in line_upper:
                    summary['risk_rating'] = 'EXTREME RISK / AVOID'
            
            # Extract Max Position Size (table or plain text)
            if not summary['max_position_size']:
                if ('MAX POSITION SIZE' in line_upper or 'POSITION SIZE' in line_upper or 'PORTFOLIO WEIGHT' in line_upper) and '%' in line:
                    match = re.search(r'(\d+(?:\.\d+)?)%', line)
                    if match:
                        summary['max_position_size'] = float(match.group(1))
            
            # Extract Bear Case Downside
            if not summary['bear_case_downside']:
                if 'BEAR CASE' in line_upper or 'DOWNSIDE' in line_upper:
                    match = re.search(r'(-\d+(?:\.\d+)?)%', line)
                    if match:
                        summary['bear_case_downside'] = float(match.group(1))
            
            # Extract Upside/Downside Ratio
            if not summary['upside_downside_ratio']:
                if 'UPSIDE/DOWNSIDE' in line_upper or 'UPSIDE-DOWNSIDE' in line_upper:
                    match = re.search(r'(\d+(?:\.\d+)?):1', line)
                    if match:
                        summary['upside_downside_ratio'] = float(match.group(1))
            
            # Extract Recommendation
            if not summary['recommendation']:
                if '|' in line and 'RECOMMENDATION' in line_upper:
                    if 'REDUCE' in line_upper or 'AVOID' in line_upper:
                        summary['recommendation'] = 'REDUCE'
                    elif 'BUY' in line_upper:
                        summary['recommendation'] = 'BUY'
                    elif 'HOLD' in line_upper:
                        summary['recommendation'] = 'HOLD'
        
        # Fallback to regex patterns for plain text format
        if not summary['red_flags_count']:
            flags_match = re.search(
                r'TOTAL FINANCIAL RED FLAGS:\s*(\d+)',
                full_analysis,
                re.IGNORECASE
            )
            if flags_match:
                summary['red_flags_count'] = int(flags_match.group(1))
        
        if not summary['upside_downside_ratio']:
            ratio_match = re.search(
                r'Upside/Downside Ratio:\s*(\d+(?:\.\d+)?):1',
                full_analysis,
                re.IGNORECASE
            )
            if ratio_match:
                summary['upside_downside_ratio'] = float(ratio_match.group(1))
        
        return summary
    
    def calculate_risk_adjusted_position_size(
        self,
        risk_score: float,
        red_flags_count: int,
        upside_downside_ratio: float = None
    ) -> float:
        """
        Calculate maximum recommended position size based on risk profile
        
        Args:
            risk_score: Overall risk score (0-10)
            red_flags_count: Number of financial red flags
            upside_downside_ratio: Upside/downside ratio (optional)
            
        Returns:
            Maximum position size as percentage (0-8%)
        """
        # Base position size from risk score
        if risk_score <= 4:
            base_size = 8.0  # Low risk
        elif risk_score <= 6:
            base_size = 5.0  # Moderate risk
        elif risk_score <= 8:
            base_size = 2.0  # High risk
        else:
            base_size = 0.0  # Extreme risk - avoid
        
        # Reduce for red flags
        if red_flags_count >= 6:
            base_size *= 0.5  # Cut in half for major red flags
        elif red_flags_count >= 3:
            base_size *= 0.75  # Reduce 25% for significant red flags
        
        # Adjust for upside/downside ratio if provided
        if upside_downside_ratio is not None:
            if upside_downside_ratio < 1.5:
                base_size *= 0.5  # Poor risk/reward
            elif upside_downside_ratio < 2.0:
                base_size *= 0.75  # Marginal risk/reward
            # else: ratio >= 2.0, no adjustment (good risk/reward)
        
        # Ensure within bounds
        return max(0.0, min(8.0, base_size))
