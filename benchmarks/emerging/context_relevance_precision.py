"""Emerging Benchmark: Context Relevance Precision (CRP)"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class ContextRelevancePrecision:
    """
    Measure: What fraction of retrieved context is relevant?
    Complements: Recall (which measures what fraction of relevant docs were retrieved)
    Importance: Reduces context noise and token waste
    """

    def __init__(self, relevance_scorer=None, threshold: float = 0.5):
        """
        relevance_scorer: optional function(query, doc) -> score
        threshold: minimum score to consider a document relevant
        """
        self.relevance_scorer = relevance_scorer
        self.threshold = threshold

    async def evaluate(self, retrieved_docs: list, query: str) -> float:
        """Calculate context relevance precision"""

        if not retrieved_docs:
            return 0.0

        relevant = 0
        total = len(retrieved_docs)

        for doc in retrieved_docs:
            score = self._score_relevance(query, doc)

            if score >= self.threshold:
                relevant += 1

        return relevant / total

    def _score_relevance(self, query: str, doc: Any) -> float:
        """
        Compute relevance score using:
        - external scorer (preferred)
        - fallback heuristic overlap scoring
        """

        if self.relevance_scorer:
            try:
                return float(self.relevance_scorer(query, doc))
            except Exception:
                pass

        text = self._extract_text(doc).lower()
        q_terms = set(query.lower().split())

        if not q_terms:
            return 0.0

        doc_terms = set(text.split())

        overlap = len(q_terms.intersection(doc_terms))
        return overlap / len(q_terms)

    def _extract_text(self, doc: Any) -> str:
        """
        Normalize different document formats into text.
        """

        if isinstance(doc, str):
            return doc

        if isinstance(doc, dict):
            return (
                doc.get("content")
                or doc.get("text")
                or doc.get("document")
                or ""
            )

        return str(doc)
