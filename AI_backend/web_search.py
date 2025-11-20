"""
Web search utilities for agents to gather real-time information
Uses DuckDuckGo for free web search without API keys
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    print("Warning: duckduckgo-search not installed. Web search will be disabled.")

load_dotenv()

ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true"


def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
    
    Returns:
        List of search results with title, snippet, and link
    """
    if not ENABLE_WEB_SEARCH or not WEB_SEARCH_AVAILABLE:
        return []
    
    try:
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("body", ""),
                    "link": result.get("href", ""),
                })
            return results
    except Exception as e:
        print(f"Error during web search: {e}")
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


def search_for_context(query: str, max_results: int = 3) -> str:
    """
    Search web and return formatted results as context.
    Convenience function that combines search and formatting.
    
    Args:
        query: Search query
        max_results: Number of results to fetch
    
    Returns:
        Formatted search results string
    """
    results = search_web(query, max_results)
    return format_search_results(results)


def enhance_prompt_with_search(user_prompt: str, search_query: str = None) -> str:
    """
    Enhance a user prompt with web search results.
    
    Args:
        user_prompt: Original user prompt
        search_query: Optional custom search query (defaults to user_prompt)
    
    Returns:
        Enhanced prompt with search context
    """
    if not ENABLE_WEB_SEARCH or not WEB_SEARCH_AVAILABLE:
        return user_prompt
    
    query = search_query or user_prompt
    search_context = search_for_context(query, max_results=3)
    
    enhanced_prompt = f"""User Request: {user_prompt}

{search_context}

Based on the user's request and the web search results above, provide well-informed ideas."""
    
    return enhanced_prompt


def search_news(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for news articles using DuckDuckGo News.
    
    Args:
        query: Search query
        max_results: Maximum number of results
    
    Returns:
        List of news results
    """
    if not ENABLE_WEB_SEARCH or not WEB_SEARCH_AVAILABLE:
        return []
    
    try:
        with DDGS() as ddgs:
            results = []
            for result in ddgs.news(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("body", ""),
                    "link": result.get("url", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", "")
                })
            return results
    except Exception as e:
        print(f"Error during news search: {e}")
        return []


def is_web_search_enabled() -> bool:
    """Check if web search is enabled and available."""
    return ENABLE_WEB_SEARCH and WEB_SEARCH_AVAILABLE
