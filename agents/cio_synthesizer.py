"""
CIO (Chief Investment Officer) Synthesizer Agent (V3.0)
Final investment decision integrating Value, Growth, and Risk perspectives
"""
import re
from typing import Dict, Optional
from .base_agent import BaseAgent
from .cio_prompts import (
    CIO_SYSTEM_PROMPT,
    CIO_SYNTHESIS_PROMPT,
    format_cio_context
)


class CIOSynthesizer(BaseAgent):
    """
    CIO Synthesizer agent for making final investment decisions
    by integrating Value Hunter, Growth Analyzer, and Risk Examiner perspectives
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.4):
        """
        Initialize CIO Synthesizer
        
        Args:
            model_name: Which Gemini model to use
            temperature: Controls creativity (0.4 for balanced but decisive synthesis)
        """
        super().__init__(
            name="CIO Synthesizer",
            role="Chief Investment Officer",
            system_prompt=CIO_SYSTEM_PROMPT,
            model_name=model_name,
            temperature=temperature
        )
    
    def synthesize(
        self,
        data: Dict,
        info: Dict,
        business_analysis: str,
        value_analysis: str,
        growth_analysis: str,
        risk_analysis: str,
        value_summary: Dict,
        growth_summary: Dict,
        risk_summary: Dict
    ) -> str:
        """
        Synthesize all analyses into final investment decision
        
        Args:
            data: Complete financial data from DataFetcherV3
            info: Company information
            business_analysis: Business understanding from BusinessAnalyst
            value_analysis: Full Value Hunter analysis
            growth_analysis: Full Growth Analyzer analysis
            risk_analysis: Full Risk Examiner analysis
            value_summary: Extracted metrics from Value Hunter
            growth_summary: Extracted metrics from Growth Analyzer
            risk_summary: Extracted metrics from Risk Examiner
            
        Returns:
            Comprehensive CIO synthesis report (3500-5000 words)
        """
        # Format comprehensive context
        context = format_cio_context(
            data, info, business_analysis,
            value_analysis, growth_analysis, risk_analysis,
            value_summary, growth_summary, risk_summary
        )
        
        # Combine prompt with context
        full_prompt = f"{CIO_SYNTHESIS_PROMPT}\n\n{context}"
        
        # Generate synthesis based on provider
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
    
    def get_decision_summary(self, full_synthesis: str) -> Dict[str, any]:
        """
        Extract key decision metrics from CIO synthesis
        
        Args:
            full_synthesis: Complete CIO synthesis text
            
        Returns:
            Dictionary with extracted decision metrics (with safe defaults)
        """
        summary = {
            'recommendation': 'N/A',
            'conviction': 0,
            'position_size': 0.0,
            'composite_score': 0.0,
            'cio_fair_value': 0.0,
            'upside_to_fair_value': 0.0,
            'expected_return_3y': 0.0,
            'bull_return': 0.0,
            'base_return': 0.0,
            'bear_return': 0.0,
            'bull_probability': 0,
            'base_probability': 0,
            'bear_probability': 0,
            'upside_downside_ratio': 0.0,
            'entry_price_low': 0.0,
            'entry_price_high': 0.0,
            'stop_loss': 0.0,
            'target_price': 0.0
        }
        
        # Extract EXECUTIVE SUMMARY section for more accurate parsing
        exec_summary = ''
        summary_match = re.search(
            r'EXECUTIVE SUMMARY.*?(?=##\s+SECTION\s+2|$)',
            full_synthesis,
            re.IGNORECASE | re.DOTALL
        )
        if summary_match:
            exec_summary = summary_match.group(0)
        
        try:
            # Extract Final Recommendation (prioritize EXECUTIVE SUMMARY)
            # Check table format first: "| Final Recommendation | HOLD |"
            rec_match = re.search(
                r'\|[^|]*Final\s+Recommendation[^|]*\|[^|]*(STRONG BUY|BUY|HOLD|REDUCE|SELL|STRONG GROWTH BUY|GROWTH BUY)[^|]*\|',
                exec_summary or full_synthesis,
                re.IGNORECASE
            )
            if rec_match:
                summary['recommendation'] = rec_match.group(1).upper()
            else:
                # Plain text format (handles emoji + markdown bold)
                rec_match = re.search(
                    r'\*?\*?Final Recommendation\*?\*?:\s*(🟢|🟡|🟠|🔴)?\s*\*?\*?(STRONG BUY|BUY|HOLD|REDUCE|SELL)\*?\*?',
                    exec_summary or full_synthesis,
                    re.IGNORECASE
                )
                if rec_match:
                    summary['recommendation'] = rec_match.group(2).upper()
                else:
                    # Fallback: Check for "Rating:" line in SECTION 5
                    rating_match = re.search(
                        r'\*?\*?Rating\*?\*?:\s*(🟢|🟡|🟠|🔴)?\s*\*?\*?(STRONG BUY|BUY|HOLD|REDUCE|SELL)\*?\*?',
                        full_synthesis,
                        re.IGNORECASE
                    )
                    if rating_match:
                        summary['recommendation'] = rating_match.group(2).upper()
                    # Final fallback to emoji detection
                    elif '🟢' in exec_summary and 'STRONG BUY' in exec_summary.upper():
                        summary['recommendation'] = 'STRONG BUY'
                    elif '🟢' in exec_summary and 'BUY' in exec_summary.upper():
                        summary['recommendation'] = 'BUY'
                    elif '🟡' in exec_summary and 'HOLD' in exec_summary.upper():
                        summary['recommendation'] = 'HOLD'
                    elif '🟠' in exec_summary and 'REDUCE' in exec_summary.upper():
                        summary['recommendation'] = 'REDUCE'
                    elif '🔴' in exec_summary and 'SELL' in exec_summary.upper():
                        summary['recommendation'] = 'SELL'
        except:
            pass
        
        # Extract Conviction Level (from EXECUTIVE SUMMARY)
        try:
            # Multiple format support - priority order
            patterns = [
                r'\|\s*Conviction\s*(?:Level)?\s*\|\s*(\d+)/10\s*\|',  # Table: | Conviction Level | 6/10 |
                r'\*\*Conviction(?:\s+Level)?\*\*\s*:\s*(\d+)/10',  # **Conviction Level**: 6/10
                r'Conviction(?:\s+Level)?\s*:\s*\*?\*?(\d+)/10\*?\*?',  # Conviction Level: 6/10 or **6/10**
                r'Conviction\s*:\s*(\d+)/10',  # Conviction: 6/10 (simple)
            ]
            for pattern in patterns:
                conviction_match = re.search(pattern, exec_summary or full_synthesis, re.IGNORECASE)
                if conviction_match:
                    summary['conviction'] = int(conviction_match.group(1))
                    break
        except Exception as e:
            print(f"Debug: Conviction extraction error: {e}")
        
        try:
            # Extract Position Size (from EXECUTIVE SUMMARY)
            # Table format: "| Position Size | 5-7% |"
            position_match = re.search(
                r'\|[^|]*Position\s+Size[^|]*\|[^|]*(\d+(?:\.\d+)?)[^|]*%',
                exec_summary or full_synthesis,
                re.IGNORECASE
            )
            if not position_match:
                # Plain text format
                position_match = re.search(
                    r'\*?\*?(?:Recommended Position(?:\s+Size)?|Position Size|FINAL POSITION)\*?\*?:\s*(\d+(?:\.\d+)?)%',
                exec_summary or full_synthesis,
                re.IGNORECASE
            )
            if position_match:
                summary['position_size'] = float(position_match.group(1))
            
            # Extract Expected 3-Year Return (from EXECUTIVE SUMMARY)
            # First try: Probability-weighted format from SECTION 4
            prob_weighted_match = re.search(
                r'\*?\*?Expected (?:3-Year|3Y) Return\*?\*?:\s*\*?\*?\+?(\d+(?:\.\d+)?)%\*?\*?',
                full_synthesis,
                re.IGNORECASE
            )
            if prob_weighted_match:
                summary['expected_return_3y'] = float(prob_weighted_match.group(1))
            else:
                # Table format: "| Expected 3Y Return | 12.8% |"
                expected_match = re.search(
                    r'\|[^|]*Expected\s+(?:3-Year|3Y)\s+Return[^|]*\|[^|]*\+?(\d+(?:\.\d+)?)%',
                    exec_summary or full_synthesis,
                    re.IGNORECASE
                )
                if not expected_match:
                    # Plain text format with range (e.g., "+25% to +40%")
                    expected_match = re.search(
                        r'\*?\*?Expected (?:3-Year|3Y) Return\*?\*?:\s*\+?(\d+(?:\.\d+)?)%?\s*to\s*\+?(\d+(?:\.\d+)?)%',
                        exec_summary or full_synthesis,
                        re.IGNORECASE
                    )
                    if expected_match:
                        # Average of range
                        summary['expected_return_3y'] = (float(expected_match.group(1)) + float(expected_match.group(2))) / 2.0
                else:
                    summary['expected_return_3y'] = float(expected_match.group(1))
            
            # Extract Composite Score
            # First try: "COMPOSITE SCORE: 8.18/10" format
            composite_match = re.search(
                r'\*?\*?COMPOSITE SCORE\*?\*?:\s*\*?\*?(\d+(?:\.\d+)?)/10\*?\*?',
                full_synthesis,
                re.IGNORECASE
            )
            if composite_match:
                # Convert /10 to /100 scale
                summary['composite_score'] = float(composite_match.group(1)) * 10.0
            else:
                # Table format: "| Composite Score | 72/100 |"
                composite_match = re.search(
                    r'\|[^|]*Composite\s+(?:Quality\s+)?Score[^|]*\|[^|]*(\d+(?:\.\d+)?)/100',
                    exec_summary or full_synthesis,
                    re.IGNORECASE
                )
                if not composite_match:
                    # Plain text /100 format
                    composite_match = re.search(
                        r'Composite\s+(?:Quality\s+)?Score:\s*(\d+(?:\.\d+)?)/100',
                        full_synthesis,
                        re.IGNORECASE
                    )
                if composite_match:
                    summary['composite_score'] = float(composite_match.group(1))
            
            # Extract CIO Fair Value
            # Table format: "| CIO Fair Value | $225.50 |"
            fair_value_match = re.search(
                r'\|[^|]*CIO\s+Fair\s+Value[^|]*\|[^|]*\$(\d+(?:\.\d+)?)',
                exec_summary or full_synthesis,
                re.IGNORECASE
            )
            if not fair_value_match:
                # Plain text format
                fair_value_match = re.search(
                    r'CIO Fair Value:\s*\$(\d+(?:\.\d+)?)',
                    full_synthesis,
                    re.IGNORECASE
                )
            if fair_value_match:
                summary['cio_fair_value'] = float(fair_value_match.group(1))
            
            # Extract Upside to Fair Value
            # Table format: "| Upside to Fair Value | 15.2% |"
            upside_match = re.search(
                r'\|[^|]*Upside\s+to\s+Fair\s+Value[^|]*\|[^|]*(-?\d+(?:\.\d+)?)%',
                exec_summary or full_synthesis,
                re.IGNORECASE
            )
            if not upside_match:
                # Plain text format
                upside_match = re.search(
                    r'Upside to Fair Value:\s*(-?\d+(?:\.\d+)?)%',
                    full_synthesis,
                    re.IGNORECASE
                )
            if upside_match:
                summary['upside_to_fair_value'] = float(upside_match.group(1))
        
        except:
            pass
        
        # Continue with original extraction patterns for remaining metrics
        try:
            # Extract Expected 3-Year Return (fallback if not extracted above)
            if summary['expected_return_3y'] == 0.0:
                expected_match = re.search(
                    r'\*?\*?Expected (?:3-Year|3Y) Return\*?\*?:\s*\+?(\d+(?:\.\d+)?)%?\s*to\s*\+?(\d+(?:\.\d+)?)%',
                    exec_summary or full_synthesis,
                    re.IGNORECASE
                )
                if expected_match:
                    low = float(expected_match.group(1))
                    high = float(expected_match.group(2))
                    summary['expected_return_3y'] = (low + high) / 2
                else:
                    # Try single value
                    expected_single = re.search(
                        r'\*?\*?Expected (?:3-Year|3Y) Return\*?\*?:\s*\+?(\d+(?:\.\d+)?)%',
                        exec_summary or full_synthesis,
                        re.IGNORECASE
                    )
                    if expected_single:
                        summary['expected_return_3y'] = float(expected_single.group(1))
            
            # Extract Composite Score (fallback from SECTION 3: INTEGRATED SCORING)
            if summary['composite_score'] == 0.0:
                composite_match = re.search(
                    r'(?:COMPOSITE SCORE|Weighted Composite|Integrated Score):\s*\*?\*?(\d+(?:\.\d+)?)/10',
                    full_synthesis,
                    re.IGNORECASE
                )
            if not composite_match:
                # Try alternative format: "Composite: X.X"
                composite_match = re.search(
                    r'(?:^|\n)\s*Composite:\s*(\d+(?:\.\d+)?)',
                    full_synthesis,
                    re.IGNORECASE | re.MULTILINE
                )
            if composite_match:
                summary['composite_score'] = float(composite_match.group(1))
            
            # Extract CIO Fair Value (from SECTION 3)
            fair_value_match = re.search(
                r'(?:CIO Fair Value|Fair Value Range|Fair Value Estimate):\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)\s*(?:-|to)\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                full_synthesis,
                re.IGNORECASE
            )
            if fair_value_match:
                # Use midpoint of range, remove commas
                low = float(fair_value_match.group(1).replace(',', ''))
                high = float(fair_value_match.group(2).replace(',', ''))
                summary['cio_fair_value'] = (low + high) / 2
            else:
                # Try single value with possible commas
                fair_value_single = re.search(
                    r'(?:CIO Fair Value|Fair Value):\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                    full_synthesis,
                    re.IGNORECASE
                )
                if fair_value_single:
                    summary['cio_fair_value'] = float(fair_value_single.group(1).replace(',', ''))
                else:
                    # Try "estimate fair value around $X"
                    fair_value_around = re.search(
                        r'fair value\s+(?:around|near|at|of)\s+\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                        full_synthesis,
                        re.IGNORECASE
                    )
                    if fair_value_around:
                        summary['cio_fair_value'] = float(fair_value_around.group(1).replace(',', ''))
            
            # Extract Upside to Fair Value
            upside_match = re.search(
                r'Upside(?:\s+to\s+Fair\s+Value)?:\s*\+?(\d+(?:\.\d+)?)%',
                full_synthesis,
                re.IGNORECASE
            )
            if upside_match:
                summary['upside_to_fair_value'] = float(upside_match.group(1))
            
            # Extract Bull/Base/Bear returns (from SECTION 4: SCENARIO ANALYSIS)
            bull_match = re.search(
                r'Bull Case.*?(?:Total Return|Return):\s*\+?(\d+(?:\.\d+)?)%',
                full_synthesis,
                re.IGNORECASE | re.DOTALL
            )
            if bull_match:
                summary['bull_return'] = float(bull_match.group(1))
            
            base_match = re.search(
                r'Base Case.*?(?:Total Return|Return):\s*\+?(\d+(?:\.\d+)?)%',
                full_synthesis,
                re.IGNORECASE | re.DOTALL
            )
            if base_match:
                summary['base_return'] = float(base_match.group(1))
            
            bear_match = re.search(
                r'Bear Case.*?(?:Total Return|Return):\s*([+-]?\d+(?:\.\d+)?)%',
                full_synthesis,
                re.IGNORECASE | re.DOTALL
            )
            if bear_match:
                summary['bear_return'] = float(bear_match.group(1))            # Extract Probabilities
            bull_prob_match = re.search(
                r'Bull Case \((\d+)%',
                full_synthesis,
                re.IGNORECASE
            )
            if bull_prob_match:
                summary['bull_probability'] = int(bull_prob_match.group(1))
            
            base_prob_match = re.search(
                r'Base Case \((\d+)%',
                full_synthesis,
                re.IGNORECASE
            )
            if base_prob_match:
                summary['base_probability'] = int(base_prob_match.group(1))
            
            bear_prob_match = re.search(
                r'Bear Case \((\d+)%',
                full_synthesis,
                re.IGNORECASE
            )
            if bear_prob_match:
                summary['bear_probability'] = int(bear_prob_match.group(1))
            
            # Extract Upside/Downside Ratio
            ratio_match = re.search(
                r'Upside/Downside Ratio:\s*(\d+(?:\.\d+)?):1',
                full_synthesis,
                re.IGNORECASE
            )
            if ratio_match:
                summary['upside_downside_ratio'] = float(ratio_match.group(1))
            
            # Extract Entry Price Range (from SECTION 6: EXECUTION PLAN)
            entry_range_match = re.search(
                r'(?:Target )?Entry(?:\s+Price)?\s+(?:Range|Zone):\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)\s*(?:-|to)\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                full_synthesis,
                re.IGNORECASE
            )
            if entry_range_match:
                summary['entry_price_low'] = float(entry_range_match.group(1).replace(',', ''))
                summary['entry_price_high'] = float(entry_range_match.group(2).replace(',', ''))
            else:
                # Try alternative format: "enter between $X and $Y"
                entry_alt = re.search(
                    r'(?:enter|buy)\s+(?:at|between)\s+\$(\d+(?:,\d{3})?(?:\.\d+)?)\s+(?:and|to|or)\s+\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                    full_synthesis,
                    re.IGNORECASE
                )
                if entry_alt:
                    summary['entry_price_low'] = float(entry_alt.group(1).replace(',', ''))
                    summary['entry_price_high'] = float(entry_alt.group(2).replace(',', ''))
                else:
                    # Try "accumulate at $X-$Y"
                    entry_accumulate = re.search(
                        r'accumulate\s+(?:at|near)\s+\$(\d+(?:,\d{3})?(?:\.\d+)?)\s*(?:-|to)\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                        full_synthesis,
                        re.IGNORECASE
                    )
                    if entry_accumulate:
                        summary['entry_price_low'] = float(entry_accumulate.group(1).replace(',', ''))
                        summary['entry_price_high'] = float(entry_accumulate.group(2).replace(',', ''))
            
            # Extract Stop Loss
            stop_match = re.search(
                r'(?:Stop Loss|Stop):\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                full_synthesis,
                re.IGNORECASE
            )
            if stop_match:
                summary['stop_loss'] = float(stop_match.group(1).replace(',', ''))
            else:
                # Try alternative formats
                stop_alt = re.search(
                    r'stop(?:\s+loss)?\s+(?:at|below)\s+\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                    full_synthesis,
                    re.IGNORECASE
                )
                if stop_alt:
                    summary['stop_loss'] = float(stop_alt.group(1).replace(',', ''))
                else:
                    # Try "exit if price falls below $X"
                    stop_exit = re.search(
                        r'exit\s+if\s+(?:price\s+)?falls\s+below\s+\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                        full_synthesis,
                        re.IGNORECASE
                    )
                    if stop_exit:
                        summary['stop_loss'] = float(stop_exit.group(1).replace(',', ''))
            
            # Extract Target Price
            target_match = re.search(
                r'(?:Target Price|Price Target|12-Month Target|Target):\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                full_synthesis,
                re.IGNORECASE
            )
            if target_match:
                summary['target_price'] = float(target_match.group(1).replace(',', ''))
            else:
                # Try range format (use high end)
                target_range = re.search(
                    r'target(?:\s+of)?\s+\$(\d+(?:,\d{3})?(?:\.\d+)?)\s*(?:-|to)\s*\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                    full_synthesis,
                    re.IGNORECASE
                )
                if target_range:
                    summary['target_price'] = float(target_range.group(2).replace(',', ''))  # Use high end
                else:
                    # Try "reach $X"
                    target_reach = re.search(
                        r'reach\s+\$(\d+(?:,\d{3})?(?:\.\d+)?)',
                        full_synthesis,
                        re.IGNORECASE
                    )
                    if target_reach:
                        summary['target_price'] = float(target_reach.group(1).replace(',', ''))
        except Exception as e:
            # Silently handle any extraction errors
            pass
        
        return summary
    
    def calculate_composite_score(
        self,
        value_quality: float,
        growth_quality: float,
        risk_score: float,
        value_weight: float = 0.30,
        growth_weight: float = 0.35,
        risk_weight: float = 0.35
    ) -> float:
        """
        Calculate weighted composite quality score
        
        Args:
            value_quality: Value Hunter quality score (0-10)
            growth_quality: Growth Analyzer quality score (0-10) 
            risk_score: Risk Examiner risk score (0-10, higher = more risk)
            value_weight: Weight for value perspective (default 30%)
            growth_weight: Weight for growth perspective (default 35%)
            risk_weight: Weight for risk perspective (default 35%)
            
        Returns:
            Composite score (0-10)
        """
        # Invert risk score (10-risk) so higher is better
        risk_quality = 10 - risk_score
        
        composite = (
            value_quality * value_weight +
            growth_quality * growth_weight +
            risk_quality * risk_weight
        )
        
        return round(composite, 2)
    
    def calculate_position_size(
        self,
        composite_score: float,
        conviction: int,
        risk_score: float,
        upside_potential: float,
        base_position: float = 5.0
    ) -> float:
        """
        Calculate recommended position size
        
        Args:
            composite_score: Composite quality score (0-10)
            conviction: Conviction level (0-10)
            risk_score: Risk score (0-10, higher = more risk)
            upside_potential: Expected upside percentage
            base_position: Base full position size (default 5%)
            
        Returns:
            Recommended position size (0-8%)
        """
        # Start with base position
        position = base_position
        
        # Conviction multiplier (0.5 to 1.0)
        conviction_mult = conviction / 10.0
        position *= conviction_mult
        
        # Risk adjustment (reduce for high risk)
        risk_adjustment = 1 - (risk_score / 20.0)  # 0.5 to 1.0
        position *= risk_adjustment
        
        # Opportunity adjustment (increase for high upside, cap at 1.2x)
        opportunity_mult = min(upside_potential / 40.0, 1.2)
        position *= opportunity_mult
        
        # Cap at 8% maximum
        position = min(position, 8.0)
        
        # Floor at 0%
        position = max(position, 0.0)
        
        return round(position, 2)
