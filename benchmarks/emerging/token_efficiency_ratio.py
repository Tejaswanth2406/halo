"""Emerging Benchmark: Token Efficiency Ratio (TER)"""

from __future__ import annotations

from typing import Dict, Any


class TokenEfficiencyRatio:
    """
    Measure: Ratio of useful tokens to total tokens spent
    Formula: Answer_Tokens_Used / (Context_Tokens + Query_Tokens + Answer_Tokens)
    Importance: Cost optimization - less is more if quality maintained
    """

    def __init__(self, quality_weight: float = 0.3):
        """
        quality_weight: how strongly to reward high-quality outputs
        """
        self.quality_weight = quality_weight

    async def evaluate(self, tokens_used: dict, quality_score: float) -> float:
        """Calculate token efficiency with quality adjustment"""

        if not tokens_used:
            return 0.0

        answer_tokens = tokens_used.get("answer_tokens", 0)
        context_tokens = tokens_used.get("context_tokens", 0)
        query_tokens = tokens_used.get("query_tokens", 0)

        total_tokens = answer_tokens + context_tokens + query_tokens

        if total_tokens <= 0:
            return 0.0

        raw_ter = answer_tokens / total_tokens

        # quality-adjusted efficiency:
        # penalize low-quality answers even if token-efficient
        adjusted = raw_ter * (1.0 + self.quality_weight * (quality_score - 0.5))

        return max(0.0, min(1.0, adjusted))