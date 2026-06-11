"""Emerging Benchmark: Query-Document Semantic Consistency (QDSC)"""

from __future__ import annotations

from typing import List, Dict, Any, Optional


class QueryDocumentSemanticConsistency:
    """
    Measure: How semantically similar is the retrieved document to the query intent?
    Beyond: BM25/vector similarity - focuses on semantic alignment at concept level
    Importance: Catches cases where lexically similar docs are semantically irrelevant
    """

    def __init__(self, intent_extractor=None, embedder=None):
        """
        intent_extractor: optional LLM-based query intent parser
        embedder: optional embedding model for semantic similarity
        """
        self.intent_extractor = intent_extractor
        self.embedder = embedder

    async def evaluate(self, query_intent: str, retrieved_docs: list) -> float:
        """Evaluate semantic consistency between query intent and retrieved documents"""

        if not retrieved_docs:
            return 0.0

        intent = self._extract_intent(query_intent)

        if not intent:
            intent = query_intent

        scores = []

        for doc in retrieved_docs:
            doc_text = self._extract_text(doc)

            score = self._semantic_similarity(intent, doc_text)
            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.0

    def _extract_intent(self, query_intent: str) -> str:
        """
        Extract semantic intent using optional LLM extractor.
        """
        if self.intent_extractor:
            try:
                result = self.intent_extractor(query_intent)
                if hasattr(result, "__await__"):
                    return result.__await__()  # fallback-safe (rare)
                return str(result)
            except Exception:
                pass

        # fallback heuristic: assume intent = cleaned query
        return query_intent.strip().lower()

    def _semantic_similarity(self, a: str, b: str) -> float:
        """
        Embedding-based similarity with lexical fallback.
        """

        if self.embedder:
            try:
                va = self.embedder(a)
                vb = self.embedder(b)

                if va is None or vb is None:
                    return 0.0

                import numpy as np

                va = np.array(va)
                vb = np.array(vb)

                denom = (np.linalg.norm(va) * np.linalg.norm(vb)) + 1e-9

                return float(np.dot(va, vb) / denom)
            except Exception:
                pass

        # fallback lexical semantic proxy
        sa = set(a.lower().split())
        sb = set(b.lower().split())

        if not sa or not sb:
            return 0.0

        return len(sa & sb) / len(sa | sb)

    def _extract_text(self, doc: Any) -> str:
        if isinstance(doc, str):
            return doc
        if isinstance(doc, dict):
            return doc.get("content") or doc.get("text") or ""
        return str(doc)
