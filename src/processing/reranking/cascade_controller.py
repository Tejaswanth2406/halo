"""Cascade reranker controller"""

from __future__ import annotations

from typing import List, Any


class CascadeController:
    """Decide reranking escalation level"""

    def __init__(
        self,
        low_threshold: float = 0.3,
        high_threshold: float = 0.7,
        max_level: int = 3,
    ):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.max_level = max_level

    def decide_escalation(
        self,
        documents: list,
        scores: list,
    ) -> int:
        """Decide reranking level"""

        if not documents or not scores:
            return 0

        if len(documents) != len(scores):
            raise ValueError("documents and scores mismatch")

        if len(scores) == 0:
            return 0

        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)

        score_spread = max_score - min_score

        if avg_score >= self.high_threshold and score_spread < 0.1:
            return 0  # no rerank needed

        if avg_score >= self.low_threshold:
            return 1  # light rerank

        if avg_score < self.low_threshold and score_spread < 0.2:
            return 2  # moderate rerank

        return min(self.max_level, 3)