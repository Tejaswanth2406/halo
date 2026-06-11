"""Max Marginal Relevance for diversity"""

from __future__ import annotations

import numpy as np
from typing import List, Any, Callable, Optional


class MMR:
    """Select diverse documents using MMR"""

    def __init__(self, embedding_fn: Optional[Callable[[Any], list]] = None):
        """
        embedding_fn: function(doc) -> embedding vector
        If not provided, assumes documents already contain 'embedding'
        """
        self.embedding_fn = embedding_fn

    def select(
        self,
        documents: list,
        k: int,
        diversity_weight: float = 0.5,
    ) -> list:
        """Select diverse documents"""

        if not documents or k <= 0:
            return []

        if k >= len(documents):
            return documents

        embeddings = self._get_embeddings(documents)

        embeddings = np.array(embeddings, dtype=np.float32)
        embeddings = self._normalize(embeddings)

        selected = []
        selected_idx = set()

        # start with most "central" (highest norm similarity proxy)
        sim_matrix = embeddings @ embeddings.T
        scores = sim_matrix.sum(axis=1)
        first = int(np.argmax(scores))

        selected.append(first)
        selected_idx.add(first)

        while len(selected) < k:
            best_idx = None
            best_score = -1e9

            for i in range(len(documents)):
                if i in selected_idx:
                    continue

                relevance = float(
                    np.dot(embeddings[i], embeddings[first])
                )

                diversity = max(
                    np.dot(embeddings[i], embeddings[j])
                    for j in selected
                )

                mmr_score = (
                    (1 - diversity_weight) * relevance
                    - diversity_weight * diversity
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i

            if best_idx is None:
                break

            selected.append(best_idx)
            selected_idx.add(best_idx)

        return [documents[i] for i in selected]

    def _get_embeddings(self, documents: list) -> list:
        embeddings = []

        for doc in documents:
            if self.embedding_fn:
                embeddings.append(self.embedding_fn(doc))
            elif isinstance(doc, dict) and "embedding" in doc:
                embeddings.append(doc["embedding"])
            else:
                raise ValueError(
                    "No embedding function or embedding found in document"
                )

        return embeddings

    def _normalize(self, x: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return x / norms