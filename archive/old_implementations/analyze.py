"""
Multi-Agent AI Investment Analysis System - VERSION 2.0 (Refactored)
=====================================================================

Clean, modular architecture for stock analysis using:
- Google Gemini API (gemini-2.5-flash)
- Yahoo Finance data (yfinance)
- Live news (DuckDuckGo Search)
- DCF Valuation (2-Stage Model)
"""
import time
from typing import Dict, Optional

from config import Config
from data import DataFetcher
from valuation import ValuationEngine
from agents import (
    BaseAgent,
    VALUE_HUNTER_PROMPT,
    GROWTH_VISIONARY_PROMPT,
    SKEPTIC_PROMPT,
    CIO_PROMPT
)
from utils import print_separator, print_section, print_error, print_success


def select_model() -> str:
    """
    Interactive model selector
    
    Returns:
        Selected model name
    """
    print("\n" + "="*80)
    print("  SELECT AI MODEL")
    print("="*80 + "\n")
    
    print("Available Gemini models:\n")
    for key, model_info in Config.AVAILABLE_MODELS.items():
        print(f"  [{key}] {model_info['name']}")
        print(f"      {model_info['description']}")
        print(f"      Limits: {model_info['rpm']} RPM / {model_info['rpd']} RPD\n")
    
    while True:
        choice = input(f"Select model (1-{len(Config.AVAILABLE_MODELS)}) or press Enter for default: ").strip()
        
        if not choice:
            model_name = Config.DEFAULT_MODEL
            print(f"✅ Using default: {model_name}")
            return model_name
        
        if choice in Config.AVAILABLE_MODELS:
            model_name = Config.AVAILABLE_MODELS[choice]["name"]
            print(f"✅ Selected: {model_name}")
            return model_name
        else:
            print(f"❌ Invalid choice. Please enter 1-{len(Config.AVAILABLE_MODELS)} or press Enter.")


def create_agents(model_name: str = None) -> Dict[str, BaseAgent]:
    """
    Create all investment analysis agents
    
    Args:
        model_name: Gemini model to use (default from config)
    
    Returns:
        Dictionary of agents by name
    """
    model_name = model_name or Config.DEFAULT_MODEL
    
    agents = {
        'value_hunter': BaseAgent(
            name="Value Hunter",
            role="Warren Buffett Style Analyst",
            system_prompt=VALUE_HUNTER_PROMPT,
            model_name=model_name
        ),
        'growth_visionary': BaseAgent(
            name="Growth Visionary",
            role="Cathie Wood Style Analyst",
            system_prompt=GROWTH_VISIONARY_PROMPT,
            model_name=model_name
        ),
        'skeptic': BaseAgent(
            name="The Skeptic",
            role="Short-Seller & Forensic Analyst",
            system_prompt=SKEPTIC_PROMPT,
            model_name=model_name
        ),
        'cio': BaseAgent(
            name="Chief Investment Officer",
            role="Final Decision Maker",
            system_prompt=CIO_PROMPT,
            model_name=model_name
        )
    }
    
    return agents


def fetch_and_prepare_data(ticker: str) -> tuple[str, Dict]:
    """
    Fetch financial data and prepare context
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Tuple of (formatted_data, data_dict)
    """
    print_separator("STAGE 1: DATA COLLECTION")
    
    # Fetch financial data
    data_fetcher = DataFetcher(ticker)
    data_fetcher.fetch_all_data()
    
    # Format for LLM consumption
    formatted_data = data_fetcher.format_for_llm()
    
    print_success(f"Data collection complete for {ticker}")
    
    return formatted_data, data_fetcher.data


def run_dcf_valuation(ticker: str, data: Dict) -> str:
    """
    Run DCF valuation analysis
    
    Args:
        ticker: Stock ticker symbol
        data: Financial data dictionary
        
    Returns:
        Formatted DCF report
    """
    print_separator("STAGE 2: DCF VALUATION")
    
    fcf_current = data.get('fcf_current', 0)
    fcf_growth_rate = data.get('fcf_growth_rate', 0)
    revenue_growth_yoy = data.get('revenue_growth_yoy', 0)
    
    if fcf_current <= 0:
        print_error("Cannot calculate DCF: FCF is negative or zero")
        return """
DCF VALUATION: UNAVAILABLE
Reason: Free Cash Flow is negative or zero
DCF requires positive FCF to project future cash flows.
"""
    
    # Use dynamic growth rate based on revenue growth
    dynamic_growth_rate = min(abs(revenue_growth_yoy), Config.DCF_DEFAULTS['growth_rate_cap'])
    fcf_growth_capped = max(
        min(fcf_growth_rate, Config.DCF_DEFAULTS['max_growth_rate']),
        Config.DCF_DEFAULTS['min_growth_rate']
    )
    growth_rate = min(dynamic_growth_rate, fcf_growth_capped)
    growth_rate = max(growth_rate, Config.DCF_DEFAULTS['min_growth_rate'])
    
    print(f"   Revenue Growth YoY: {revenue_growth_yoy * 100:.1f}%")
    print(f"   FCF Growth (Historical): {fcf_growth_rate * 100:.1f}%")
    print(f"   Growth Rate Used (Dynamic): {growth_rate * 100:.1f}%")
    
    # Run DCF calculation
    valuation_engine = ValuationEngine(ticker)
    dcf_result = valuation_engine.calculate_dcf(
        fcf=fcf_current,
        growth_rate=growth_rate,
        discount_rate=Config.DCF_DEFAULTS['discount_rate'],
        terminal_growth_rate=Config.DCF_DEFAULTS['terminal_growth_rate'],
        high_growth_years=Config.DCF_DEFAULTS['high_growth_years']
    )
    
    dcf_report = valuation_engine.format_dcf_report(dcf_result)
    
    print_success("DCF valuation complete")
    
    return dcf_report


def run_agent_analysis(agents: Dict[str, BaseAgent], context: str) -> Dict[str, str]:
    """
    Run analysis by all agents sequentially
    
    Args:
        agents: Dictionary of agents
        context: Financial data context
        
    Returns:
        Dictionary of analysis reports by agent name
    """
    print_separator("STAGE 3: MULTI-AGENT ANALYSIS")
    
    reports = {}
    
    # Run first three agents (Value, Growth, Skeptic)
    for key in ['value_hunter', 'growth_visionary', 'skeptic']:
        agent = agents[key]
        report = agent.analyze(context)
        reports[key] = report
        
        # Rate limiting
        time.sleep(Config.AGENT_DELAY)
    
    # CIO gets all previous reports as additional context
    print_section("CIO - FINAL DECISION")
    
    additional_context = f"""
================================================================================
ANALYST REPORTS FOR YOUR REVIEW
================================================================================

VALUE HUNTER ANALYSIS:
{reports['value_hunter']}

GROWTH VISIONARY ANALYSIS:
{reports['growth_visionary']}

SKEPTIC ANALYSIS:
{reports['skeptic']}
"""
    
    reports['cio'] = agents['cio'].analyze(context, additional_context)
    
    print_success("Multi-agent analysis complete")
    
    return reports


def display_final_report(ticker: str, reports: Dict[str, str]):
    """
    Display the final investment analysis report
    
    Args:
        ticker: Stock ticker symbol
        reports: Dictionary of analysis reports
    """
    print_separator(f"FINAL INVESTMENT ANALYSIS REPORT - {ticker}")
    
    print("\n" + "="*80)
    print("VALUE HUNTER PERSPECTIVE")
    print("="*80)
    print(reports['value_hunter'])
    
    print("\n" + "="*80)
    print("GROWTH VISIONARY PERSPECTIVE")
    print("="*80)
    print(reports['growth_visionary'])
    
    print("\n" + "="*80)
    print("SKEPTIC PERSPECTIVE")
    print("="*80)
    print(reports['skeptic'])
    
    print("\n" + "="*80)
    print("CIO FINAL DECISION")
    print("="*80)
    print(reports['cio'])
    
    print_separator()
    print_success(f"Analysis complete for {ticker}")


def analyze_stock(ticker: str, model_name: str = None):
    """
    Main analysis workflow
    
    Args:
        ticker: Stock ticker symbol
        model_name: Gemini model to use (default from config)
    """
    try:
        # Create agents with selected model
        agents = create_agents(model_name)
        
        # Fetch and prepare data
        formatted_data, data_dict = fetch_and_prepare_data(ticker)
        
        # Run DCF valuation
        dcf_report = run_dcf_valuation(ticker, data_dict)
        
        # Combine data with DCF for agent context
        full_context = formatted_data + "\n\n" + dcf_report
        
        # Run agent analysis
        reports = run_agent_analysis(agents, full_context)
        
        # Display final report
        display_final_report(ticker, reports)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print_error(f"Analysis failed: {str(e)}")
        raise


def main():
    """Main entry point"""
    print_separator("MULTI-AGENT AI INVESTMENT ANALYSIS SYSTEM V2.0")
    
    print("""
Welcome to the AI Investment Analysis System!

This system uses 4 specialized AI agents to analyze stocks:
1. Value Hunter - Focuses on intrinsic value and margin of safety
2. Growth Visionary - Seeks high-growth opportunities
3. The Skeptic - Identifies risks and red flags
4. Chief Investment Officer - Makes the final decision

Features:
✅ Live News Integration (DuckDuckGo)
✅ DCF Valuation (2-Stage Model)
✅ Manual FCF Calculation
✅ Dynamic Growth Rates
✅ Multi-Perspective Analysis
    """)
    
    # Select model once at startup
    selected_model = select_model()
    
    while True:
        ticker = input("\nEnter stock ticker (or 'quit' to exit): ").strip().upper()
        
        if ticker in ['QUIT', 'EXIT', 'Q']:
            print("\n👋 Thank you for using the AI Investment Analysis System!")
            break
        
        if not ticker:
            print_error("Please enter a valid ticker symbol")
            continue
        
        analyze_stock(ticker, selected_model)
        
        print("\n" + "-"*80)


if __name__ == "__main__":
    main()
