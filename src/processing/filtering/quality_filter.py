"""Quality-based filtering"""

from __future__ import annotations

from typing import List, Any, Optional


class QualityFilter:
    """Filter by importance and quality score"""

    def __init__(
        self,
        score_field: str = "quality_score",
        fallback_score: float = 0.0,
    ):
        self.score_field = score_field
        self.fallback_score = fallback_score

    def filter(
        self,
        documents: list,
        min_quality_score: float = 0.5,
    ) -> list:
        """Filter by quality score"""

        if not documents:
            return []

        if min_quality_score < 0:
            raise ValueError("min_quality_score must be >= 0")

        filtered: List[Any] = []

        for doc in documents:
            score = self._extract_score(doc)

            if score >= min_quality_score:
                filtered.append(doc)

        # optional: sort high-quality first
        filtered.sort(
            key=lambda d: self._extract_score(d),
            reverse=True,
        )

        return filtered

    def _extract_score(self, doc: Any) -> float:
        """Extract quality score safely"""

        try:
            if isinstance(doc, dict):
                value = doc.get(self.score_field, self.fallback_score)
                return float(value)

            value = getattr(doc, self.score_field, self.fallback_score)
            return float(value)

        except Exception:
            return float(self.fallback_score)