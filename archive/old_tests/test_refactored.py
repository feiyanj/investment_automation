#!/usr/bin/env python3
"""
Quick Test Script - Verify Refactored System
Tests imports and basic functionality
"""
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing Imports...")
    
    try:
        from config import Config
        print("   ✅ config.py")
    except Exception as e:
        print(f"   ❌ config.py: {e}")
        return False
    
    try:
        from agents import BaseAgent, VALUE_HUNTER_PROMPT
        print("   ✅ agents package")
    except Exception as e:
        print(f"   ❌ agents package: {e}")
        return False
    
    try:
        from data import DataFetcher, NewsFetcher, FinancialCalculator
        print("   ✅ data package")
    except Exception as e:
        print(f"   ❌ data package: {e}")
        return False
    
    try:
        from valuation import ValuationEngine
        print("   ✅ valuation package")
    except Exception as e:
        print(f"   ❌ valuation package: {e}")
        return False
    
    try:
        from utils import print_separator, format_currency
        print("   ✅ utils package")
    except Exception as e:
        print(f"   ❌ utils package: {e}")
        return False
    
    return True


def test_config():
    """Test configuration module"""
    print("\n🧪 Testing Configuration...")
    
    try:
        from config import Config
        
        assert Config.DEFAULT_MODEL is not None
        print("   ✅ Default model configured")
        
        assert Config.DCF_DEFAULTS is not None
        print("   ✅ DCF defaults configured")
        
        assert Config.AGENT_DELAY > 0
        print("   ✅ Rate limiting configured")
        
        return True
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False


def test_utilities():
    """Test utility functions"""
    print("\n🧪 Testing Utilities...")
    
    try:
        from utils import format_currency, format_percentage
        
        # Test currency formatting
        result = format_currency(1234567.89, decimals=2)
        assert "$" in result
        print(f"   ✅ format_currency: {result}")
        
        # Test percentage formatting
        result = format_percentage(0.1542, decimals=2)
        assert "%" in result
        print(f"   ✅ format_percentage: {result}")
        
        return True
    except Exception as e:
        print(f"   ❌ Utilities test failed: {e}")
        return False


def test_financial_calculator():
    """Test financial calculator"""
    print("\n🧪 Testing Financial Calculator...")
    
    try:
        from data import FinancialCalculator
        
        calc = FinancialCalculator()
        
        # Test CAGR calculation
        cagr = calc.calculate_cagr([9.4, 7.2, 4.5, 1.6])
        print(f"   ✅ CAGR calculation: {cagr*100:.1f}%")
        
        # Test PEG ratio
        peg = calc.calculate_peg_ratio(25.5, 0.20)
        print(f"   ✅ PEG ratio calculation: {peg}")
        
        return True
    except Exception as e:
        print(f"   ❌ Financial calculator test failed: {e}")
        return False


def main():
    print("="*80)
    print("REFACTORED SYSTEM - QUICK TEST")
    print("="*80)
    print()
    
    tests_passed = 0
    tests_total = 4
    
    # Run tests
    if test_imports():
        tests_passed += 1
    
    if test_config():
        tests_passed += 1
    
    if test_utilities():
        tests_passed += 1
    
    if test_financial_calculator():
        tests_passed += 1
    
    # Summary
    print()
    print("="*80)
    print(f"TEST RESULTS: {tests_passed}/{tests_total} PASSED")
    print("="*80)
    
    if tests_passed == tests_total:
        print("\n✅ All tests passed! Refactored system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python cleanup.py (to remove old files)")
        print("2. Run: python analyze.py (to test with real data)")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
