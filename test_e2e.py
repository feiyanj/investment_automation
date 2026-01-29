#!/usr/bin/env python3
"""
End-to-End Testing Script for V3.0 Investment Analysis System

This script performs comprehensive testing of the complete system,
including all 6 agents and the integration layer.

Run this when API quota is available (after midnight Pacific).

Usage:
    python test_e2e.py                    # Full test suite
    python test_e2e.py --quick            # Quick test (1 stock)
    python test_e2e.py --comparison       # Test comparison feature
"""

import sys
import time
from datetime import datetime
from analyze_complete import InvestmentAnalyzer, analyze_multiple_stocks, print_comparison
from utils.display import print_header, print_success, print_error, print_warning, print_info

def print_test_header(test_name: str):
    """Print a test section header"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80 + "\n")

def test_single_stock():
    """Test 1: Single stock analysis"""
    print_test_header("Single Stock Analysis (AAPL)")
    
    try:
        analyzer = InvestmentAnalyzer('AAPL', verbose=True)
        results = analyzer.analyze()
        
        # Validate results structure
        assert 'metadata' in results, "Missing metadata"
        assert 'company_info' in results, "Missing company_info"
        assert 'business_analysis' in results, "Missing business_analysis"
        assert 'value_analysis' in results, "Missing value_analysis"
        assert 'growth_analysis' in results, "Missing growth_analysis"
        assert 'risk_analysis' in results, "Missing risk_analysis"
        assert 'cio_synthesis' in results, "Missing cio_synthesis"
        
        # Validate decision
        decision = results['cio_synthesis']['decision']
        assert decision['recommendation'] in ['STRONG BUY', 'BUY', 'HOLD', 'REDUCE', 'SELL'], \
            f"Invalid recommendation: {decision['recommendation']}"
        assert 0 <= decision['conviction'] <= 10, \
            f"Invalid conviction: {decision['conviction']}"
        assert 0 <= decision['position_size'] <= 8.0, \
            f"Invalid position size: {decision['position_size']}"
        
        print_success("✅ Test 1 PASSED: Single stock analysis works correctly")
        return True
        
    except Exception as e:
        print_error(f"❌ Test 1 FAILED: {str(e)}")
        return False

def test_save_json():
    """Test 2: Save results as JSON"""
    print_test_header("Save Results (JSON Format)")
    
    try:
        analyzer = InvestmentAnalyzer('MSFT', verbose=False)
        results = analyzer.analyze()
        analyzer.save_results(output_dir='test_output', format='json')
        
        # Check if file was created
        import os
        import glob
        json_files = glob.glob('test_output/MSFT_*.json')
        assert len(json_files) > 0, "No JSON file created"
        
        # Validate JSON structure
        import json
        with open(json_files[0], 'r') as f:
            data = json.load(f)
            assert 'metadata' in data, "Missing metadata in JSON"
            assert 'cio_synthesis' in data, "Missing cio_synthesis in JSON"
        
        print_success("✅ Test 2 PASSED: JSON save works correctly")
        
        # Cleanup
        import shutil
        shutil.rmtree('test_output')
        
        return True
        
    except Exception as e:
        print_error(f"❌ Test 2 FAILED: {str(e)}")
        return False

def test_save_txt():
    """Test 3: Save results as TXT"""
    print_test_header("Save Results (TXT Format)")
    
    try:
        analyzer = InvestmentAnalyzer('GOOGL', verbose=False)
        results = analyzer.analyze()
        analyzer.save_results(output_dir='test_output', format='txt')
        
        # Check if file was created
        import os
        import glob
        txt_files = glob.glob('test_output/GOOGL_*.txt')
        assert len(txt_files) > 0, "No TXT file created"
        
        # Validate TXT content
        with open(txt_files[0], 'r') as f:
            content = f.read()
            assert 'INVESTMENT ANALYSIS REPORT' in content, "Missing header in TXT"
            assert 'FINAL INVESTMENT DECISION' in content, "Missing decision in TXT"
        
        print_success("✅ Test 3 PASSED: TXT save works correctly")
        
        # Cleanup
        import shutil
        shutil.rmtree('test_output')
        
        return True
        
    except Exception as e:
        print_error(f"❌ Test 3 FAILED: {str(e)}")
        return False

def test_multiple_stocks():
    """Test 4: Multiple stock analysis"""
    print_test_header("Multiple Stock Analysis (3 stocks)")
    
    try:
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        results = []
        
        for ticker in tickers:
            print_info(f"Analyzing {ticker}...")
            analyzer = InvestmentAnalyzer(ticker, verbose=False)
            result = analyzer.analyze()
            results.append(result)
            time.sleep(10)  # Avoid rate limits
        
        # Validate all results
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        for r in results:
            assert 'cio_synthesis' in r, "Missing cio_synthesis"
            decision = r['cio_synthesis']['decision']
            assert decision['recommendation'] is not None, "Missing recommendation"
        
        print_success("✅ Test 4 PASSED: Multiple stock analysis works")
        return True
        
    except Exception as e:
        print_error(f"❌ Test 4 FAILED: {str(e)}")
        return False

def test_comparison_table():
    """Test 5: Comparison table"""
    print_test_header("Comparison Table (3 stocks)")
    
    try:
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        results = analyze_multiple_stocks(tickers, save=False, compare=True)
        
        # Validate comparison was printed (visual check needed)
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        print_success("✅ Test 5 PASSED: Comparison table displayed")
        return True
        
    except Exception as e:
        print_error(f"❌ Test 5 FAILED: {str(e)}")
        return False

def test_different_sectors():
    """Test 6: Different sector stocks"""
    print_test_header("Cross-Sector Analysis")
    
    try:
        # Test different types of stocks
        stocks = {
            'JNJ': 'Healthcare (Value)',
            'NVDA': 'Technology (Growth)',
            'JPM': 'Financial (Cyclical)',
            'WMT': 'Consumer Defensive'
        }
        
        results = []
        for ticker, description in stocks.items():
            print_info(f"Testing {ticker} ({description})...")
            analyzer = InvestmentAnalyzer(ticker, verbose=False)
            result = analyzer.analyze()
            results.append(result)
            
            # Validate
            decision = result['cio_synthesis']['decision']
            assert decision['recommendation'] is not None, \
                f"Missing recommendation for {ticker}"
            
            time.sleep(10)  # Avoid rate limits
        
        print_success("✅ Test 6 PASSED: Cross-sector analysis works")
        return True
        
    except Exception as e:
        print_error(f"❌ Test 6 FAILED: {str(e)}")
        return False

def quick_test():
    """Quick test - just one stock"""
    print_test_header("QUICK TEST (Single Stock Only)")
    return test_single_stock()

def full_test():
    """Run all tests"""
    print_header("INVESTMENT ANALYSIS SYSTEM V3.0 - E2E TESTING")
    print_info(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_warning("⚠️  This will take ~30-40 minutes to complete")
    print_warning("⚠️  Ensure you have sufficient API quota available\n")
    
    # Track results
    tests = [
        ("Single Stock Analysis", test_single_stock),
        ("Save JSON", test_save_json),
        ("Save TXT", test_save_txt),
        ("Multiple Stocks", test_multiple_stocks),
        ("Comparison Table", test_comparison_table),
        ("Cross-Sector Analysis", test_different_sectors),
    ]
    
    results = []
    start_time = time.time()
    
    for i, (name, test_func) in enumerate(tests, 1):
        print_info(f"\n[{i}/{len(tests)}] Running: {name}")
        result = test_func()
        results.append((name, result))
        
        if not result:
            print_warning(f"⚠️  Test failed, but continuing...")
        
        # Pause between tests to avoid rate limits
        if i < len(tests):
            print_info("Pausing 15 seconds to avoid rate limits...")
            time.sleep(15)
    
    # Summary
    duration = time.time() - start_time
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "-"*80)
    print(f"Results: {passed}/{total} tests passed")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print("="*80 + "\n")
    
    if passed == total:
        print_success("🎉 ALL TESTS PASSED! System is fully functional.")
        return 0
    else:
        print_warning(f"⚠️  {total - passed} test(s) failed. Review output above.")
        return 1

def comparison_test():
    """Test comparison feature only"""
    print_header("COMPARISON FEATURE TEST")
    return test_comparison_table()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            exit_code = 0 if quick_test() else 1
        elif sys.argv[1] == '--comparison':
            exit_code = 0 if comparison_test() else 1
        else:
            print_error(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python test_e2e.py [--quick|--comparison]")
            exit_code = 1
    else:
        exit_code = full_test()
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
