"""Cross-encoder reranking"""

from __future__ import annotations

from typing import List, Any, Optional


class CrossEncoderReranker:
    """Stage 2: ms-marco-MiniLM cross-encoder reranking"""

    def __init__(
        self,
        model,
        batch_size: int = 32,
    ):
        """
        model: sentence-transformers CrossEncoder instance
        """
        self.model = model
        self.batch_size = batch_size

    async def rerank(
        self,
        query: str,
        documents: list,
        k: int = 10,
    ) -> list:
        """Rerank using cross-encoder"""

        if not query or not documents:
            return []

        pairs = [
            (query, self._get_text(doc))
            for doc in documents
        ]

        scores = self.model.predict(
            pairs,
            batch_size=self.batch_size,
        )

        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        return [doc for doc, _ in ranked[:k]]

    def _get_text(self, doc: Any) -> str:
        if isinstance(doc, dict):
            return str(doc.get("content", ""))
        return str(doc)
