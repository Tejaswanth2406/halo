"""Qdrant vector retriever for production"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class QdrantRetriever:
    """Vector retrieval using Qdrant"""

    def __init__(self, client, collection_name: str):
        """
        client: Qdrant client instance
        collection_name: target collection
        """
        self.client = client
        self.collection_name = collection_name

    async def retrieve(self, query_embedding: list, k: int = 10) -> list:
        """Retrieve from Qdrant"""

        if not query_embedding:
            return []

        response = await self._query(query_embedding, k)

        # Qdrant responses typically contain "result"
        points = response.get("result") if isinstance(response, dict) else None

        if not points:
            return []

        results = []

        for p in points:
            payload = getattr(p, "payload", None) or p.get("payload", {})
            vector = getattr(p, "vector", None) or p.get("vector")

            results.append(
                {
                    "id": getattr(p, "id", None) or p.get("id"),
                    "score": getattr(p, "score", None) or p.get("score"),
                    "payload": payload,
                    "vector": vector,
                    "source": "qdrant",
                }
            )

        return results[:k]

    async def _query(self, query_embedding: list, k: int) -> dict:
        """
        Supports both async and sync Qdrant clients.
        """

        search_params = {
            "collection_name": self.collection_name,
            "query_vector": query_embedding,
            "limit": k,
            "with_payload": True,
            "with_vectors": False,
        }

        if hasattr(self.client, "search"):
            try:
                return await self.client.search(**search_params)
            except TypeError:
                return self.client.search(**search_params)

        raise RuntimeError("Unsupported Qdrant client")