"""Emerging Benchmark: Query-Document Temporal Alignment (QDTA)"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class QueryDocumentTemporalAlignment:
    """
    Measure: Are retrieved documents temporally appropriate for the query?
    Importance: Queries about 'current events' should use recent docs
    Metric: Temporal freshness vs query temporal context
    """

    def __init__(self, freshness_scorer=None):
        """
        freshness_scorer: optional function(doc)->0..1 freshness score
        """
        self.freshness_scorer = freshness_scorer

    async def evaluate(self, query: str, retrieved_docs: list) -> float:
        """Evaluate temporal alignment of retrieval"""

        if not retrieved_docs:
            return 0.0

        query_time_hint = self._extract_temporal_intent(query)

        scores = []

        for doc in retrieved_docs:
            doc_freshness = self._get_doc_freshness(doc)

            alignment = self._score_alignment(query_time_hint, doc_freshness)
            scores.append(alignment)

        return sum(scores) / len(scores) if scores else 0.0

    def _extract_temporal_intent(self, query: str) -> str:
        """
        Detect whether query expects:
        - recent (now, today, latest)
        - bounded past (2023, last year)
        - historical/agnostic
        """

        q = query.lower()

        recent_signals = ["now", "today", "latest", "current", "breaking", "this week"]
        past_signals = ["2023", "2022", "last year", "in 2020", "historical"]

        if any(s in q for s in recent_signals):
            return "recent"

        if any(s in q for s in past_signals):
            return "bounded_past"

        return "agnostic"

    def _get_doc_freshness(self, doc: Any) -> float:
        """
        Compute document freshness score [0..1].
        """

        if self.freshness_scorer:
            try:
                return float(self.freshness_scorer.score(doc))
            except Exception:
                pass

        ts = self._extract_timestamp(doc)

        if ts is None:
            return 0.5

        now = datetime.now(timezone.utc)
        age_days = (now - ts).total_seconds() / 86400.0

        # exponential decay (30-day half-life approx)
        return max(0.0, min(1.0, 2.71828 ** (-age_days / 30.0)))

    def _score_alignment(self, query_time_hint: str, doc_freshness: float) -> float:
        """
        Align query temporal intent with document freshness.
        """

        if query_time_hint == "recent":
            return doc_freshness

        if query_time_hint == "bounded_past":
            # moderate freshness preferred
            return 1.0 - abs(doc_freshness - 0.5) * 2

        # agnostic queries tolerate all
        return 0.7 + (0.3 * doc_freshness)

    def _extract_timestamp(self, doc: Any):
        """
        Extract timestamp from document metadata.
        """

        ts_str = None

        if isinstance(doc, dict):
            ts_str = (
                doc.get("created_at")
                or doc.get("updated_at")
                or doc.get("timestamp")
                or doc.get("date")
                or doc.get("published_date")
            )

        if not ts_str:
            return None

        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            return None
