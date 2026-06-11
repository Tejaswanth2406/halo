"""BM25 pre-filter for reranking"""

from __future__ import annotations

from typing import List, Any, Optional
import math
import re
from collections import Counter


class BM25Prefilter:
    """Stage 1: cheap BM25 scoring filter"""

    def __init__(
        self,
        text_field: str = "content",
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.text_field = text_field
        self.k1 = k1
        self.b = b

    def filter(
        self,
        documents: list,
        k: int = 50,
    ) -> list:
        """Filter using BM25 scores"""

        if not documents:
            return []

        if k <= 0:
            return []

        tokenized_docs = [
            self._tokenize(self._get_text(doc))
            for doc in documents
        ]

        doc_lengths = [len(doc) for doc in tokenized_docs]
        avgdl = sum(doc_lengths) / len(doc_lengths)

        # compute document frequencies
        df = Counter()
        for doc in tokenized_docs:
            for term in set(doc):
                df[term] += 1

        N = len(documents)

        scores = []

        for idx, doc in enumerate(tokenized_docs):
            score = 0.0
            doc_len = len(doc)
            term_freq = Counter(doc)

            for term, freq in term_freq.items():
                idf = math.log(
                    (N - df[term] + 0.5)
                    / (df[term] + 0.5)
                    + 1
                )

                tf = freq * (self.k1 + 1)
                denom = freq + self.k1 * (
                    1
                    - self.b
                    + self.b * (doc_len / (avgdl + 1e-9))
                )

                score += idf * (tf / denom)

            scores.append((score, idx))

        scores.sort(reverse=True, key=lambda x: x[0])

        top_indices = [idx for _, idx in scores[:k]]

        return [documents[i] for i in top_indices]

    def _get_text(self, doc: Any) -> str:
        if isinstance(doc, dict):
            return str(doc.get(self.text_field, ""))
        return str(doc)

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())