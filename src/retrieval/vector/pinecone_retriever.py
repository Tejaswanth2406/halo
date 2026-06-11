"""Pinecone vector retriever"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class PineconeRetriever:
    """Vector retrieval using Pinecone managed service"""

    def __init__(self, index, namespace: Optional[str] = None):
        """
        index: Pinecone index client
        namespace: optional namespace for isolation
        """
        self.index = index
        self.namespace = namespace

    async def retrieve(self, query_embedding: list, k: int = 10) -> list:
        """Retrieve from Pinecone"""

        if not query_embedding:
            return []

        response = await self._query(query_embedding, k)

        matches = response.get("matches", []) if isinstance(response, dict) else []

        results = []

        for m in matches:
            results.append(
                {
                    "id": m.get("id"),
                    "score": m.get("score"),
                    "values": m.get("values"),
                    "metadata": m.get("metadata", {}),
                    "source": "pinecone",
                }
            )

        return results[:k]

    async def _query(self, query_embedding: list, k: int) -> dict:
        """
        Supports async/sync Pinecone clients.
        """

        params = {
            "vector": query_embedding,
            "top_k": k,
            "include_metadata": True,
        }

        if self.namespace:
            params["namespace"] = self.namespace

        if hasattr(self.index, "query"):
            try:
                return await self.index.query(**params)
            except TypeError:
                return self.index.query(**params)

        raise RuntimeError("Unsupported Pinecone index client")