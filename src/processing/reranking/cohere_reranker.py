"""Cohere reranker"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class CohereReranker:
    """Stage 3: Cohere reranker API"""

    def __init__(
        self,
        api_key: str,
        model: str = "rerank-3.5",
        timeout_seconds: float = 10.0,
    ):
        import cohere

        self.client = cohere.Client(api_key)
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def rerank(
        self,
        query: str,
        documents: list,
        k: int = 10,
    ) -> list:
        """Rerank using Cohere API"""

        if not query:
            return []

        if not documents:
            return []

        texts = [self._get_text(doc) for doc in documents]

        response = self.client.rerank(
            model=self.model,
            query=query,
            documents=texts,
            top_n=min(k, len(texts)),
        )

        ranked_indices = [
            r.index for r in response.results
        ]

        return [documents[i] for i in ranked_indices]

    def _get_text(self, doc: Any) -> str:
        if isinstance(doc, dict):
            return str(doc.get("content", ""))
        return str(doc)
