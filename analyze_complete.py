"""
Investment Analysis System V3.0 - Complete Integration
======================================================
Comprehensive stock analysis using 6 specialized AI agents:
1. Business Analyst - Understanding the business
2. Value Hunter - Quality and intrinsic value
3. Growth Analyzer - Growth quality and sustainability  
4. Risk Examiner - Risks and red flags
5. CIO Synthesizer - Final investment decision

Usage:
    python analyze_complete.py AAPL
    python analyze_complete.py AAPL --save --format json
    python analyze_complete.py AAPL MSFT GOOGL --compare
"""
import sys
import argparse
import json
from datetime import datetime
from typing import Dict, List
import os

from config import Config
from data.fetcher_v3 import DataFetcherV3
from agents import (
    BusinessAnalyst,
    ValueHunter,
    GrowthAnalyzer,
    RiskExaminer,
    CIOSynthesizer
)
from utils.display import (
    print_header,
    print_section,
    print_success,
    print_error,
    print_warning
)


class InvestmentAnalyzer:
    """Complete investment analysis system integrating all 6 agents"""
    
    def __init__(self, ticker: str, verbose: bool = True, model_name: str = None):
        self.ticker = ticker.upper()
        self.verbose = verbose
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.results = {}
        
    def analyze(self) -> Dict:
        """
        Run complete 6-stage analysis
        
        Returns:
            Dictionary with all analysis results
        """
        if self.verbose:
            print_header(f"Investment Analysis: {self.ticker}")
            print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        try:
            # Stage 1: Data Collection
            if self.verbose:
                print_section("Stage 1/6: Data Collection")
            data, info = self._collect_data()
            
            # Stage 2: Business Understanding
            if self.verbose:
                print_section("Stage 2/6: Business Understanding")
            business_analysis, key_events = self._analyze_business(data, info)
            
            # Stage 3: Value Analysis
            if self.verbose:
                print_section("Stage 3/6: Value Analysis")
            value_analysis, value_summary = self._analyze_value(
                data, info, business_analysis, key_events
            )
            
            # Stage 4: Growth Analysis
            if self.verbose:
                print_section("Stage 4/6: Growth Analysis")
            growth_analysis, growth_summary = self._analyze_growth(
                data, info, business_analysis, key_events
            )
            
            # Stage 5: Risk Analysis
            if self.verbose:
                print_section("Stage 5/6: Risk Analysis")
            risk_analysis, risk_summary = self._analyze_risk(
                data, info, business_analysis, key_events,
                value_analysis, growth_analysis
            )
            
            # Stage 6: CIO Synthesis
            if self.verbose:
                print_section("Stage 6/6: CIO Final Decision")
            synthesis, decision_summary = self._synthesize_decision(
                data, info, business_analysis,
                value_analysis, growth_analysis, risk_analysis,
                value_summary, growth_summary, risk_summary
            )
            
            # Compile results
            self.results = {
                'ticker': self.ticker,
                'timestamp': datetime.now().isoformat(),
                'company_info': {
                    'name': info.get('longName', info.get('name', self.ticker)),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'current_price': info.get('currentPrice', 0)
                },
                'business_analysis': business_analysis,
                'key_events': key_events,
                'value_analysis': {
                    'full_analysis': value_analysis,
                    'summary': value_summary
                },
                'growth_analysis': {
                    'full_analysis': growth_analysis,
                    'summary': growth_summary
                },
                'risk_analysis': {
                    'full_analysis': risk_analysis,
                    'summary': risk_summary
                },
                'cio_synthesis': {
                    'full_synthesis': synthesis,
                    'decision': decision_summary
                }
            }
            
            if self.verbose:
                print_success(f"\n✅ Analysis complete for {self.ticker}")
                self._print_executive_summary()
            
            return self.results
            
        except Exception as e:
            if self.verbose:
                print_error(f"❌ Analysis failed: {str(e)}")
            raise
    
    def _collect_data(self) -> tuple:
        """Stage 1: Collect comprehensive financial data"""
        fetcher = DataFetcherV3(self.ticker)
        data = fetcher.fetch_all_data()
        info = data.get('company_info', {})
        
        if self.verbose:
            print(f"✅ Data collected")
            print(f"   Company: {info.get('longName', self.ticker)}")
            print(f"   Price: ${info.get('currentPrice', 0):.2f}")
            print(f"   Financials: {len(data.get('income_5y', {}))} years")
            print(f"   News: {len(data.get('news', []))} articles\n")
        
        return data, info
    
    def _analyze_business(self, data: Dict, info: Dict) -> tuple:
        """Stage 2: Understand the business"""
        analyst = BusinessAnalyst(model_name=self.model_name)
        
        if self.verbose:
            print("Analyzing business fundamentals...")
        business_analysis = analyst.analyze_business(data, info)
        
        if self.verbose:
            print("Extracting key events...")
        key_events = analyst.extract_key_events(data.get('news', []), info)
        
        if self.verbose:
            print(f"✅ Business analysis: {len(business_analysis)} chars")
            print(f"✅ Key events: {len(key_events)} chars\n")
        
        return business_analysis, key_events
    
    def _analyze_value(self, data: Dict, info: Dict, 
                       business_analysis: str, key_events: str) -> tuple:
        """Stage 3: Analyze value and quality"""
        hunter = ValueHunter(model_name=self.model_name)
        
        if self.verbose:
            print("Conducting value analysis (30-60 seconds)...")
        value_analysis = hunter.analyze(data, info, business_analysis, key_events)
        value_summary = hunter.get_analysis_summary(value_analysis)
        
        if self.verbose:
            print(f"✅ Value analysis: {len(value_analysis)} chars")
            print(f"   Quality Score: {value_summary.get('quality_score', 'N/A')}/10")
            print(f"   Recommendation: {value_summary.get('recommendation', 'N/A')}\n")
        
        return value_analysis, value_summary
    
    def _analyze_growth(self, data: Dict, info: Dict,
                        business_analysis: str, key_events: str) -> tuple:
        """Stage 4: Analyze growth quality"""
        analyzer = GrowthAnalyzer(model_name=self.model_name)
        
        if self.verbose:
            print("Conducting growth analysis (30-60 seconds)...")
        growth_analysis = analyzer.analyze(data, info, business_analysis, key_events)
        growth_summary = analyzer.get_growth_summary(growth_analysis)
        
        if self.verbose:
            print(f"✅ Growth analysis: {len(growth_analysis)} chars")
            print(f"   Historical Quality: {growth_summary.get('historical_quality_score', 'N/A')}/10")
            print(f"   Market Space: {growth_summary.get('market_space_score', 'N/A')}/10")
            print(f"   Recommendation: {growth_summary.get('recommendation', 'N/A')}\n")
        
        return growth_analysis, growth_summary
    
    def _analyze_risk(self, data: Dict, info: Dict,
                      business_analysis: str, key_events: str,
                      value_analysis: str, growth_analysis: str) -> tuple:
        """Stage 5: Analyze risks and red flags"""
        examiner = RiskExaminer(model_name=self.model_name)
        
        if self.verbose:
            print("Conducting risk analysis (30-60 seconds)...")
        risk_analysis = examiner.analyze(
            data, info, business_analysis, key_events,
            value_analysis, growth_analysis
        )
        risk_summary = examiner.get_risk_summary(risk_analysis)
        
        if self.verbose:
            print(f"✅ Risk analysis: {len(risk_analysis)} chars")
            print(f"   Risk Score: {risk_summary.get('overall_risk_score', 'N/A')}/10")
            print(f"   Risk Rating: {risk_summary.get('risk_rating', 'N/A')}")
            print(f"   Red Flags: {risk_summary.get('red_flags_count', 0)}\n")
        
        return risk_analysis, risk_summary
    
    def _synthesize_decision(self, data: Dict, info: Dict,
                            business_analysis: str,
                            value_analysis: str, growth_analysis: str, risk_analysis: str,
                            value_summary: Dict, growth_summary: Dict, risk_summary: Dict) -> tuple:
        """Stage 6: Synthesize final investment decision"""
        cio = CIOSynthesizer(model_name=self.model_name)
        
        if self.verbose:
            print("Synthesizing final decision (30-60 seconds)...")
        synthesis = cio.synthesize(
            data, info, business_analysis,
            value_analysis, growth_analysis, risk_analysis,
            value_summary, growth_summary, risk_summary
        )
        decision_summary = cio.get_decision_summary(synthesis)
        
        if self.verbose:
            print(f"✅ CIO synthesis: {len(synthesis)} chars\n")
        
        return synthesis, decision_summary
    
    def _print_executive_summary(self):
        """Print executive summary of the analysis"""
        decision = self.results['cio_synthesis']['decision']
        
        print("\n" + "="*80)
        print(" " * 25 + "EXECUTIVE SUMMARY")
        print("="*80)
        print(f"\nCompany: {self.results['company_info']['name']}")
        print(f"Ticker: {self.ticker}")
        print(f"Current Price: ${self.results['company_info']['current_price']:.2f}")
        print(f"Sector: {self.results['company_info']['sector']}")
        
        print(f"\n{'─'*80}")
        print("FINAL INVESTMENT DECISION:")
        print(f"{'─'*80}")
        print(f"Recommendation: {decision.get('recommendation', 'N/A')}")
        print(f"Conviction: {decision.get('conviction', 0)}/10")
        print(f"Position Size: {decision.get('position_size', 0):.2f}%")
        print(f"Composite Score: {decision.get('composite_score', 0):.1f}/10")
        
        if decision.get('cio_fair_value', 0) > 0:
            print(f"\nCIO Fair Value: ${decision.get('cio_fair_value', 0):.2f}")
            print(f"Upside: {decision.get('upside_to_fair_value', 0):.1f}%")
        
        print(f"Expected 3Y Return: {decision.get('expected_return_3y', 0):.1f}%")
        
        if decision.get('entry_price_low', 0) > 0:
            print(f"\nEntry Range: ${decision.get('entry_price_low', 0):.2f} - ${decision.get('entry_price_high', 0):.2f}")
        if decision.get('stop_loss', 0) > 0:
            print(f"Stop Loss: ${decision.get('stop_loss', 0):.2f}")
        if decision.get('target_price', 0) > 0:
            print(f"Target Price: ${decision.get('target_price', 0):.2f}")
        
        print("="*80 + "\n")
    
    def save_results(self, output_dir: str = "output", format: str = "json"):
        """Save analysis results to file"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"{output_dir}/{self.ticker}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✅ Results saved to: {filename}")
        
        elif format == "txt":
            filename = f"{output_dir}/{self.ticker}_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"Investment Analysis Report: {self.ticker}\n")
                f.write(f"Generated: {self.results['timestamp']}\n")
                f.write("="*80 + "\n\n")
                
                f.write("EXECUTIVE SUMMARY\n")
                f.write("-"*80 + "\n")
                decision = self.results['cio_synthesis']['decision']
                f.write(f"Recommendation: {decision.get('recommendation', 'N/A')}\n")
                f.write(f"Conviction: {decision.get('conviction', 0)}/10\n")
                f.write(f"Position Size: {decision.get('position_size', 0):.2f}%\n\n")
                
                f.write("\nFULL CIO SYNTHESIS\n")
                f.write("="*80 + "\n\n")
                f.write(self.results['cio_synthesis']['full_synthesis'])
            
            print(f"✅ Results saved to: {filename}")


def analyze_single_stock(ticker: str, save: bool = False, format: str = "json", 
                        model: str = None, show_full: bool = False, log_decision: bool = False):
    """Analyze a single stock"""
    analyzer = InvestmentAnalyzer(ticker, verbose=True, model_name=model)
    results = analyzer.analyze()
    
    # Log decision for performance tracking (only if explicitly requested)
    if log_decision:
        from utils.performance_tracker import PerformanceTracker, extract_decision_data
        tracker = PerformanceTracker()
        
        # Extract decision data
        decision_data = extract_decision_data(analyzer)
        decision_data['model'] = model or analyzer.model_name
        
        # Add output file if saved
        if save:
            # Get timestamp from results and format for filename
            timestamp_iso = results.get('timestamp', datetime.now().isoformat())
            # Convert ISO format to filename format: 20260131_031405
            timestamp = datetime.fromisoformat(timestamp_iso).strftime('%Y%m%d_%H%M%S')
            
            if format == "txt":
                decision_data['output_file'] = f"output/{ticker}_{timestamp}.txt"
            else:
                decision_data['output_file'] = f"output/{ticker}_{timestamp}.json"
        
        # Log the decision
        tracker.log_decision(decision_data)
    
    # Display full reports if requested
    if show_full:
        print("\n" + "="*80)
        print("📊 FULL ANALYSIS REPORTS")
        print("="*80 + "\n")
        
        # Business Analysis
        print("\n" + "="*80)
        print("1️⃣  BUSINESS UNDERSTANDING")
        print("="*80 + "\n")
        print(results['business_analysis']['full_analysis'])
        
        # Value Analysis
        print("\n" + "="*80)
        print("2️⃣  VALUE HUNTER ANALYSIS")
        print("="*80 + "\n")
        print(results['value_analysis']['full_analysis'])
        
        # Growth Analysis
        print("\n" + "="*80)
        print("3️⃣  GROWTH ANALYZER REPORT")
        print("="*80 + "\n")
        print(results['growth_analysis']['full_analysis'])
        
        # Risk Analysis
        print("\n" + "="*80)
        print("4️⃣  RISK EXAMINER REPORT")
        print("="*80 + "\n")
        print(results['risk_analysis']['full_analysis'])
        
        # CIO Synthesis
        print("\n" + "="*80)
        print("5️⃣  CIO FINAL SYNTHESIS")
        print("="*80 + "\n")
        print(results['cio_synthesis']['full_synthesis'])
        
        print("\n" + "="*80)
        print("✅ Full Analysis Complete")
        print("="*80 + "\n")
    
    if save:
        analyzer.save_results(format=format)
    
    return results


def analyze_multiple_stocks(tickers: List[str], save: bool = False, compare: bool = False, 
                          model: str = None, show_full: bool = False):
    """Analyze multiple stocks"""
    results = []
    
    for i, ticker in enumerate(tickers, 1):
        print(f"\n{'='*80}")
        print(f"Analyzing {i}/{len(tickers)}: {ticker}")
        print(f"{'='*80}\n")
        
        try:
            analyzer = InvestmentAnalyzer(ticker, verbose=True, model_name=model)
            result = analyzer.analyze()
            results.append(result)
            
            # Display full reports if requested
            if show_full:
                print("\n" + "="*80)
                print(f"📊 FULL REPORTS FOR {ticker}")
                print("="*80 + "\n")
                
                print("\n🔹 CIO SYNTHESIS (Most Important)\n")
                print(result['cio_synthesis']['full_synthesis'])
                print("\n" + "-"*80 + "\n")
            
            if save:
                analyzer.save_results()
        
        except Exception as e:
            print_error(f"Failed to analyze {ticker}: {str(e)}")
            continue
    
    if compare and len(results) > 1:
        print_comparison(results)
    
    return results


def print_comparison(results: List[Dict]):
    """Print comparison table of multiple stocks"""
    print("\n" + "="*80)
    print(" " * 30 + "COMPARISON")
    print("="*80 + "\n")
    
    # Header
    print(f"{'Ticker':<10} {'Recommendation':<15} {'Conviction':<12} {'Position':<10} {'Score':<8} {'3Y Return':<10}")
    print("-"*80)
    
    # Rows
    for result in results:
        ticker = result['ticker']
        decision = result['cio_synthesis']['decision']
        
        rec = decision.get('recommendation', 'N/A')[:14]
        conviction = f"{decision.get('conviction', 0)}/10"
        position = f"{decision.get('position_size', 0):.1f}%"
        score = f"{decision.get('composite_score', 0):.1f}/10"
        ret_3y = f"{decision.get('expected_return_3y', 0):.1f}%"
        
        print(f"{ticker:<10} {rec:<15} {conviction:<12} {position:<10} {score:<8} {ret_3y:<10}")
    
    print("="*80 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Investment Analysis System V3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_complete.py AAPL
  python analyze_complete.py AAPL --save --format json
  python analyze_complete.py AAPL MSFT GOOGL --compare
  python analyze_complete.py AAPL --model gemini-3-flash-preview
  python analyze_complete.py AAPL MSFT --save --compare --model gemini-2.5-flash-lite
        """
    )
    
    parser.add_argument('tickers', nargs='+', help='Stock ticker(s) to analyze')
    parser.add_argument('--save', action='store_true', help='Save results to file')
    parser.add_argument('--format', choices=['json', 'txt'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--compare', action='store_true',
                       help='Compare multiple stocks')
    parser.add_argument('--full', action='store_true',
                       help='Display full analysis reports (not just summaries)')
    parser.add_argument('--model', type=str, default=None,
                       help=f'AI model to use (default: {Config.DEFAULT_MODEL}). '
                            f'Options: gemini-2.5-flash, gemini-2.5-flash-lite, gemini-3-flash-preview')
    parser.add_argument('--log', action='store_true',
                       help='Log decision to performance tracker for later review')
    
    args = parser.parse_args()
    
    # Display model selection
    model = args.model or Config.DEFAULT_MODEL
    print(f"🤖 Using model: {model}")
    if args.model:
        print(f"   (Overriding default: {Config.DEFAULT_MODEL})")
    print()
    
    try:
        if len(args.tickers) == 1:
            analyze_single_stock(args.tickers[0], save=args.save, format=args.format, 
                               model=args.model, show_full=args.full, log_decision=args.log)
        else:
            analyze_multiple_stocks(args.tickers, save=args.save, compare=args.compare, 
                                  model=args.model, show_full=args.full)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
