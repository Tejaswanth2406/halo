"""Elasticsearch keyword retriever"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class ElasticsearchRetriever:
    """Keyword-based retrieval using Elasticsearch"""

    def __init__(self, client, index: str):
        self.client = client
        self.index = index

    async def retrieve(self, query: str, k: int = 10) -> list:
        """Retrieve using Elasticsearch"""

        if not query:
            return []

        body = {
            "size": k,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content", "keywords^2"],
                    "type": "best_fields",
                }
            },
        }

        response = await self._search(body)

        hits = response.get("hits", {}).get("hits", [])

        results = []

        for h in hits:
            source = h.get("_source", {})
            results.append(
                {
                    "id": h.get("_id"),
                    "score": h.get("_score"),
                    "title": source.get("title"),
                    "content": source.get("content"),
                    "raw": source,
                }
            )

        return results[:k]

    async def _search(self, body: dict) -> dict:
        if hasattr(self.client, "search"):
            return await self.client.search(index=self.index, body=body)

        # fallback for sync clients
        return self.client.search(index=self.index, body=body)
