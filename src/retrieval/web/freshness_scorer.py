"""Freshness scorer for search results"""

from __future__ import annotations

from typing import Dict, Any
from datetime import datetime, timezone


class FreshnessScorer:
    """Score results by freshness"""

    def __init__(self, decay_days: float = 30.0):
        self.decay_days = decay_days

    def score(self, result: dict) -> float:
        """Score freshness of result"""

        if not result:
            return 0.0

        ts = self._extract_timestamp(result)

        if ts is None:
            return 0.5  # unknown freshness baseline

        now = datetime.now(timezone.utc)
        age_days = (now - ts).total_seconds() / 86400.0

        # exponential decay
        score = 2.71828 ** (-age_days / self.decay_days)

        # clamp
        return max(0.0, min(1.0, score))

    def _extract_timestamp(self, result: dict):
        """
        Try common timestamp fields:
        - created_at
        - updated_at
        - timestamp
        - date
        """

        ts_str = (
            result.get("created_at")
            or result.get("updated_at")
            or result.get("timestamp")
            or result.get("date")
        )

        if not ts_str:
            return None

        try:
            # ISO-8601 parsing
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            return None