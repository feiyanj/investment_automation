"""
Test Setup for Investment Analysis System V2.0
Verifies all components are properly installed and configured
"""

import sys
import os

def test_environment():
    """Test basic Python environment"""
    print("🔍 Testing Python Environment...")
    print(f"   Python Version: {sys.version}")
    print(f"   ✅ Python environment OK")


def test_packages():
    """Test required packages are installed"""
    print("\n🔍 Testing Required Packages...")
    
    packages = {
        'google.generativeai': 'google-generativeai',
        'yfinance': 'yfinance',
        'pandas': 'pandas',
        'dotenv': 'python-dotenv',
        'duckduckgo_search': 'duckduckgo-search',  # V2 NEW
        'numpy': 'numpy'  # V2 NEW
    }
    
    missing = []
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} NOT FOUND")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    else:
        print(f"   ✅ All packages installed")
        return True


def test_api_key():
    """Test Google API key is configured"""
    print("\n🔍 Testing API Key Configuration...")
    
    # Try to load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception as e:
        print(f"   ⚠️  Could not load .env: {e}")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("   ❌ GOOGLE_API_KEY not found in environment")
        print("\n   Please:")
        print("   1. Get API key from: https://makersuite.google.com/app/apikey")
        print("   2. Create .env file")
        print("   3. Add: GOOGLE_API_KEY=your_key_here")
        return False
    
    # Mask the key for security
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"   ✅ GOOGLE_API_KEY found: {masked_key}")
    return True


def test_gemini_connection():
    """Test connection to Gemini API"""
    print("\n🔍 Testing Gemini API Connection...")
    
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("   ⚠️  Skipping (no API key)")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test with a simple prompt
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say 'Connection test successful' and nothing else.")
        
        print(f"   ✅ Gemini 2.5 Flash API responding")
        print(f"   Response: {response.text[:50]}...")
        return True
        
    except Exception as e:
        print(f"   ❌ Gemini API test failed: {str(e)}")
        return False


def test_yfinance():
    """Test Yahoo Finance data fetching"""
    print("\n🔍 Testing Yahoo Finance Connection...")
    
    try:
        import yfinance as yf
        
        # Try to fetch data for a reliable ticker
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info and 'symbol' in info:
            print(f"   ✅ Yahoo Finance API responding")
            print(f"   Test Symbol: {info.get('symbol', 'N/A')}")
            print(f"   Company: {info.get('longName', 'N/A')}")
            return True
        else:
            print(f"   ⚠️  Yahoo Finance returned incomplete data")
            return False
            
    except Exception as e:
        print(f"   ❌ Yahoo Finance test failed: {str(e)}")
        return False


def test_news_search():
    """Test DuckDuckGo news search (V2 NEW)"""
    print("\n🔍 Testing News Search (V2 Feature)...")
    
    try:
        from duckduckgo_search import DDGS
        
        # Try a simple news search
        ddgs = DDGS()
        results = list(ddgs.news(
            keywords="AAPL stock news",
            max_results=2,
            region='wt-wt'
        ))
        
        if results:
            print(f"   ✅ DuckDuckGo news search working")
            print(f"   Found {len(results)} test articles")
            return True
        else:
            print(f"   ⚠️  No news results (might be rate limited)")
            return False
            
    except Exception as e:
        print(f"   ❌ News search test failed: {str(e)}")
        print(f"   This is optional - analysis can work without news")
        return False


def test_valuation_engine():
    """Test DCF valuation engine (V2 NEW)"""
    print("\n🔍 Testing DCF Valuation Engine (V2 Feature)...")
    
    try:
        from valuation_engine import ValuationEngine
        import numpy as np
        
        # Test DCF calculation with sample data
        engine = ValuationEngine("TEST")
        
        dcf_result = engine.calculate_dcf(
            fcf=10_000_000_000,  # $10B FCF
            growth_rate=0.15,    # 15% growth
            discount_rate=0.10,  # 10% WACC
            shares_outstanding=1_000_000_000  # 1B shares
        )
        
        if dcf_result and 'intrinsic_value_per_share' in dcf_result:
            intrinsic = dcf_result['intrinsic_value_per_share']
            print(f"   ✅ DCF calculation working")
            print(f"   Test Intrinsic Value: ${intrinsic:.2f}")
            
            # Test margin of safety
            mos = engine.calculate_margin_of_safety(intrinsic, intrinsic * 0.8)
            print(f"   ✅ Margin of Safety calculation working")
            print(f"   Test MOS: {mos['margin_of_safety_%']:.1f}%")
            return True
        else:
            print(f"   ❌ DCF result incomplete")
            return False
            
    except Exception as e:
        print(f"   ❌ Valuation engine test failed: {str(e)}")
        return False


def test_data_fetcher():
    """Test enhanced data fetcher with news"""
    print("\n🔍 Testing Enhanced Data Fetcher (V2)...")
    
    try:
        from data_fetcher import DataFetcher
        
        # Test with Apple (reliable ticker)
        fetcher = DataFetcher("AAPL")
        
        # Fetch just company info as a quick test
        company_info = fetcher._get_company_info()
        
        if company_info and 'name' in company_info:
            print(f"   ✅ Data fetcher working")
            print(f"   Test Company: {company_info['name']}")
            
            # Check if news method exists
            if hasattr(fetcher, '_get_live_news'):
                print(f"   ✅ News fetching method available")
            
            # Check if derived metrics method exists
            if hasattr(fetcher, '_calculate_derived_metrics'):
                print(f"   ✅ Derived metrics method available")
            
            return True
        else:
            print(f"   ⚠️  Data fetcher returned incomplete data")
            return False
            
    except Exception as e:
        print(f"   ❌ Data fetcher test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("  🧪 INVESTMENT ANALYSIS SYSTEM V2.0 - SYSTEM TEST")
    print("="*80)
    
    results = {
        'Environment': test_environment(),
        'Packages': test_packages(),
        'API Key': test_api_key(),
        'Gemini API': test_gemini_connection(),
        'Yahoo Finance': test_yfinance(),
        'News Search': test_news_search(),
        'DCF Engine': test_valuation_engine(),
        'Data Fetcher': test_data_fetcher()
    }
    
    # Summary
    print("\n" + "="*80)
    print("  📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n   Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   🎉 ALL TESTS PASSED! System is ready.")
        print("\n   Next step: python investment_agent_v2.py")
    elif passed >= total - 2:
        print("\n   ⚠️  MOSTLY WORKING - Optional features may be unavailable")
        print("   You can still run the analysis with reduced functionality")
    else:
        print("\n   ❌ CRITICAL ISSUES - Please fix errors above")
        print("   Most likely issues:")
        print("   - Missing packages: pip install -r requirements.txt")
        print("   - Missing API key: Add GOOGLE_API_KEY to .env file")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test suite crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
