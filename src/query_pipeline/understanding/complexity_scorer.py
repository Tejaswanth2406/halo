"""Query complexity scoring"""

from __future__ import annotations

import re
from typing import List


class ComplexityScorer:
    """Score query complexity"""

    def score(self, query: str) -> str:
        """Score complexity: simple, multi-hop, comparison"""

        if not query or not query.strip():
            return "simple"

        q = query.lower().strip()

        # simple heuristics
        multi_hop_signals = [
            "why", "how", "explain", "impact", "effect",
            "relationship", "cause", "depends", "steps",
        ]

        comparison_signals = [
            "vs", "versus", "compare", "difference",
            "better", "worse", "tradeoff",
        ]

        question_marks = q.count("?")

        token_count = len(re.findall(r"\w+", q))

        multi_hop_score = sum(
            1 for w in multi_hop_signals if w in q
        )

        comparison_score = sum(
            1 for w in comparison_signals if w in q
        )

        # classification logic
        if comparison_score > 0:
            return "comparison"

        if multi_hop_score >= 2 or token_count > 20 or question_marks > 1:
            return "multi-hop"

        if multi_hop_score == 1 and token_count > 12:
            return "multi-hop"

        return "simple"