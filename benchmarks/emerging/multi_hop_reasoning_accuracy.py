"""Emerging Benchmark: Multi-Hop Reasoning Accuracy (MHRA)"""

from __future__ import annotations

from typing import List, Dict, Any, Optional


class MultiHopReasoningAccuracy:
    """
    Measure: Can the system correctly answer questions requiring multi-step reasoning?
    Addresses: Multi-hop QA challenges where intermediate steps must be correct
    Importance: Tests agent's ability to decompose and chain retrieval calls
    """

    def __init__(self, reasoning_model=None):
        """
        reasoning_model: optional function(query)->list of inferred steps
        """
        self.reasoning_model = reasoning_model

    async def evaluate(self, query: str, expected_reasoning_path: list) -> float:
        """Evaluate multi-hop reasoning accuracy"""

        if not query or not expected_reasoning_path:
            return 0.0

        predicted_path = await self._generate_reasoning(query)

        if not predicted_path:
            return 0.0

        return self._score_paths(predicted_path, expected_reasoning_path)

    async def _generate_reasoning(self, query: str) -> list:
        """
        Generate reasoning path using provided model or fallback heuristic.
        """
        if self.reasoning_model:
            try:
                result = self.reasoning_model(query)
                if hasattr(result, "__await__"):
                    return await result
                return result
            except Exception:
                return []

        # fallback: naive decomposition
        return query.split("?") if "?" in query else query.split()

    def _score_paths(self, predicted: list, expected: list) -> float:
        """
        Compute partial-credit score for multi-hop reasoning:
        - exact match steps get full credit
        - partial semantic overlap gives partial credit
        """

        if not predicted or not expected:
            return 0.0

        expected_set = [str(e).lower().strip() for e in expected]
        predicted_set = [str(p).lower().strip() for p in predicted]

        total_credit = 0.0

        for i, exp in enumerate(expected_set):
            if i < len(predicted_set):
                pred = predicted_set[i]

                if pred == exp:
                    total_credit += 1.0
                elif exp in pred or pred in exp:
                    total_credit += 0.5
                else:
                    # token overlap fallback
                    exp_tokens = set(exp.split())
                    pred_tokens = set(pred.split())

                    if exp_tokens:
                        overlap = len(exp_tokens & pred_tokens) / len(exp_tokens)
                        total_credit += overlap

        return total_credit / len(expected_set)
