"""Emerging Benchmark: Retriever Disagreement Index (RDI)"""

from __future__ import annotations

from typing import List, Dict, Any
import itertools


class RetrieverDisagreementIndex:
    """
    Measure: How much do different retrievers disagree on relevance ranking?
    Importance: High disagreement → uncertain retrieval → risky fusion
    Framework: Detects when ensemble retrievers are fundamentally misaligned
    """

    def __init__(self):
        pass

    async def evaluate(self, query: str, retrievers: list) -> float:
        """Measure retriever consensus/disagreement"""

        if not query or not retrievers or len(retrievers) < 2:
            return 0.0

        rankings = []

        for r in retrievers:
            docs = await self._run_retriever(r, query)
            rankings.append(self._extract_ranking(docs))

        correlations = []

        for a, b in itertools.combinations(rankings, 2):
            correlations.append(self._spearman(a, b))

        if not correlations:
            return 0.0

        avg_corr = sum(correlations) / len(correlations)

        # RDI = disagreement = 1 - agreement
        return max(0.0, min(1.0, 1.0 - avg_corr))

    async def _run_retriever(self, retriever, query: str) -> list:
        """
        Execute retriever safely.
        """
        try:
            if hasattr(retriever, "retrieve"):
                result = retriever.retrieve(query)
                if hasattr(result, "__await__"):
                    return await result
                return result
        except Exception:
            return []

        return []

    def _extract_ranking(self, docs: list) -> list:
        """
        Convert docs into ranked IDs or hashes.
        """
        ranking = []

        for i, d in enumerate(docs):
            if isinstance(d, dict):
                ranking.append(d.get("id") or d.get("url") or str(d))
            else:
                ranking.append(str(d))

        return ranking

    def _spearman(self, a: list, b: list) -> float:
        """
        Lightweight Spearman approximation using rank overlap.
        Returns correlation in [-1, 1].
        """

        if not a or not b:
            return 0.0

        # align on common items
        common = set(a) & set(b)

        if len(common) < 2:
            return 0.0

        def ranks(lst):
            return {item: i for i, item in enumerate(lst)}

        ra = ranks(a)
        rb = ranks(b)

        diffs = []
        for item in common:
            diffs.append((ra[item] - rb[item]) ** 2)

        n = len(common)
        denom = n * (n**2 - 1) + 1e-9

        spearman = 1 - (6 * sum(diffs) / denom)

        return max(-1.0, min(1.0, spearman))
