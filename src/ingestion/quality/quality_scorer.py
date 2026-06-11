"""
Document quality scoring.
"""

import re


class QualityScorer:
    """Score document quality."""

    def score(self, text: str) -> float:
        """
        Return quality score between 0 and 1.
        """

        if not text:
            return 0.0

        text = text.strip()

        # Minimum length check
        if len(text) < 50:
            return 0.2

        words = text.split()

        if not words:
            return 0.0

        # Alphabetic character ratio
        alpha_chars = sum(
            c.isalpha()
            for c in text
        )

        alpha_ratio = (
            alpha_chars / len(text)
        )

        # Word count
        word_count = len(words)

        # Garbage token detection
        garbage_tokens = len(
            re.findall(
                r"[A-Za-z0-9]{15,}",
                text
            )
        )

        garbage_penalty = min(
            garbage_tokens * 0.1,
            0.5
        )

        score = (
            0.5 * alpha_ratio
            +
            0.5 * min(
                word_count / 100,
                1.0
            )
        )

        score -= garbage_penalty

        return max(
            0.0,
            min(score, 1.0)
        )