"""Chroma vector retriever for development"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class ChromaRetriever:
    """Vector retrieval using Chroma"""

    def __init__(self, collection):
        """
        collection: Chroma collection instance
        """
        self.collection = collection

    async def retrieve(self, query_embedding: list, k: int = 10) -> list:
        """Retrieve from Chroma"""

        if not query_embedding:
            return []

        results = await self._query_chroma(query_embedding, k)

        if not results:
            return []

        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        ids = results.get("ids") or []
        distances = results.get("distances") or []

        output = []

        for i in range(len(documents)):
            output.append(
                {
                    "id": ids[i] if i < len(ids) else None,
                    "document": documents[i],
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "distance": distances[i] if i < len(distances) else None,
                    "source": "chroma",
                }
            )

        return output[:k]

    async def _query_chroma(self, query_embedding: list, k: int) -> dict:
        """
        Supports both async wrappers and sync Chroma client.
        """

        if hasattr(self.collection, "query"):
            try:
                return await self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    include=["documents", "metadatas", "distances", "ids"],
                )
            except TypeError:
                return self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    include=["documents", "metadatas", "distances", "ids"],
                )

        raise RuntimeError("Unsupported Chroma collection client")