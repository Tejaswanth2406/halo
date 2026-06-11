"""Semantic deduplication"""

from __future__ import annotations

import numpy as np
from typing import List, Any, Callable, Optional


class SemanticDedup:
    """Remove semantically similar documents"""

    def __init__(self, embedding_fn: Optional[Callable[[Any], list]] = None):
        """
        embedding_fn: function(doc) -> embedding vector
        If not provided, expects doc["embedding"]
        """
        self.embedding_fn = embedding_fn

    def deduplicate(
        self,
        documents: list,
        threshold: float = 0.95,
    ) -> list:
        """Remove semantic duplicates"""

        if not documents:
            return []

        embeddings = self._get_embeddings(documents)
        embeddings = np.array(embeddings, dtype=np.float32)
        embeddings = self._normalize(embeddings)

        kept = []
        kept_embeddings = []

        for i, doc in enumerate(documents):
            emb = embeddings[i]

            if not kept:
                kept.append(doc)
                kept_embeddings.append(emb)
                continue

            max_sim = max(
                float(np.dot(emb, kept_emb))
                for kept_emb in kept_embeddings
            )

            if max_sim < threshold:
                kept.append(doc)
                kept_embeddings.append(emb)

        return kept

    def _get_embeddings(self, documents: list) -> list:
        embeddings = []

        for doc in documents:
            if self.embedding_fn:
                embeddings.append(self.embedding_fn(doc))
            elif isinstance(doc, dict) and "embedding" in doc:
                embeddings.append(doc["embedding"])
            else:
                raise ValueError(
                    "Missing embedding or embedding_fn"
                )

        return embeddings

    def _normalize(self, x: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return x / norms