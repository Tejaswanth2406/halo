"""Tavily live web search connector"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class TavilyConnector:
    """Connect to Tavily Search API for live retrieval"""

    def __init__(self, client):
        """
        client: Tavily API client or HTTP wrapper
        """
        self.client = client

    async def search(self, query: str, k: int = 10) -> list:
        """Search the web using Tavily"""

        if not query or not query.strip():
            return []

        response = await self._execute(query, k)

        results = response.get("results", []) if isinstance(response, dict) else []

        output = []

        for r in results:
            output.append(
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": r.get("content"),
                    "score": r.get("score"),
                    "published_date": r.get("published_date"),
                    "source": "tavily",
                }
            )

        return output[:k]

    async def _execute(self, query: str, k: int) -> dict:
        """
        Supports Tavily SDK or HTTP wrapper clients.
        """

        if hasattr(self.client, "search"):
            try:
                return await self.client.search(query=query, max_results=k)
            except TypeError:
                return self.client.search(query=query, max_results=k)

        if hasattr(self.client, "get"):
            return await self.client.get(
                "/search",
                params={"query": query, "max_results": k},
            )

        raise RuntimeError("Unsupported Tavily client")