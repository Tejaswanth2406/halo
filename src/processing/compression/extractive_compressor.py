"""Extractive compression"""

from __future__ import annotations

import re
from typing import List, Dict, Any
from collections import Counter


class ExtractiveCompressor:
    """Extract most relevant sentences"""

    def __init__(self):
        self._sentence_splitter = re.compile(r"(?<=[.!?])\s+")

    def compress(
        self,
        documents: list,
        max_tokens: int = 2000,
    ) -> str:
        """Extract relevant sentences"""

        if not documents:
            return ""

        sentences = self._extract_sentences(documents)

        if not sentences:
            return ""

        scored = self._score_sentences(sentences)

        selected = []
        token_count = 0

        for sentence, score, tokens in scored:
            if token_count + tokens > max_tokens:
                continue

            selected.append(sentence)
            token_count += tokens

            if token_count >= max_tokens:
                break

        return " ".join(selected)

    def _extract_sentences(self, documents: list) -> List[str]:
        sentences = []

        for doc in documents:
            text = str(doc)
            parts = self._sentence_splitter.split(text)
            sentences.extend([p.strip() for p in parts if p.strip()])

        return sentences

    def _score_sentences(self, sentences: List[str]) -> List[tuple]:
        """Simple frequency-based importance scoring"""

        words = []
        sentence_tokens = []

        for s in sentences:
            tokens = re.findall(r"\w+", s.lower())
            sentence_tokens.append(tokens)
            words.extend(tokens)

        freq = Counter(words)

        scored = []

        for sentence, tokens in zip(sentences, sentence_tokens):
            score = sum(freq[t] for t in tokens)
            scored.append(
                (
                    sentence,
                    score,
                    len(tokens),
                )
            )

        scored.sort(key=lambda x: x[1], reverse=True)

        return scored