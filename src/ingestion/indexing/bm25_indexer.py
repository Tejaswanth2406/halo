from __future__ import annotations

import json
import math
import pickle
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


class BM25Indexer:
    """
    BM25 Search Index

    Parameters:
        k1: term frequency saturation parameter
        b: document length normalization parameter
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

        self.documents: list[dict[str, Any]] = []

        self.doc_lengths: list[int] = []
        self.avg_doc_length: float = 0.0

        self.term_frequencies: list[Counter] = []
        self.document_frequencies: dict[str, int] = defaultdict(int)
        self.idf: dict[str, float] = {}

        self.total_documents: int = 0

    # --------------------------------------------------
    # TOKENIZATION
    # --------------------------------------------------

    def tokenize(self, text: str) -> list[str]:
        """
        Basic tokenizer.
        Replace with spaCy/NLTK in production.
        """

        if not text:
            return []

        return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    # --------------------------------------------------
    # INDEXING
    # --------------------------------------------------

    def index_documents(self, documents: list[dict[str, Any]]) -> None:
        """
        Index a batch of documents.

        Expected format:

        [
            {
                "id": "doc1",
                "title": "...",
                "text": "...",
                "metadata": {...}
            }
        ]
        """

        self.documents = documents
        self.term_frequencies.clear()
        self.document_frequencies.clear()
        self.doc_lengths.clear()
        self.idf.clear()

        total_length = 0

        for doc in documents:

            text = doc.get("text", "")

            tokens = self.tokenize(text)

            doc_length = len(tokens)

            self.doc_lengths.append(doc_length)

            total_length += doc_length

            tf = Counter(tokens)

            self.term_frequencies.append(tf)

            for term in tf.keys():
                self.document_frequencies[term] += 1

        self.total_documents = len(documents)

        if self.total_documents > 0:
            self.avg_doc_length = (
                total_length / self.total_documents
            )

        self._compute_idf()

    def add_document(self, document: dict[str, Any]) -> None:
        """
        Add single document and rebuild statistics.
        """

        self.documents.append(document)

        self.index_documents(self.documents)

    # --------------------------------------------------
    # IDF
    # --------------------------------------------------

    def _compute_idf(self) -> None:

        N = self.total_documents

        for term, df in self.document_frequencies.items():

            self.idf[term] = math.log(
                1 + ((N - df + 0.5) / (df + 0.5))
            )

    # --------------------------------------------------
    # BM25 SCORING
    # --------------------------------------------------

    def score_document(
        self,
        query: str,
        document_index: int,
    ) -> float:

        query_terms = self.tokenize(query)

        tf = self.term_frequencies[document_index]

        dl = self.doc_lengths[document_index]

        score = 0.0

        for term in query_terms:

            if term not in tf:
                continue

            term_frequency = tf[term]

            idf = self.idf.get(term, 0.0)

            numerator = (
                term_frequency
                * (self.k1 + 1)
            )

            denominator = (
                term_frequency
                + self.k1
                * (
                    1
                    - self.b
                    + self.b
                    * dl
                    / max(self.avg_doc_length, 1)
                )
            )

            score += idf * (numerator / denominator)

        return score

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[dict[str, Any]]:

        results = []

        for idx, doc in enumerate(self.documents):

            score = self.score_document(query, idx)

            if score < min_score:
                continue

            results.append(
                {
                    "score": round(score, 6),
                    "document": doc,
                }
            )

        results.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return results[:top_k]

    # --------------------------------------------------
    # DEBUG / STATS
    # --------------------------------------------------

    def get_statistics(self) -> dict:

        return {
            "documents": self.total_documents,
            "average_doc_length": round(
                self.avg_doc_length,
                2,
            ),
            "unique_terms": len(
                self.document_frequencies
            ),
        }

    # --------------------------------------------------
    # SAVE / LOAD
    # --------------------------------------------------

    def save(self, path: str) -> None:

        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> "BM25Indexer":

        with open(path, "rb") as f:
            return pickle.load(f)

    # --------------------------------------------------
    # EXPORT
    # --------------------------------------------------

    def export_json(self, path: str) -> None:

        data = {
            "documents": self.documents,
            "stats": self.get_statistics(),
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False,
            )


# ==================================================
# Example
# ==================================================

if __name__ == "__main__":

    documents = [
        {
            "id": "1",
            "title": "Python Programming",
            "text": (
                "Python is a popular programming "
                "language used for AI and web "
                "development."
            ),
        },
        {
            "id": "2",
            "title": "Machine Learning",
            "text": (
                "Machine learning relies heavily "
                "on Python libraries such as "
                "PyTorch and TensorFlow."
            ),
        },
        {
            "id": "3",
            "title": "Football",
            "text": (
                "Football is the most popular "
                "sport in many countries."
            ),
        },
    ]

    bm25 = BM25Indexer()

    bm25.index_documents(documents)

    print("Statistics:")
    print(bm25.get_statistics())

    print("\nSearch Results:")

    results = bm25.search(
        query="python ai",
        top_k=5,
    )

    for rank, result in enumerate(results, start=1):

        print(
            f"{rank}. "
            f"Score={result['score']:.4f} "
            f"DocID={result['document']['id']} "
            f"Title={result['document']['title']}"
        )

    bm25.save("bm25_index.pkl")