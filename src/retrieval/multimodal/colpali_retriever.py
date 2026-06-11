"""ColPali image retriever for document images"""

from __future__ import annotations

from typing import List, Any, Optional


class ColPaliRetriever:
    """Retrieve document images using ColPali"""

    def __init__(self, index, embedder):
        """
        index: document image index (pages / figures / chunks)
        embedder: ColPali text->multimodal embedding function
        """
        self.index = index
        self.embedder = embedder

    async def retrieve(self, query: str, k: int = 10) -> list:
        """Retrieve document images"""

        if not query or not query.strip():
            return []

        query_vec = self.embedder(query)

        if query_vec is None:
            return []

        candidates = await self._fetch_candidates(query_vec, k)

        scored = []

        for c in candidates:
            vec = c.get("embedding") or c.get("vector")

            if vec is None:
                continue

            score = self._cosine_similarity(query_vec, vec)

            scored.append((c, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [item for item, _ in scored[:k]]

    async def _fetch_candidates(self, query_vec, k: int):
        """
        Retrieve candidate document images from index.
        """
        if hasattr(self.index, "search"):
            return await self.index.search(query_vec, k=k)

        if hasattr(self.index, "query"):
            return await self.index.query(query_vec, k=k)

        return []

    def _cosine_similarity(self, a, b) -> float:
        try:
            import numpy as np

            a = np.array(a)
            b = np.array(b)

            denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9

            return float(np.dot(a, b) / denom)
        except Exception:
            return 0.0