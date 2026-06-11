"""Emerging Benchmark: Cross-Lingual Retrieval Effectiveness (CLRE)"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from collections import defaultdict


class CrossLingualRetrievalEffectiveness:
    """
    Measure: Quality of retrieval and response in multilingual scenarios
    Addresses: Query in one language, documents in multiple languages
    Importance: Global RAG systems need multilingual competence
    """

    def __init__(self, retriever=None, embedder=None, language_detector=None):
        """
        retriever: function(query)->list of docs
        embedder: multilingual embedding model
        language_detector: optional language detection function
        """
        self.retriever = retriever
        self.embedder = embedder
        self.language_detector = language_detector

    async def evaluate(
        self,
        queries_by_language: dict,
        multilingual_corpus: list,
    ) -> dict:
        """Evaluate cross-lingual retrieval effectiveness"""

        if not queries_by_language:
            return {"clre": 0.0, "details": {}}

        per_language_scores = {}
        pair_scores = defaultdict(list)

        for lang, queries in queries_by_language.items():
            if not isinstance(queries, list):
                queries = [queries]

            scores = []

            for q in queries:
                retrieved = await self._retrieve(q)

                score = self._score_retrieval(q, retrieved, multilingual_corpus)

                scores.append(score)

                detected_lang = self._detect_language(q)
                pair_scores[(lang, detected_lang)].append(score)

            per_language_scores[lang] = sum(scores) / len(scores) if scores else 0.0

        # aggregate score
        all_scores = [v for v in per_language_scores.values() if v is not None]
        clre = sum(all_scores) / len(all_scores) if all_scores else 0.0

        return {
            "clre": clre,
            "per_language": per_language_scores,
            "language_pair_scores": {
                str(k): sum(v) / len(v) for k, v in pair_scores.items() if v
            },
        }

    async def _retrieve(self, query: str) -> list:
        if not self.retriever:
            return []

        try:
            result = self.retriever.retrieve(query)
            if hasattr(result, "__await__"):
                return await result
            return result
        except Exception:
            return []

    def _score_retrieval(self, query: str, retrieved: list, corpus: list) -> float:
        """
        Heuristic multilingual relevance scoring:
        overlap + embedding similarity (if available)
        """

        if not retrieved:
            return 0.0

        q_tokens = set(query.lower().split())

        total = 0.0

        for doc in retrieved:
            text = self._extract_text(doc).lower()
            d_tokens = set(text.split())

            lexical = len(q_tokens & d_tokens) / (len(q_tokens) + 1e-9)

            semantic = self._semantic_similarity(query, text)

            total += 0.5 * lexical + 0.5 * semantic

        return total / len(retrieved)

    def _semantic_similarity(self, a: str, b: str) -> float:
        if not self.embedder:
            return 0.0

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
            return 0.0

    def _extract_text(self, doc: Any) -> str:
        if isinstance(doc, str):
            return doc
        if isinstance(doc, dict):
            return doc.get("content") or doc.get("text") or ""
        return str(doc)

    def _detect_language(self, text: str) -> str:
        if self.language_detector:
            try:
                return self.language_detector.detect(text)
            except Exception:
                pass

        # naive fallback
        if any("\u0b00" <= c <= "\u0b7f" for c in text):  # Telugu range
            return "te"
        if any("\u0900" <= c <= "\u097f" for c in text):  # Hindi range
            return "hi"

        return "unknown"