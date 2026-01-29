"""
DCF Calculator Module
2-Stage Discounted Cash Flow valuation model
"""
import numpy as np
from typing import Dict, Optional


class ValuationEngine:
    """
    Mathematical valuation calculator using 2-Stage DCF Model
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker
    
    def calculate_dynamic_growth_rate(
        self,
        historical_revenue_cagr: float,
        historical_earnings_cagr: float,
        historical_fcf_cagr: float,
        market_cap: float,
        company_stage: str = 'mature'
    ) -> Dict[str, float]:
        """
        Calculate dynamic growth rate based on multiple factors
        
        Args:
            historical_revenue_cagr: 5-year revenue CAGR (as decimal, e.g., 0.15 for 15%)
            historical_earnings_cagr: 5-year earnings CAGR
            historical_fcf_cagr: 5-year FCF CAGR
            market_cap: Current market cap in dollars
            company_stage: 'startup', 'growth', 'mature', or 'declining'
            
        Returns:
            Dictionary with growth rate and reasoning
        """
        # Start with historical average (weighted towards FCF as most conservative)
        historical_avg = (
            historical_revenue_cagr * 0.3 +
            historical_earnings_cagr * 0.3 +
            historical_fcf_cagr * 0.4
        )
        
        # Apply stage adjustment
        stage_multipliers = {
            'startup': 1.2,      # Can sustain higher growth
            'growth': 1.0,       # Historical is good proxy
            'mature': 0.8,       # Growth typically slows
            'declining': 0.5     # Significant slowdown
        }
        stage_adjusted = historical_avg * stage_multipliers.get(company_stage, 1.0)
        
        # Apply size constraint (law of large numbers)
        market_cap_b = market_cap / 1e9  # Convert to billions
        
        if market_cap_b > 500:
            size_cap = 0.10  # Very hard to grow >10% when you're huge
        elif market_cap_b > 200:
            size_cap = 0.12
        elif market_cap_b > 50:
            size_cap = 0.15
        elif market_cap_b > 10:
            size_cap = 0.20
        else:
            size_cap = 0.30  # Smaller companies can grow faster
        
        # Take the minimum of stage-adjusted and size cap
        final_growth = min(stage_adjusted, size_cap)
        
        # Floor at 0%, cap at 30%
        final_growth = max(0.0, min(final_growth, 0.30))
        
        return {
            'growth_rate': final_growth,
            'historical_avg': historical_avg,
            'stage_adjusted': stage_adjusted,
            'size_cap': size_cap,
            'reasoning': f"Historical avg: {historical_avg:.1%}, "
                        f"Stage ({company_stage}): {stage_adjusted:.1%}, "
                        f"Size constraint (${market_cap_b:.1f}B): {size_cap:.1%}, "
                        f"Final: {final_growth:.1%}"
        }
    
    def calculate_dynamic_wacc(
        self,
        risk_free_rate: float = 0.045,  # 10-year Treasury, update as needed
        beta: float = 1.0,
        market_cap: float = 100e9,
        debt_to_equity: float = 0.5,
        equity_risk_premium: float = 0.065
    ) -> Dict[str, float]:
        """
        Calculate dynamic WACC based on company characteristics
        
        Args:
            risk_free_rate: Current 10-year Treasury yield (as decimal)
            beta: Company beta (volatility vs market)
            market_cap: Market capitalization in dollars
            debt_to_equity: Debt/Equity ratio
            equity_risk_premium: Expected market return over risk-free (typically 6-7%)
            
        Returns:
            Dictionary with WACC and breakdown
        """
        # Size premium based on market cap
        market_cap_b = market_cap / 1e9
        
        if market_cap_b < 2:
            size_premium = 0.035  # Micro-cap: +3.5%
        elif market_cap_b < 10:
            size_premium = 0.025  # Small-cap: +2.5%
        elif market_cap_b < 50:
            size_premium = 0.015  # Mid-cap: +1.5%
        elif market_cap_b < 200:
            size_premium = 0.008  # Large-cap: +0.8%
        else:
            size_premium = 0.0    # Mega-cap: 0%
        
        # Financial risk premium based on leverage
        if debt_to_equity > 2.0:
            risk_premium = 0.025  # High debt: +2.5%
        elif debt_to_equity > 1.0:
            risk_premium = 0.015  # Moderate debt: +1.5%
        elif debt_to_equity > 0.5:
            risk_premium = 0.008  # Low debt: +0.8%
        else:
            risk_premium = 0.0    # Very low debt: 0%
        
        # Cost of Equity using CAPM with adjustments
        cost_of_equity = (
            risk_free_rate +
            (beta * equity_risk_premium) +
            size_premium +
            risk_premium
        )
        
        # For simplicity, assume all equity financing
        # (In practice, you'd calculate weighted average with cost of debt)
        wacc = cost_of_equity
        
        return {
            'wacc': wacc,
            'cost_of_equity': cost_of_equity,
            'risk_free_rate': risk_free_rate,
            'beta': beta,
            'equity_risk_premium': equity_risk_premium,
            'size_premium': size_premium,
            'risk_premium': risk_premium,
            'breakdown': f"WACC = {risk_free_rate:.1%} (RF) + "
                        f"{beta:.2f} × {equity_risk_premium:.1%} (ERP) + "
                        f"{size_premium:.1%} (Size) + {risk_premium:.1%} (Risk) = {wacc:.1%}"
        }
    
    def calculate_pe_valuation(
        self,
        trailing_eps: float,
        forward_eps: float,
        historical_pe_5y: float,
        quality_score: int,
        growth_rate: float
    ) -> Dict[str, float]:
        """
        Calculate intrinsic value using P/E multiple approach
        
        Args:
            trailing_eps: Trailing 12-month EPS
            forward_eps: Forward 12-month EPS estimate
            historical_pe_5y: Average P/E ratio over 5 years
            quality_score: Financial quality score (0-10)
            growth_rate: Expected growth rate (as decimal)
            
        Returns:
            Dictionary with valuation and justified P/E
        """
        # Determine justified P/E based on growth and quality
        growth_pct = growth_rate * 100
        
        # Base P/E from growth
        if growth_pct > 15:
            base_pe = 28
        elif growth_pct > 10:
            base_pe = 20
        elif growth_pct > 5:
            base_pe = 15
        else:
            base_pe = 12
        
        # Quality adjustment
        if quality_score >= 8:
            quality_multiplier = 1.0
        elif quality_score >= 6:
            quality_multiplier = 0.85
        elif quality_score >= 4:
            quality_multiplier = 0.70
        else:
            quality_multiplier = 0.55
        
        justified_pe = base_pe * quality_multiplier
        
        # Use forward EPS if available, otherwise trailing
        eps_to_use = forward_eps if forward_eps > 0 else trailing_eps
        
        intrinsic_value = justified_pe * eps_to_use
        
        return {
            'intrinsic_value_per_share': intrinsic_value,
            'justified_pe': justified_pe,
            'eps_used': eps_to_use,
            'historical_pe': historical_pe_5y,
            'reasoning': f"Growth {growth_pct:.1f}% + Quality {quality_score}/10 "
                        f"→ Justified P/E {justified_pe:.1f}x × EPS ${eps_to_use:.2f}"
        }
    
    def calculate_pfcf_valuation(
        self,
        fcf_per_share: float,
        historical_pfcf_5y: float,
        quality_score: int,
        growth_rate: float
    ) -> Dict[str, float]:
        """
        Calculate intrinsic value using P/FCF multiple approach
        
        Args:
            fcf_per_share: Free cash flow per share (TTM)
            historical_pfcf_5y: Average P/FCF ratio over 5 years
            quality_score: Financial quality score (0-10)
            growth_rate: Expected growth rate (as decimal)
            
        Returns:
            Dictionary with valuation and justified P/FCF
        """
        growth_pct = growth_rate * 100
        
        # Base P/FCF from growth
        if growth_pct > 15:
            base_pfcf = 30
        elif growth_pct > 10:
            base_pfcf = 22
        elif growth_pct > 5:
            base_pfcf = 16
        else:
            base_pfcf = 12
        
        # Quality adjustment (same as P/E)
        if quality_score >= 8:
            quality_multiplier = 1.0
        elif quality_score >= 6:
            quality_multiplier = 0.85
        elif quality_score >= 4:
            quality_multiplier = 0.70
        else:
            quality_multiplier = 0.55
        
        justified_pfcf = base_pfcf * quality_multiplier
        
        intrinsic_value = justified_pfcf * fcf_per_share
        
        return {
            'intrinsic_value_per_share': intrinsic_value,
            'justified_pfcf': justified_pfcf,
            'fcf_per_share': fcf_per_share,
            'historical_pfcf': historical_pfcf_5y,
            'reasoning': f"Growth {growth_pct:.1f}% + Quality {quality_score}/10 "
                        f"→ Justified P/FCF {justified_pfcf:.1f}x × FCF ${fcf_per_share:.2f}"
        }
        
    def calculate_dcf(
        self,
        fcf: float,
        growth_rate: float,
        discount_rate: float = 0.10,
        terminal_growth_rate: float = 0.03,
        high_growth_years: int = 5,
        shares_outstanding: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate intrinsic value using 2-Stage DCF
        
        Stage 1: High growth period (Years 1-5)
        Stage 2: Perpetual growth (Terminal value)
        
        Args:
            fcf: Current Free Cash Flow
            growth_rate: Annual growth rate (Stage 1)
            discount_rate: Required rate of return (WACC)
            terminal_growth_rate: Perpetual growth rate
            high_growth_years: Years of high growth
            shares_outstanding: Number of shares
            
        Returns:
            Dictionary with valuation results
        """
        # Validation
        if fcf <= 0:
            return {
                'error': 'FCF must be positive for DCF calculation',
                'intrinsic_value_per_share': 0,
                'total_present_value': 0,
                'terminal_value': 0
            }
        
        if growth_rate <= 0 or growth_rate > 1.0:
            print(f"⚠️  Warning: Growth rate {growth_rate:.1%} unrealistic. Using 10%.")
            growth_rate = 0.10
        
        if discount_rate <= terminal_growth_rate:
            print(f"⚠️  Warning: Adjusting discount rate...")
            discount_rate = terminal_growth_rate + 0.05
        
        # Stage 1: High Growth Period
        projected_fcf = []
        present_value_fcf = []
        
        for year in range(1, high_growth_years + 1):
            fcf_year = fcf * ((1 + growth_rate) ** year)
            projected_fcf.append(fcf_year)
            
            pv = fcf_year / ((1 + discount_rate) ** year)
            present_value_fcf.append(pv)
        
        stage1_value = sum(present_value_fcf)
        
        # Stage 2: Terminal Value
        fcf_terminal = fcf * ((1 + growth_rate) ** (high_growth_years + 1))
        terminal_value = fcf_terminal / (discount_rate - terminal_growth_rate)
        pv_terminal = terminal_value / ((1 + discount_rate) ** high_growth_years)
        
        # Total Enterprise Value
        total_pv = stage1_value + pv_terminal
        
        # Per-share value
        intrinsic_value_per_share = None
        if shares_outstanding and shares_outstanding > 0:
            intrinsic_value_per_share = total_pv / shares_outstanding
        
        return {
            'intrinsic_value_per_share': intrinsic_value_per_share,
            'total_present_value': total_pv,
            'stage1_value': stage1_value,
            'terminal_value': pv_terminal,
            'terminal_value_undiscounted': terminal_value,
            'projected_fcf': projected_fcf,
            'discount_rate': discount_rate,
            'growth_rate': growth_rate,
            'terminal_growth_rate': terminal_growth_rate,
            'assumptions': {
                'current_fcf': fcf,
                'high_growth_years': high_growth_years,
                'discount_rate_%': discount_rate * 100,
                'growth_rate_%': growth_rate * 100,
                'terminal_growth_%': terminal_growth_rate * 100
            }
        }
    
    def calculate_margin_of_safety(
        self,
        intrinsic_value: float,
        current_price: float
    ) -> Dict[str, float]:
        """
        Calculate Margin of Safety
        
        MOS = (Intrinsic Value - Current Price) / Intrinsic Value
        
        Args:
            intrinsic_value: Calculated fair value
            current_price: Current market price
            
        Returns:
            Dictionary with MOS analysis
        """
        if intrinsic_value <= 0:
            return {
                'margin_of_safety_%': None,
                'recommendation': 'Cannot calculate - invalid intrinsic value'
            }
        
        mos = ((intrinsic_value - current_price) / intrinsic_value) * 100
        
        # Assessment
        if mos > 25:
            assessment = "🟢 STRONG BUY - Significant undervaluation"
        elif mos > 10:
            assessment = "🟡 BUY - Moderate undervaluation"
        elif mos > -10:
            assessment = "⚪ FAIR - Roughly fairly valued"
        elif mos > -25:
            assessment = "🟠 CAUTION - Moderately overvalued"
        else:
            assessment = "🔴 AVOID - Significantly overvalued"
        
        return {
            'margin_of_safety_%': mos,
            'intrinsic_value': intrinsic_value,
            'current_price': current_price,
            'upside_downside_%': mos,
            'assessment': assessment,
            'price_to_value_ratio': current_price / intrinsic_value if intrinsic_value else None
        }
    
    def format_dcf_report(
        self,
        dcf_result: Dict,
        current_price: Optional[float] = None
    ) -> str:
        """
        Format DCF results for LLM consumption
        
        Args:
            dcf_result: DCF calculation results
            current_price: Current stock price
            
        Returns:
            Formatted report string
        """
        if 'error' in dcf_result:
            return f"""
DCF VALUATION - ERROR
---------------------
⚠️  {dcf_result['error']}

DCF calculation could not be completed.
"""
        
        report = f"""
================================================================================
DISCOUNTED CASH FLOW (DCF) VALUATION
================================================================================

📊 INTRINSIC VALUE CALCULATION:

Total Enterprise Value: ${dcf_result['total_present_value']:,.0f}
"""
        
        if dcf_result['intrinsic_value_per_share']:
            report += f"Intrinsic Value Per Share: ${dcf_result['intrinsic_value_per_share']:.2f}\n"
        
        report += f"""
BREAKDOWN:
- Stage 1 Value (High Growth): ${dcf_result['stage1_value']:,.0f}
- Stage 2 Value (Terminal): ${dcf_result['terminal_value']:,.0f}

ASSUMPTIONS USED:
- Current FCF: ${dcf_result['assumptions']['current_fcf']:,.0f}
- High Growth Period: {dcf_result['assumptions']['high_growth_years']} years
- Growth Rate (Stage 1): {dcf_result['assumptions']['growth_rate_%']:.1f}%
- Discount Rate (WACC): {dcf_result['assumptions']['discount_rate_%']:.1f}%
- Terminal Growth Rate: {dcf_result['assumptions']['terminal_growth_%']:.1f}%
"""
        
        if current_price and dcf_result['intrinsic_value_per_share']:
            mos_result = self.calculate_margin_of_safety(
                dcf_result['intrinsic_value_per_share'],
                current_price
            )
            
            report += f"""
================================================================================
MARGIN OF SAFETY ANALYSIS
================================================================================

Current Market Price: ${current_price:.2f}
DCF Intrinsic Value: ${dcf_result['intrinsic_value_per_share']:.2f}

Margin of Safety: {mos_result['margin_of_safety_%']:.1f}%
Price/Value Ratio: {mos_result['price_to_value_ratio']:.2f}x

{mos_result['assessment']}

Interpretation:
- If MOS > 25%: Strong Buy Signal (significant undervaluation)
- If MOS 10-25%: Buy Signal (moderate undervaluation)
- If MOS -10 to +10%: Fairly Valued
- If MOS < -25%: Avoid (significantly overvalued)

Current Assessment: {"UNDERVALUED ✓" if mos_result['margin_of_safety_%'] > 0 else "OVERVALUED ✗"}
Potential Upside/Downside: {mos_result['margin_of_safety_%']:+.1f}%
"""
        
        report += """
================================================================================
IMPORTANT NOTES FOR ANALYSIS:
- DCF is sensitive to growth rate assumptions - test different scenarios
- Market may disagree with DCF due to different risk assessments
- Use DCF as ONE input alongside qualitative factors
- Skeptics should question growth and discount rate assumptions
================================================================================
"""
        
        return report.strip()
