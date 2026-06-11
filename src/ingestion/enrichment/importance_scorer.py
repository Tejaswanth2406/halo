from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Any


@dataclass
class ScoreBreakdown:
    quality: float
    authority: float
    freshness: float
    popularity: float
    trust: float
    final_score: float


class ImportanceScorer:
    """
    Score document importance and authority.

    Expected document format:

    {
        "url": "https://example.com/article",
        "title": "...",
        "text": "...",
        "author": "...",
        "published_at": "2025-01-15T10:00:00Z",
        "backlinks": 120,
        "citations": 15,
        "views": 5000,
        "shares": 250,
        "spam_score": 0.05
    }
    """

    TRUSTED_DOMAINS = {
        "nature.com": 100,
        "science.org": 100,
        "nih.gov": 100,
        "arxiv.org": 90,
        "wikipedia.org": 85,
        "reuters.com": 90,
        "bbc.com": 85,
        "who.int": 95,
        "gov": 95,
        "edu": 90,
    }

    def score(self, doc: dict[str, Any]) -> float:
        """Return final score (0-100)."""

        quality = self._quality_score(doc)
        authority = self._authority_score(doc)
        freshness = self._freshness_score(doc)
        popularity = self._popularity_score(doc)
        trust = self._trust_score(doc)

        final_score = (
            0.30 * quality +
            0.30 * authority +
            0.15 * freshness +
            0.15 * popularity +
            0.10 * trust
        )

        return round(min(max(final_score, 0), 100), 2)

    def score_with_breakdown(self, doc: dict[str, Any]) -> ScoreBreakdown:
        quality = self._quality_score(doc)
        authority = self._authority_score(doc)
        freshness = self._freshness_score(doc)
        popularity = self._popularity_score(doc)
        trust = self._trust_score(doc)

        final_score = (
            0.30 * quality +
            0.30 * authority +
            0.15 * freshness +
            0.15 * popularity +
            0.10 * trust
        )

        return ScoreBreakdown(
            quality=round(quality, 2),
            authority=round(authority, 2),
            freshness=round(freshness, 2),
            popularity=round(popularity, 2),
            trust=round(trust, 2),
            final_score=round(final_score, 2),
        )

    # --------------------------------------------------
    # QUALITY
    # --------------------------------------------------

    def _quality_score(self, doc: dict[str, Any]) -> float:
        score = 0.0

        text = doc.get("text", "")
        title = doc.get("title", "")

        word_count = len(text.split())

        # content length
        score += min(word_count / 20, 40)

        # title exists
        if title:
            score += 10

        # author exists
        if doc.get("author"):
            score += 10

        # structured metadata
        if doc.get("published_at"):
            score += 10

        # long-form content bonus
        if word_count > 1000:
            score += 15

        if word_count > 2000:
            score += 15

        return min(score, 100)

    # --------------------------------------------------
    # AUTHORITY
    # --------------------------------------------------

    def _authority_score(self, doc: dict[str, Any]) -> float:
        score = 0.0

        backlinks = float(doc.get("backlinks", 0))
        citations = float(doc.get("citations", 0))

        score += min(backlinks * 0.2, 50)
        score += min(citations * 1.5, 50)

        return min(score, 100)

    # --------------------------------------------------
    # FRESHNESS
    # --------------------------------------------------

    def _freshness_score(self, doc: dict[str, Any]) -> float:
        published_at = doc.get("published_at")

        if not published_at:
            return 30

        try:
            published = self._parse_date(published_at)
        except Exception:
            return 30

        now = datetime.now(timezone.utc)

        age_days = (now - published).days

        if age_days <= 1:
            return 100

        if age_days <= 7:
            return 90

        if age_days <= 30:
            return 80

        if age_days <= 90:
            return 70

        if age_days <= 365:
            return 50

        return 20

    # --------------------------------------------------
    # POPULARITY
    # --------------------------------------------------

    def _popularity_score(self, doc: dict[str, Any]) -> float:
        views = float(doc.get("views", 0))
        shares = float(doc.get("shares", 0))

        score = 0.0

        score += min(views / 1000, 50)
        score += min(shares / 10, 50)

        return min(score, 100)

    # --------------------------------------------------
    # TRUST
    # --------------------------------------------------

    def _trust_score(self, doc: dict[str, Any]) -> float:
        url = doc.get("url", "")
        spam_score = float(doc.get("spam_score", 0))

        domain_score = self._domain_trust(url)

        spam_penalty = spam_score * 50

        trust = domain_score - spam_penalty

        return max(0, min(trust, 100))

    def _domain_trust(self, url: str) -> float:
        if not url:
            return 50

        domain = urlparse(url).netloc.lower()

        for trusted_domain, score in self.TRUSTED_DOMAINS.items():

            if trusted_domain in domain:
                return score

            if domain.endswith("." + trusted_domain):
                return score

        return 50

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def _parse_date(self, value: str) -> datetime:
        value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)


if __name__ == "__main__":

    doc = {
        "url": "https://arxiv.org/abs/2501.12345",
        "title": "Large Language Models for OCR",
        "author": "Research Team",
        "text": "word " * 1800,
        "published_at": "2025-12-01T10:00:00Z",
        "backlinks": 350,
        "citations": 40,
        "views": 25000,
        "shares": 1200,
        "spam_score": 0.01,
    }

    scorer = ImportanceScorer()

    print("Score:", scorer.score(doc))
    print()
    print(scorer.score_with_breakdown(doc))