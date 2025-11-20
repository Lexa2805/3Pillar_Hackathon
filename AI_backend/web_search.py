"""
Web search utilities for agents to gather real-time information
Uses Tavily API for intelligent web search
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("Warning: tavily-python not installed. Run: pip install tavily-python")

load_dotenv()


def search_web(query: str, max_results: int = 5, search_depth: str = "advanced", include_domains: List[str] = None) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        search_depth: "basic" or "advanced" (advanced uses more credits but better quality)
        include_domains: Optional list of domains to prioritize (e.g., ["github.com", "stackoverflow.com"])
    
    Returns:
        List of search results with title, snippet, and link
    """
    # Reload env vars to ensure we have the latest config
    load_dotenv(override=True)
    enable_web_search = os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true"
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    if not enable_web_search:
        print("⚠️ Web search is disabled (ENABLE_WEB_SEARCH=false in .env)")
        return []
    
    if not TAVILY_AVAILABLE or not tavily_api_key:
        print("❌ Tavily API not available. Check your TAVILY_API_KEY in .env")
        return []
    
    print(f"\n🌐 WEB SEARCH QUERY: '{query}'")
    print(f"📊 Search depth: {search_depth} | Max results: {max_results}")
    if include_domains:
        print(f"🎯 Prioritizing domains: {', '.join(include_domains)}")
    
    try:
        print("🔍 Using Tavily Search API...")
        tavily = TavilyClient(api_key=tavily_api_key)
        
        search_params = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": False,  # We want raw results, not AI summary
        }
        
        if include_domains:
            search_params["include_domains"] = include_domains
        
        response = tavily.search(**search_params)
        results = []
        
        for i, result in enumerate(response.get("results", []), 1):
            results.append({
                "title": result.get("title", ""),
                "snippet": result.get("content", ""),
                "link": result.get("url", ""),
                "score": result.get("score", 0),  # Tavily relevance score
            })
            print(f"  ✓ Result {i}: {result.get('title', 'No title')[:60]}...")
            print(f"     URL: {result.get('url', '')[:80]}")
            print(f"     Score: {result.get('score', 0):.2f}")
        
        print(f"✅ Tavily returned {len(results)} high-quality results\n")
        return results
    except Exception as e:
        print(f"❌ Error during Tavily search: {e}")
        return []


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results into a readable string for the LLM.
    
    Args:
        results: List of search results
    
    Returns:
        Formatted string with search results
    """
    if not results:
        return "No web search results available."
    
    formatted = "Web Search Results:\n\n"
    for i, result in enumerate(results, 1):
        formatted += f"{i}. {result['title']}\n"
        formatted += f"   {result['snippet']}\n"
        formatted += f"   Source: {result['link']}\n\n"
    
    return formatted


def search_for_context(query: str, max_results: int = 3, search_depth: str = "advanced", include_domains: List[str] = None) -> str:
    """
    Search web and return formatted results as context.
    Convenience function that combines search and formatting.
    
    Args:
        query: Search query
        max_results: Number of results to fetch
        search_depth: "basic" or "advanced"
        include_domains: Optional list of domains to prioritize
    
    Returns:
        Formatted search results string
    """
    print(f"🔎 Searching for context: '{query[:80]}...'")
    results = search_web(query, max_results, search_depth, include_domains)
    formatted = format_search_results(results)
    print(f"📝 Formatted {len(results)} results for LLM context")
    return formatted


def enhance_prompt_with_search(user_prompt: str, search_query: str = None, include_domains: List[str] = None) -> str:
    """
    Enhance a user prompt with web search results.
    
    Args:
        user_prompt: Original user prompt
        search_query: Optional custom search query (defaults to user_prompt)
        include_domains: Optional list of domains to prioritize
    
    Returns:
        Enhanced prompt with search context
    """
    if not is_web_search_enabled():
        return user_prompt
    
    query = search_query or user_prompt
    search_context = search_for_context(query, max_results=3, search_depth="advanced", include_domains=include_domains)
    
    enhanced_prompt = f"""User Request: {user_prompt}

{search_context}

Based on the user's request and the web search results above, provide well-informed ideas."""
    
    return enhanced_prompt


def is_web_search_enabled() -> bool:
    """Check if web search is enabled and available."""
    # Reload env vars to ensure we have the latest config
    load_dotenv(override=True)
    enable_web_search = os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true"
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    return enable_web_search and TAVILY_AVAILABLE and tavily_api_key is not None
