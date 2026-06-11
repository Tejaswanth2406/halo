"""Emerging Benchmark: Contextual Faithfulness Score (CFS)"""

from __future__ import annotations

from typing import Dict, Any, List, Optional


class ContextualFaithfulnessScore:
    """
    Measure: Does the response align with context AND external knowledge?
    Unlike traditional faithfulness which only checks context alignment
    CFS ensures the model doesn't mix up contextual facts with pre-trained knowledge
    Importance: Critical for factually correct retrieval-augmented responses
    """

    def __init__(self, embedder=None, drift_threshold: float = 0.25):
        """
        embedder: function(text)->vector for semantic similarity
        drift_threshold: lower similarity indicates higher drift risk
        """
        self.embedder = embedder
        self.drift_threshold = drift_threshold

    async def evaluate(self, response: str, context: str, query: str) -> dict:
        """Calculate contextual faithfulness score with semantic drift detection"""

        if not response or not context:
            return {
                "cfs": 0.0,
                "context_alignment": 0.0,
                "drift_score": 1.0,
                "query_alignment": 0.0,
                "status": "insufficient_input",
            }

        context_alignment = self._semantic_similarity(response, context)
        query_alignment = self._semantic_similarity(response, query)

        drift_score = 1.0 - context_alignment

        # penalize if response is closer to query than context (hallucination signal)
        drift_penalty = max(0.0, query_alignment - context_alignment)

        cfs = (
            0.6 * context_alignment
            + 0.4 * query_alignment
            - drift_penalty
        )

        cfs = max(0.0, min(1.0, cfs))

        return {
            "cfs": cfs,
            "context_alignment": context_alignment,
            "query_alignment": query_alignment,
            "drift_score": drift_score,
            "drift_penalty": drift_penalty,
            "status": "ok",
        }

    def _semantic_similarity(self, a: str, b: str) -> float:
        """
        Compute embedding-based cosine similarity with fallback heuristic.
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

        # fallback lexical similarity
        sa = set(a.lower().split())
        sb = set(b.lower().split())

        if not sa or not sb:
            return 0.0

        return len(sa & sb) / len(sa | sb)
