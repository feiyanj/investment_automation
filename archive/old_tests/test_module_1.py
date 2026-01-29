"""
Test Script for MODULE 1: Enhanced Data Collection
Tests the new DataFetcherV3 with comprehensive 5-year data
"""
from data.fetcher_v3 import DataFetcherV3


def test_module_1():
    """Test MODULE 1 deliverables"""
    print("="*80)
    print("MODULE 1 TEST: Enhanced Data Collection")
    print("="*80)
    
    ticker = "NFLX"  # Netflix as per the guide
    
    print(f"\n🧪 Testing with {ticker}...")
    
    # Initialize fetcher
    fetcher = DataFetcherV3(ticker)
    
    # Fetch all data
    data = fetcher.fetch_all_data()
    
    print("\n" + "="*80)
    print("VALIDATION CHECKS:")
    print("="*80)
    
    # Test 1: 5-year financial statements
    print("\n1. Checking 5-year financial statements...")
    income_5y = data.get('income_5y', [])
    balance_5y = data.get('balance_5y', [])
    cashflow_5y = data.get('cashflow_5y', [])
    
    assert len(income_5y) >= 3, f"❌ Expected at least 3 years of income data, got {len(income_5y)}"
    print(f"   ✅ Income statements: {len(income_5y)} years")
    
    assert len(balance_5y) >= 3, f"❌ Expected at least 3 years of balance sheet data, got {len(balance_5y)}"
    print(f"   ✅ Balance sheets: {len(balance_5y)} years")
    
    assert len(cashflow_5y) >= 3, f"❌ Expected at least 3 years of cash flow data, got {len(cashflow_5y)}"
    print(f"   ✅ Cash flows: {len(cashflow_5y)} years")
    
    # Test 2: Quality indicators
    print("\n2. Checking quality indicators...")
    quality = data.get('quality_indicators', {})
    
    assert 'red_flags' in quality, "❌ red_flags not found"
    print(f"   ✅ Red flags detected: {quality.get('red_flag_count', 0)}")
    
    assert 'fcf_to_ni_ratio' in quality, "❌ fcf_to_ni_ratio not found"
    print(f"   ✅ FCF/NI ratio: {quality.get('fcf_to_ni_ratio', 0):.2f}")
    
    assert 'goodwill_pct' in quality, "❌ goodwill_pct not found"
    print(f"   ✅ Goodwill %: {quality.get('goodwill_pct', 0):.1f}%")
    
    # Test 3: Comprehensive metrics
    print("\n3. Checking 5-year metrics...")
    metrics = data.get('metrics_5y', {})
    
    assert 'growth_rates' in metrics, "❌ growth_rates not found"
    growth = metrics['growth_rates']
    print(f"   ✅ Revenue CAGR: {growth.get('revenue_cagr', 0)*100:.1f}%")
    print(f"   ✅ Earnings CAGR: {growth.get('earnings_cagr', 0)*100:.1f}%")
    print(f"   ✅ FCF CAGR: {growth.get('fcf_cagr', 0)*100:.1f}%")
    
    assert 'profitability' in metrics, "❌ profitability not found"
    profit = metrics['profitability']
    print(f"   ✅ Avg Gross Margin: {profit.get('avg_gross_margin', 0):.1f}%")
    print(f"   ✅ Avg Operating Margin: {profit.get('avg_operating_margin', 0):.1f}%")
    
    assert 'returns' in metrics, "❌ returns not found"
    returns = metrics['returns']
    print(f"   ✅ Avg ROE: {returns.get('avg_roe', 0):.1f}%")
    print(f"   ✅ Avg ROIC: {returns.get('avg_roic', 0):.1f}%")
    
    # Test 4: News deduplication
    print("\n4. Checking news collection...")
    news = data.get('news', [])
    
    assert len(news) >= 10, f"❌ Expected at least 10 news articles, got {len(news)}"
    print(f"   ✅ News articles collected: {len(news)}")
    print(f"   ✅ First article: {news[0]['title'][:60]}...")
    
    # Test 5: LLM formatting
    print("\n5. Checking LLM formatting...")
    formatted = fetcher.format_for_llm()
    
    assert len(formatted) > 5000, f"❌ Formatted output too short: {len(formatted)} chars"
    print(f"   ✅ Formatted output: {len(formatted):,} characters")
    
    assert "COMPREHENSIVE FINANCIAL DATA" in formatted, "❌ Missing header"
    assert "QUALITY INDICATORS & RED FLAGS" in formatted, "❌ Missing quality section"
    assert "KEY METRICS & TRENDS" in formatted, "❌ Missing metrics section"
    print(f"   ✅ All sections present")
    
    print("\n" + "="*80)
    print("✅ MODULE 1 TEST PASSED!")
    print("="*80)
    
    # Show sample of formatted output
    print("\n📄 SAMPLE OF FORMATTED OUTPUT (first 2000 chars):")
    print("="*80)
    print(formatted[:2000])
    print("...")
    print("="*80)
    
    # Show red flags if any
    if quality.get('red_flag_count', 0) > 0:
        print("\n🚩 RED FLAGS DETECTED:")
        print("="*80)
        for flag in quality['red_flags']:
            print(f"[{flag['severity']}] {flag['category']}: {flag['flag']}")
            print(f"    → {flag['detail']}\n")
    
    return data


if __name__ == "__main__":
    try:
        data = test_module_1()
        print("\n✅ All tests passed! MODULE 1 is complete.")
        print("\n📊 Data collection summary:")
        print(f"   - Financial years: {len(data.get('income_5y', []))}")
        print(f"   - Red flags: {data.get('quality_indicators', {}).get('red_flag_count', 0)}")
        print(f"   - News articles: {len(data.get('news', []))}")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
