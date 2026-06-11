"""Emerging Benchmark: Source Attribution Accuracy (SAA)"""

from __future__ import annotations

from typing import List, Dict, Any
import re


class SourceAttributionAccuracy:
    """
    Measure: How accurately does the system cite and attribute sources?
    Importance: Users need to verify claims and understand provenance
    Metric: Precision of citations + completeness of attribution
    """

    def __init__(self, embedder=None):
        """
        embedder: optional semantic similarity model for claim-source matching
        """
        self.embedder = embedder

    async def evaluate(self, response: str, citations: list, source_docs: list) -> float:
        """Evaluate citation accuracy and completeness"""

        if not response or not source_docs:
            return 0.0

        citations = citations or []

        cited_sources = self._normalize_citations(citations)
        doc_map = self._index_sources(source_docs)

        precision = self._citation_precision(cited_sources, doc_map, response)
        recall = self._citation_recall(cited_sources, doc_map, response)
        support = self._claim_support(response, doc_map)

        saa = (0.4 * precision) + (0.4 * recall) + (0.2 * support)

        return max(0.0, min(1.0, saa))

    def _normalize_citations(self, citations: list) -> list:
        """
        Normalize citation identifiers.
        """
        norm = []

        for c in citations:
            if isinstance(c, str):
                norm.append(c.strip().lower())
            elif isinstance(c, dict):
                norm.append(str(c.get("id") or c.get("source") or "").lower())

        return [c for c in norm if c]

    def _index_sources(self, source_docs: list) -> dict:
        """
        Map source IDs to content.
        """
        index = {}

        for i, doc in enumerate(source_docs):
            if isinstance(doc, dict):
                key = (
                    doc.get("id")
                    or doc.get("url")
                    or doc.get("title")
                    or f"doc_{i}"
                )
                content = doc.get("content") or doc.get("text") or ""
            else:
                key = f"doc_{i}"
                content = str(doc)

            index[str(key).lower()] = content

        return index

    def _citation_precision(self, citations: list, doc_map: dict, response: str) -> float:
        """
        Precision: cited sources actually exist and are relevant.
        """
        if not citations:
            return 0.0

        valid = 0

        for c in citations:
            if c in doc_map:
                if self._citation_supports_response(doc_map[c], response):
                    valid += 1

        return valid / len(citations)

    def _citation_recall(self, citations: list, doc_map: dict, response: str) -> float:
        """
        Recall: sources used in response are properly cited.
        """

        referenced = self._extract_inferred_sources(response)

        if not referenced:
            return 1.0 if not citations else 0.0

        cited_set = set(citations)
        return len(referenced & cited_set) / len(referenced)

    def _claim_support(self, response: str, doc_map: dict) -> float:
        """
        Estimate how well claims are supported by any source.
        """
        if not response or not doc_map:
            return 0.0

        sentences = re.split(r"[.!?]", response)

        supported = 0

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            if any(self._similar(sent, doc) > 0.3 for doc in doc_map.values()):
                supported += 1

        return supported / len(sentences) if sentences else 0.0

    def _citation_supports_response(self, doc: str, response: str) -> bool:
        return self._similar(doc, response) > 0.3

    def _extract_inferred_sources(self, response: str) -> set:
        """
        Extract citation-like tokens from response (e.g., [1], (source), etc.)
        """
        matches = re.findall(r"\[([^\]]+)\]", response)
        return set(m.lower() for m in matches)

    def _similar(self, a: str, b: str) -> float:
        """
        Semantic similarity via embedding or lexical overlap.
        """
        if self.embedder:
            try:
                va = self.embedder(a)
                vb = self.embedder(b)

                if va is None or vb is None:
                    return 0.0

                import numpy as np

                va = np.array(va)
                vb = np.array(vb)

                denom = (np.linalg.norm(va) * np.linalg.norm(vb)) + 1e-9

                return float(np.dot(va, vb) / denom)
            except Exception:
                pass

        sa = set(a.lower().split())
        sb = set(b.lower().split())

        if not sa or not sb:
            return 0.0

        return len(sa & sb) / len(sa | sb)