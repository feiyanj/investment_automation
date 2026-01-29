"""
Test Script for MODULE 2: Business Understanding
Tests business analysis and key events extraction
"""
from data.fetcher_v3 import DataFetcherV3
from agents.business_analyst import BusinessAnalyst


def test_module_2():
    """Test MODULE 2 deliverables"""
    print("="*80)
    print("MODULE 2 TEST: Business Understanding")
    print("="*80)
    
    ticker = "NFLX"  # Netflix as per the guide
    
    print(f"\n🧪 Testing business understanding for {ticker}...")
    
    # Step 1: Fetch comprehensive data
    print("\n[Step 1] Fetching comprehensive data...")
    fetcher = DataFetcherV3(ticker)
    data = fetcher.fetch_all_data()
    
    # Step 2: Format data for business analyst
    print("\n[Step 2] Formatting data for LLM...")
    formatted_data = fetcher.format_for_llm()
    
    company_info = {
        'name': data['company_info'].get('name', 'Unknown'),
        'ticker': ticker,
        'sector': data['company_info'].get('sector', 'N/A'),
        'industry': data['company_info'].get('industry', 'N/A')
    }
    
    # Step 3: Initialize business analyst
    print("\n[Step 3] Initializing business analyst...")
    analyst = BusinessAnalyst()
    
    # Step 4: Analyze business
    print("\n[Step 4] Running business analysis...")
    business_understanding, key_events, formatted_context = analyst.get_full_context(
        formatted_data,
        company_info,
        data.get('news', [])
    )
    
    print("\n" + "="*80)
    print("VALIDATION CHECKS:")
    print("="*80)
    
    # Test 1: Business understanding length
    print("\n1. Checking business understanding...")
    assert len(business_understanding) > 500, f"❌ Too short: {len(business_understanding)} chars"
    print(f"   ✅ Business analysis: {len(business_understanding):,} characters")
    
    # Check for key sections
    keywords = ['business', 'revenue', 'competitive', 'growth', 'quality']
    found_keywords = sum(1 for kw in keywords if kw.lower() in business_understanding.lower())
    assert found_keywords >= 4, f"❌ Missing key sections, found {found_keywords}/5 keywords"
    print(f"   ✅ Contains key sections ({found_keywords}/5 keywords found)")
    
    # Test 2: Key events extraction
    print("\n2. Checking key events...")
    assert len(key_events) > 100, f"❌ Too short: {len(key_events)} chars"
    print(f"   ✅ Key events: {len(key_events):,} characters")
    
    # Check for dates and impact markers
    has_dates = '[202' in key_events  # Look for date format
    has_impact = any(marker in key_events.upper() for marker in ['POSITIVE', 'NEGATIVE', 'MIXED', 'NEUTRAL'])
    
    if has_dates:
        print(f"   ✅ Contains dated events")
    else:
        print(f"   ⚠️  No dated events found (may be no material events)")
    
    if has_impact:
        print(f"   ✅ Contains impact assessments")
    else:
        print(f"   ⚠️  No impact assessments found")
    
    # Test 3: Formatted context
    print("\n3. Checking formatted context...")
    assert len(formatted_context) > 1000, f"❌ Too short: {len(formatted_context)} chars"
    print(f"   ✅ Formatted context: {len(formatted_context):,} characters")
    
    assert "BUSINESS CONTEXT" in formatted_context, "❌ Missing header"
    assert "BUSINESS UNDERSTANDING" in formatted_context, "❌ Missing business section"
    assert "KEY RECENT EVENTS" in formatted_context, "❌ Missing events section"
    print(f"   ✅ All required sections present")
    
    print("\n" + "="*80)
    print("✅ MODULE 2 TEST PASSED!")
    print("="*80)
    
    # Display outputs
    print("\n" + "="*80)
    print("📊 BUSINESS UNDERSTANDING (first 1000 chars):")
    print("="*80)
    print(business_understanding[:1000])
    print("...\n")
    
    print("="*80)
    print("📰 KEY EVENTS (first 800 chars):")
    print("="*80)
    print(key_events[:800])
    print("...\n")
    
    print("="*80)
    print("📝 OUTPUT STATISTICS:")
    print("="*80)
    print(f"Business Understanding: {len(business_understanding):,} chars")
    print(f"Key Events: {len(key_events):,} chars")
    print(f"Formatted Context: {len(formatted_context):,} chars")
    print(f"Total: {len(business_understanding) + len(key_events) + len(formatted_context):,} chars")
    
    return {
        'business_understanding': business_understanding,
        'key_events': key_events,
        'formatted_context': formatted_context
    }


if __name__ == "__main__":
    try:
        result = test_module_2()
        print("\n✅ All tests passed! MODULE 2 is complete.")
        print("\n🎯 Ready for MODULE 3: Value Hunter Rewrite")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
