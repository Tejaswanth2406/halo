"""Emerging Benchmark: Knowledge Cutoff Awareness (KCA)"""

from __future__ import annotations

from typing import List, Dict, Any, Optional


class KnowledgeCutoffAwareness:
    """
    Measure: Does the system correctly identify when it lacks knowledge?
    Importance: Prevents hallucinated answers by knowing knowledge boundaries
    Metric: Tests system's ability to distinguish in-scope vs out-of-scope queries
    """

    def __init__(self, response_model=None):
        """
        response_model: optional function(query)->response used to simulate system behavior
        """
        self.response_model = response_model

    async def evaluate(self, out_of_scope_queries: list) -> float:
        """Measure knowledge boundary awareness"""

        if not out_of_scope_queries:
            return 0.0

        correct_awareness = 0
        total = len(out_of_scope_queries)

        for item in out_of_scope_queries:
            query = item.get("query") if isinstance(item, dict) else item

            if not query:
                continue

            response = await self._generate(query)

            if self._shows_awareness(response):
                correct_awareness += 1

        return correct_awareness / total

    async def _generate(self, query: str) -> str:
        """
        Simulate system response or delegate to provided model.
        """
        if self.response_model:
            try:
                result = self.response_model(query)
                if hasattr(result, "__await__"):
                    return await result
                return result
            except Exception:
                return ""

        # fallback placeholder behavior
        return "I don't have enough information to answer that accurately."

    def _shows_awareness(self, response: str) -> bool:
        """
        Detect whether system correctly signals uncertainty instead of hallucinating.
        """

        if not response:
            return False

        r = response.lower()

        uncertainty_signals = [
            "don't know",
            "cannot determine",
            "not sure",
            "no information",
            "insufficient information",
            "outside my knowledge",
            "cannot answer",
        ]

        return any(sig in r for sig in uncertainty_signals)