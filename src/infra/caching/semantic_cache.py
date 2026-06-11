"""Semantic cache for similar queries"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np


class SemanticCache:
    """Cache by query similarity"""

    def __init__(
        self,
        embedding_model,
        max_entries: int = 100_000,
    ):
        self.embedding_model = embedding_model
        self.max_entries = max_entries

        self._entries: List[Dict[str, Any]] = []

    async def get_similar(
        self,
        query: str,
        threshold: float = 0.95,
    ) -> Any:
        """Get semantically similar cached result"""

        if not query:
            return None

        if not self._entries:
            return None

        query_embedding = np.asarray(
            await self.embedding_model.embed(query),
            dtype=np.float32,
        )

        query_embedding /= (
            np.linalg.norm(query_embedding) + 1e-12
        )

        best_score = -1.0
        best_result = None

        for entry in self._entries:
            score = float(
                np.dot(
                    query_embedding,
                    entry["embedding"],
                )
            )

            if score > best_score:
                best_score = score
                best_result = entry["result"]

        return (
            best_result
            if best_score >= threshold
            else None
        )

    async def put(
        self,
        query: str,
        result: Any,
    ) -> None:
        """Store query/result pair"""

        embedding = np.asarray(
            await self.embedding_model.embed(query),
            dtype=np.float32,
        )

        embedding /= (
            np.linalg.norm(embedding) + 1e-12
        )

        if len(self._entries) >= self.max_entries:
            self._entries.pop(0)

        self._entries.append(
            {
                "query": query,
                "embedding": embedding,
                "result": result,
            }
        )