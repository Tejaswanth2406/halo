"""CLIP image retriever"""

from __future__ import annotations

from typing import List, Any, Optional


class CLIPImageRetriever:
    """Retrieve images using CLIP embeddings"""

    def __init__(self, image_index, embedder):
        """
        image_index: storage with image embeddings
        embedder: function(text)->vector (CLIP text encoder)
        """
        self.image_index = image_index
        self.embedder = embedder

    async def retrieve(self, query: str, k: int = 10) -> list:
        """Retrieve similar images"""

        if not query or not query.strip():
            return []

        query_vec = self.embedder(query)

        if query_vec is None:
            return []

        results = await self._search(query_vec, k)

        scored = []

        for item in results:
            img_vec = item.get("embedding") or item.get("vector")

            if img_vec is None:
                continue

            score = self._cosine_similarity(query_vec, img_vec)

            scored.append((item, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [item for item, _ in scored[:k]]

    async def _search(self, query_vec, k: int):
        """
        Fetch candidate images from index.
        Assumes ANN index returns prefiltered candidates.
        """
        if hasattr(self.image_index, "search"):
            return await self.image_index.search(query_vec, k=k)

        if hasattr(self.image_index, "query"):
            return await self.image_index.query(query_vec, k=k)

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