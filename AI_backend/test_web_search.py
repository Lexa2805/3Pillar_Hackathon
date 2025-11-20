"""
Quick test to verify web search functionality
"""
import sys
sys.path.append('.')

from web_search import search_web, format_search_results, is_web_search_enabled

def test_web_search():
    print("=" * 60)
    print("🔍 Testing Web Search Functionality")
    print("=" * 60)
    
    # Check if enabled
    print(f"\n✓ Web search enabled: {is_web_search_enabled()}")
    
    if not is_web_search_enabled():
        print("\n⚠️  Web search is disabled.")
        print("To enable, set ENABLE_WEB_SEARCH=true in .env file")
        return
    
    # Test search
    print("\n📊 Testing Tavily search...")
    query = "AI trends in healthcare 2025"
    print(f"   Query: '{query}'")
    print("   Fetching results...")
    
    results = search_web(query, max_results=3)
    
    if results:
        print(f"\n✅ Found {len(results)} results!\n")
        formatted = format_search_results(results)
        print(formatted)
    else:
        print("\n❌ No results found")
        print("   This might be due to rate limiting or network issues")
    
    print("\n" + "=" * 60)
    print("✓ Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_web_search()
