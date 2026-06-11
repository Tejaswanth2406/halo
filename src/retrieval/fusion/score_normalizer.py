"""Score normalizer for fusion"""

from __future__ import annotations

from typing import List


class ScoreNormalizer:
    """Normalize scores from different retrievers"""

    def normalize(self, scores: list) -> list:
        """Min-max normalize scores"""

        if not scores:
            return []

        # ensure numeric stability
        values = [float(s) for s in scores]

        min_s = min(values)
        max_s = max(values)

        if max_s == min_s:
            return [1.0 for _ in values]

        return [
            (s - min_s) / (max_s - min_s)
            for s in values
        ]