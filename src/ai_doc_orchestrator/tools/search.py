"""Search tool using Tavily or Google Search."""

import os
from typing import Any, Dict, List, Optional

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None


class SearchTool:
    """Tool for searching the web using Tavily or Google Search."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "tavily"):
        """Initialize the search tool.

        Args:
            api_key: API key for the search provider
            provider: Either 'tavily' or 'google'
        """
        self.provider = provider
        self.api_key = api_key or os.getenv("TAVILY_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if provider == "tavily":
            if TavilyClient is None:
                raise ImportError(
                    "tavily-python is required. Install with: pip install tavily-python"
                )
            if not self.api_key:
                raise ValueError("TAVILY_API_KEY environment variable is required")
            self.client = TavilyClient(api_key=self.api_key)
        elif provider == "google":
            # For Google Search, we'd use Custom Search API
            # This is a placeholder - actual implementation would use google-api-python-client
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required")
            self.client = None
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for information.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of search results with content and metadata
        """
        if self.provider == "tavily":
            return self._search_tavily(query, max_results)
        elif self.provider == "google":
            return self._search_google(query, max_results)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Tavily.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        response = self.client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
        )

        results = []
        for result in response.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
            })

        return results

    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        # Placeholder implementation
        # In production, this would use google-api-python-client
        # For now, return empty results with a note
        return [
            {
                "title": "Google Search",
                "url": f"https://www.google.com/search?q={query}",
                "content": f"Google search results for: {query}",
                "score": 1.0,
                "note": "Google Search API integration needs to be configured",
            }
        ]

