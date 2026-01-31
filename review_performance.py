"""
Performance Review Script
Review and analyze historical investment decisions
"""
import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import yfinance as yf
from utils.performance_tracker import PerformanceTracker


def get_current_price(ticker: str) -> float:
    """Get current price for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
    except:
        return None


def calculate_return(initial_price: float, current_price: float) -> float:
    """Calculate return percentage"""
    if initial_price and current_price:
        return ((current_price - initial_price) / initial_price) * 100
    return None


def review_all_decisions():
    """Review all logged decisions with current performance"""
    tracker = PerformanceTracker()
    decisions = tracker.get_all_decisions()
    
    if not decisions:
        print("No decisions logged yet.")
        return
    
    print("\n" + "="*120)
    print("INVESTMENT DECISION PERFORMANCE REVIEW")
    print("="*120 + "\n")
    
    print(f"{'Date':<12} {'Ticker':<8} {'Model':<25} {'Rec':<10} {'Conv':<6} {'Price@':<10} {'Now':<10} {'Return':<10} {'Status':<10}")
    print("-"*120)
    
    total_decisions = len(decisions)
    correct_decisions = 0
    total_return = 0
    analyzed_count = 0
    
    for decision in decisions:
        date = decision['date']
        ticker = decision['ticker']
        model = decision['model'][:23]
        rec = decision['recommendation'][:8]
        conv = f"{decision['conviction']}/10" if decision['conviction'] else "N/A"
        initial_price = decision['current_price']
        
        # Get current price
        current_price = get_current_price(ticker)
        
        if initial_price and current_price:
            actual_return = calculate_return(initial_price, current_price)
            
            # Determine if decision was "correct"
            if rec == 'BUY' and actual_return > 0:
                status = "✅ Correct"
                correct_decisions += 1
            elif rec == 'SELL' and actual_return < 0:
                status = "✅ Correct"
                correct_decisions += 1
            elif rec == 'HOLD':
                status = "⚪ Hold"
            else:
                status = "❌ Wrong"
            
            total_return += actual_return
            analyzed_count += 1
            
            price_at = f"${initial_price:.2f}"
            price_now = f"${current_price:.2f}"
            ret_str = f"{actual_return:+.1f}%"
        else:
            price_at = f"${initial_price:.2f}" if initial_price else "N/A"
            price_now = "N/A"
            ret_str = "N/A"
            status = "❓ Unknown"
        
        print(f"{date:<12} {ticker:<8} {model:<25} {rec:<10} {conv:<6} {price_at:<10} {price_now:<10} {ret_str:<10} {status:<10}")
    
    print("-"*120)
    print(f"\nSUMMARY:")
    print(f"  Total Decisions: {total_decisions}")
    print(f"  Analyzable: {analyzed_count} ({analyzed_count/total_decisions*100:.1f}%)")
    if analyzed_count > 0:
        print(f"  Correct: {correct_decisions} ({correct_decisions/analyzed_count*100:.1f}%)")
        print(f"  Average Return: {total_return/analyzed_count:+.1f}%")
    print("="*120 + "\n")


def review_by_ticker(ticker: str):
    """Review decisions for a specific ticker"""
    tracker = PerformanceTracker()
    decisions = tracker.get_decisions_by_ticker(ticker)
    
    if not decisions:
        print(f"No decisions found for {ticker}")
        return
    
    print(f"\n" + "="*80)
    print(f"DECISION HISTORY FOR {ticker}")
    print("="*80 + "\n")
    
    current_price = get_current_price(ticker)
    
    for i, decision in enumerate(decisions, 1):
        print(f"Decision #{i}")
        print(f"  Date: {decision['date']}")
        print(f"  Model: {decision['model']}")
        print(f"  Recommendation: {decision['recommendation']}")
        print(f"  Conviction: {decision['conviction']}/10")
        print(f"  Price at Analysis: ${decision['current_price']:.2f}")
        
        if current_price:
            actual_return = calculate_return(decision['current_price'], current_price)
            print(f"  Current Price: ${current_price:.2f}")
            print(f"  Actual Return: {actual_return:+.1f}%")
        
        if decision.get('fair_value'):
            print(f"  Fair Value (at time): ${decision['fair_value']:.2f}")
        
        if decision.get('expected_return_3y'):
            print(f"  Expected 3Y Return: {decision['expected_return_3y']:.1f}%")
        
        print()


def review_by_model(model: str):
    """Review performance of a specific model"""
    tracker = PerformanceTracker()
    decisions = tracker.get_decisions_by_model(model)
    
    if not decisions:
        print(f"No decisions found for model: {model}")
        return
    
    print(f"\n" + "="*80)
    print(f"PERFORMANCE REVIEW: {model}")
    print("="*80 + "\n")
    
    buy_decisions = [d for d in decisions if d['recommendation'] == 'BUY']
    sell_decisions = [d for d in decisions if d['recommendation'] == 'SELL']
    
    print(f"Total Decisions: {len(decisions)}")
    print(f"  BUY: {len(buy_decisions)}")
    print(f"  SELL: {len(sell_decisions)}")
    print()
    
    # Calculate returns for BUY recommendations
    if buy_decisions:
        print("BUY RECOMMENDATIONS:")
        total_return = 0
        count = 0
        
        for decision in buy_decisions:
            ticker = decision['ticker']
            initial_price = decision['current_price']
            current_price = get_current_price(ticker)
            
            if initial_price and current_price:
                actual_return = calculate_return(initial_price, current_price)
                total_return += actual_return
                count += 1
                
                status = "✅" if actual_return > 0 else "❌"
                print(f"  {status} {ticker}: {actual_return:+.1f}% (${initial_price:.2f} → ${current_price:.2f})")
        
        if count > 0:
            print(f"\n  Average Return: {total_return/count:+.1f}%")
            print(f"  Win Rate: {sum(1 for d in buy_decisions if calculate_return(d['current_price'], get_current_price(d['ticker'])) > 0) / count * 100:.1f}%")
    
    print("\n" + "="*80 + "\n")


def review_recent(days: int = 30):
    """Review recent decisions"""
    tracker = PerformanceTracker()
    decisions = tracker.get_recent_decisions(days=days)
    
    if not decisions:
        print(f"No decisions in the last {days} days")
        return
    
    print(f"\n" + "="*80)
    print(f"DECISIONS IN LAST {days} DAYS")
    print("="*80 + "\n")
    
    for decision in decisions:
        print(f"{decision['date']} - {decision['ticker']}: {decision['recommendation']}")
        print(f"  Model: {decision['model']}")
        print(f"  Conviction: {decision['conviction']}/10")
        print(f"  Price: ${decision['current_price']:.2f}")
        
        current_price = get_current_price(decision['ticker'])
        if current_price:
            actual_return = calculate_return(decision['current_price'], current_price)
            print(f"  Current: ${current_price:.2f} ({actual_return:+.1f}%)")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Review Investment Decision Performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python review_performance.py                    # Review all decisions
  python review_performance.py --ticker AAPL      # Review AAPL decisions
  python review_performance.py --model gemini-3-flash-preview
  python review_performance.py --recent 7         # Last 7 days
        """
    )
    
    parser.add_argument('--ticker', type=str, help='Review specific ticker')
    parser.add_argument('--model', type=str, help='Review specific model')
    parser.add_argument('--recent', type=int, help='Review decisions from last N days')
    
    args = parser.parse_args()
    
    if args.ticker:
        review_by_ticker(args.ticker.upper())
    elif args.model:
        review_by_model(args.model)
    elif args.recent:
        review_recent(days=args.recent)
    else:
        review_all_decisions()


if __name__ == "__main__":
    main()
