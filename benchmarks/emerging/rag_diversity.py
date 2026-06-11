"""Emerging Benchmark: Retrieval-Augmented Generation Diversity (RAGD)"""

from __future__ import annotations

from typing import List, Dict, Any
from collections import Counter


class RetrievalAugmentedGenerationDiversity:
    """
    Measure: Do responses leverage diverse sources or rely on single-source information?
    Importance: Ensures robust answers drawing from multiple perspectives
    Metric: Tracks unique source coverage and cross-source consistency
    """

    def __init__(self, embedder=None):
        """
        embedder: optional function(text)->vector for semantic clustering of sources
        """
        self.embedder = embedder

    async def evaluate(self, response: str, sources: list) -> float:
        """Calculate diversity of source utilization"""

        if not sources:
            return 0.0

        normalized_sources = self._normalize_sources(sources)

        if not normalized_sources:
            return 0.0

        uniqueness_score = self._source_uniqueness(normalized_sources)
        coverage_score = self._coverage_score(response, normalized_sources)
        redundancy_penalty = self._redundancy_penalty(normalized_sources)

        ragd = (
            0.5 * uniqueness_score +
            0.4 * coverage_score +
            0.1 * (1.0 - redundancy_penalty)
        )

        return max(0.0, min(1.0, ragd))

    def _normalize_sources(self, sources: list) -> list:
        """
        Extract comparable text representations of sources.
        """
        normalized = []

        for s in sources:
            if isinstance(s, str):
                normalized.append(s.lower().strip())
            elif isinstance(s, dict):
                normalized.append(
                    (
                        s.get("content")
                        or s.get("text")
                        or s.get("title")
                        or ""
                    ).lower().strip()
                )
            else:
                normalized.append(str(s).lower().strip())

        return [s for s in normalized if s]

    def _source_uniqueness(self, sources: list) -> float:
        """
        Ratio of unique sources.
        """
        if not sources:
            return 0.0

        unique = len(set(sources))
        return unique / len(sources)

    def _coverage_score(self, response: str, sources: list) -> float:
        """
        Estimate how many sources are actually reflected in response.
        Uses lexical overlap + lightweight semantic proxy.
        """
        if not response:
            return 0.0

        response_tokens = set(response.lower().split())

        matched = 0

        for src in sources:
            src_tokens = set(src.split())

            # overlap heuristic
            overlap = len(response_tokens & src_tokens) / (len(src_tokens) + 1e-9)

            if overlap > 0.2:
                matched += 1

        return matched / len(sources)

    def _redundancy_penalty(self, sources: list) -> float:
        """
        Penalize near-duplicate sources.
        """
        if len(sources) < 2:
            return 0.0

        counts = Counter(sources)
        max_freq = max(counts.values())

        return (max_freq - 1) / len(sources)