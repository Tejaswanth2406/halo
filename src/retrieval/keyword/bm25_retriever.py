"""BM25 keyword retriever"""

from __future__ import annotations

from typing import List, Any, Dict, Optional
import math
import re
from collections import Counter


class BM25Retriever:
    """Keyword-based retrieval using BM25"""

    def __init__(self, corpus: Optional[list] = None, k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus or []
        self.k1 = k1
        self.b = b

        self.doc_tokens = [self._tokenize(d) for d in self.corpus]
        self.doc_freqs = [Counter(t) for t in self.doc_tokens]
        self.doc_lengths = [len(t) for t in self.doc_tokens]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0
        self.N = len(self.corpus)

        self.idf = self._build_idf()

    async def retrieve(self, query: str, k: int = 10) -> list:
        """Retrieve using BM25"""

        if not query or not self.corpus:
            return []

        q_tokens = self._tokenize(query)

        scores = []

        for i, doc_freq in enumerate(self.doc_freqs):
            score = self._score(q_tokens, doc_freq, self.doc_lengths[i])
            scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        return [self.corpus[i] for i, _ in scores[:k]]

    def _build_idf(self) -> Dict[str, float]:
        idf = {}

        for token in set(t for doc in self.doc_tokens for t in doc):
            df = sum(1 for doc in self.doc_tokens if token in doc)
            idf[token] = math.log(1 + (self.N - df + 0.5) / (df + 0.5))

        return idf

    def _score(self, query_tokens, doc_freq, doc_len) -> float:
        score = 0.0

        for q in query_tokens:
            if q not in doc_freq:
                continue

            tf = doc_freq[q]
            idf = self.idf.get(q, 0.0)

            denom = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl if self.avgdl else 1))

            score += idf * (tf * (self.k1 + 1)) / (denom + 1e-9)

        return score

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())