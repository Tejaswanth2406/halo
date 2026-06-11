"""Freshness-based filtering"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Any, Optional


class FreshnessFilter:
    """Filter documents by freshness"""

    def __init__(self, timestamp_field: str = "timestamp"):
        self.timestamp_field = timestamp_field

    def filter(
        self,
        documents: list,
        max_age_days: int = 30,
    ) -> list:
        """Filter by document age"""

        if not documents:
            return []

        now = datetime.now(timezone.utc)

        filtered: List[Any] = []

        for doc in documents:
            ts = self._extract_timestamp(doc)

            if ts is None:
                continue

            age_days = (now - ts).total_seconds() / 86400

            if age_days <= max_age_days:
                filtered.append(doc)

        return filtered

    def _extract_timestamp(self, doc: Any) -> Optional[datetime]:
        """Extract timestamp from document"""

        try:
            if isinstance(doc, dict):
                value = doc.get(self.timestamp_field)

                if isinstance(value, datetime):
                    return value

                if isinstance(value, str):
                    return datetime.fromisoformat(
                        value.replace("Z", "+00:00")
                    )

            return None

        except Exception:
            return None