"""
Production-grade auto-tagging using Anthropic Claude.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import anthropic

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class ContentType(str, Enum):
    ARTICLE = "article"
    RESEARCH_PAPER = "research_paper"
    BLOG_POST = "blog_post"
    NEWS = "news"
    TUTORIAL = "tutorial"
    DOCUMENTATION = "documentation"
    LEGAL = "legal"
    FINANCIAL = "financial"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    TRANSCRIPT = "transcript"
    OTHER = "other"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class TaggerConfig:
    """Runtime configuration for the auto-tagger."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 1024
    # Taxonomy control
    max_topics: int = 8                     # max topic tags to return
    min_confidence: float = 0.5             # drop tags below this threshold (0–1)
    allowed_content_types: Optional[list[ContentType]] = None  # None = all
    custom_taxonomy: Optional[list[str]] = None  # constrain topics to this list
    # Feature flags
    extract_entities: bool = True           # people, orgs, locations
    extract_keywords: bool = True           # key terms/phrases
    detect_language: bool = True
    detect_sentiment: bool = True
    generate_summary: bool = True
    summary_max_words: int = 60
    # Truncation — LLM context guard
    max_content_chars: int = 12_000


@dataclass
class Entity:
    text: str
    entity_type: str    # PERSON | ORG | LOCATION | PRODUCT | EVENT | OTHER
    confidence: float


@dataclass
class Tag:
    label: str
    confidence: float   # 0.0 – 1.0
    category: str       # "topic" | "keyword" | "content_type" | "sentiment" etc.


@dataclass
class TagResult:
    """Complete structured output of a single tagging run."""
    # Core taxonomy
    content_type: ContentType
    content_type_confidence: float
    topics: list[Tag]
    keywords: list[str]
    sentiment: Optional[Sentiment]
    sentiment_confidence: Optional[float]
    # Enrichment
    entities: list[Entity]
    language: Optional[str]         # ISO 639-1 e.g. "en"
    summary: Optional[str]
    # Convenience flat list
    all_tags: list[str]             # labels from topics + content_type
    # Meta
    model_used: str
    processing_time_ms: float
    input_chars: int
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return bool(self.topics or self.content_type)

    def to_dict(self) -> dict:
        return {
            "content_type": self.content_type.value,
            "content_type_confidence": self.content_type_confidence,
            "topics": [
                {"label": t.label, "confidence": t.confidence}
                for t in self.topics
            ],
            "keywords": self.keywords,
            "sentiment": self.sentiment.value if self.sentiment else None,
            "sentiment_confidence": self.sentiment_confidence,
            "entities": [
                {"text": e.text, "type": e.entity_type, "confidence": e.confidence}
                for e in self.entities
            ],
            "language": self.language,
            "summary": self.summary,
            "all_tags": self.all_tags,
            "model_used": self.model_used,
            "processing_time_ms": self.processing_time_ms,
            "input_chars": self.input_chars,
            "warnings": self.warnings,
            "success": self.success,
        }


# ---------------------------------------------------------------------------
# Core tagger
# ---------------------------------------------------------------------------

class AutoTagger:
    """
    Production-ready auto-tagger powered by Anthropic Claude.

    Features
    --------
    - Content-type classification with confidence score.
    - Topic tagging with per-tag confidence; optional custom taxonomy.
    - Named entity extraction (people, orgs, locations, products).
    - Keyword extraction.
    - Sentiment detection.
    - Language detection.
    - Concise summary generation.
    - Configurable confidence threshold to filter low-quality tags.
    - Input truncation guard to stay within LLM context limits.
    - Batch tagging with a single client instance.

    Usage
    -----
    >>> tagger = AutoTagger()
    >>> result = tagger.tag("OpenAI released GPT-5 today...")
    >>> print(result.topics)
    >>> print(result.to_dict())

    >>> cfg = TaggerConfig(
    ...     custom_taxonomy=["AI", "Finance", "Health", "Politics"],
    ...     extract_entities=True,
    ...     min_confidence=0.6,
    ... )
    >>> tagger = AutoTagger(config=cfg)
    >>> results = tagger.tag_batch([doc1, doc2, doc3])
    """

    def __init__(
        self,
        config: Optional[TaggerConfig] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.config = config or TaggerConfig()
        self._client = anthropic.Anthropic(
            **({"api_key": api_key} if api_key else {})
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tag(self, content: str, context: Optional[str] = None) -> TagResult:
        """
        Generate metadata tags for *content*.

        Parameters
        ----------
        content:
            The text to tag. Truncated to `config.max_content_chars` if longer.
        context:
            Optional hint about the content source or domain
            (e.g. "financial news article") to improve accuracy.

        Returns
        -------
        TagResult
        """
        if not content or not content.strip():
            return self._empty_result(0, time.perf_counter(), ["Empty content provided."])

        start = time.perf_counter()
        warnings: list[str] = []
        cfg = self.config

        # Truncate if necessary
        text = content.strip()
        if len(text) > cfg.max_content_chars:
            text = text[: cfg.max_content_chars]
            warnings.append(
                f"Content truncated from {len(content)} to {cfg.max_content_chars} chars."
            )

        prompt = self._build_prompt(text, context)

        try:
            response = self._client.messages.create(
                model=cfg.model,
                max_tokens=cfg.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text
        except anthropic.APIError as exc:
            logger.error("Anthropic API error: %s", exc)
            warnings.append(f"API error: {exc}")
            return self._empty_result(len(text), start, warnings)

        parsed = self._parse_response(raw_text, warnings)
        result = self._build_result(parsed, len(text), start, warnings)

        logger.debug(
            "Tagged %d chars: type=%s topics=%d entities=%d ms=%.0f",
            len(text),
            result.content_type.value,
            len(result.topics),
            len(result.entities),
            result.processing_time_ms,
        )
        return result

    def tag_batch(
        self,
        contents: list[str],
        contexts: Optional[list[Optional[str]]] = None,
    ) -> list[TagResult]:
        """Tag multiple content strings, reusing the same client."""
        contexts = contexts or [None] * len(contents)
        return [self.tag(c, ctx) for c, ctx in zip(contents, contexts)]

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_prompt(self, text: str, context: Optional[str]) -> str:
        cfg = self.config

        taxonomy_note = ""
        if cfg.custom_taxonomy:
            taxonomy_note = (
                f"\nTOPIC TAXONOMY (only use labels from this list): "
                f"{', '.join(cfg.custom_taxonomy)}"
            )

        ct_note = ""
        if cfg.allowed_content_types:
            ct_note = (
                f"\nALLOWED CONTENT TYPES: "
                f"{', '.join(t.value for t in cfg.allowed_content_types)}"
            )

        context_note = f"\nCONTEXT: {context}" if context else ""

        optional_fields = []
        if cfg.extract_entities:
            optional_fields.append(
                '"entities": [{"text": str, "entity_type": "PERSON|ORG|LOCATION|PRODUCT|EVENT|OTHER", "confidence": float}]'
            )
        if cfg.extract_keywords:
            optional_fields.append('"keywords": [str]')
        if cfg.detect_language:
            optional_fields.append('"language": str  // ISO 639-1 code e.g. "en"')
        if cfg.detect_sentiment:
            optional_fields.append(
                '"sentiment": "positive|negative|neutral|mixed", "sentiment_confidence": float'
            )
        if cfg.generate_summary:
            optional_fields.append(
                f'"summary": str  // ≤{cfg.summary_max_words} words, plain prose'
            )

        optional_block = (",\n  " + ",\n  ".join(optional_fields)) if optional_fields else ""

        return f"""You are a precise document metadata extractor. Analyse the content below and respond ONLY with a valid JSON object — no preamble, no markdown fences.

JSON schema:
{{
  "content_type": str,          // one of: {', '.join(t.value for t in ContentType)}
  "content_type_confidence": float,  // 0.0–1.0
  "topics": [
    {{"label": str, "confidence": float}}  // up to {cfg.max_topics} topics, confidence 0.0–1.0
  ]{optional_block}
}}{taxonomy_note}{ct_note}{context_note}

CONTENT:
{text}"""

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_response(self, raw: str, warnings: list[str]) -> dict:
        text = raw.strip()
        # Strip accidental markdown fences
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip().rstrip("```").strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            warnings.append(f"JSON parse error ({exc}); returning empty result.")
            logger.warning("Failed to parse LLM response: %s\nRaw: %s", exc, raw[:300])
            return {}

    # ------------------------------------------------------------------
    # Result assembly
    # ------------------------------------------------------------------

    def _build_result(
        self, data: dict, input_chars: int, start: float, warnings: list[str]
    ) -> TagResult:
        cfg = self.config

        # Content type
        raw_ct = data.get("content_type", "other")
        try:
            content_type = ContentType(raw_ct)
        except ValueError:
            content_type = ContentType.OTHER
            warnings.append(f"Unknown content_type '{raw_ct}'; defaulted to 'other'.")
        ct_conf = float(data.get("content_type_confidence", 0.0))

        # Topics — filter by min confidence
        raw_topics = data.get("topics", [])
        topics = []
        for t in raw_topics:
            conf = float(t.get("confidence", 0.0))
            if conf >= cfg.min_confidence:
                topics.append(Tag(
                    label=t.get("label", ""),
                    confidence=conf,
                    category="topic",
                ))
        topics.sort(key=lambda x: x.confidence, reverse=True)
        topics = topics[: cfg.max_topics]

        # Keywords
        keywords: list[str] = data.get("keywords", []) if cfg.extract_keywords else []

        # Sentiment
        sentiment: Optional[Sentiment] = None
        sentiment_conf: Optional[float] = None
        if cfg.detect_sentiment and "sentiment" in data:
            try:
                sentiment = Sentiment(data["sentiment"])
                sentiment_conf = float(data.get("sentiment_confidence", 0.0))
            except ValueError:
                warnings.append(f"Unknown sentiment '{data['sentiment']}'; ignored.")

        # Entities
        entities: list[Entity] = []
        if cfg.extract_entities:
            for e in data.get("entities", []):
                entities.append(Entity(
                    text=e.get("text", ""),
                    entity_type=e.get("entity_type", "OTHER"),
                    confidence=float(e.get("confidence", 0.0)),
                ))

        language: Optional[str] = data.get("language") if cfg.detect_language else None
        summary: Optional[str] = data.get("summary") if cfg.generate_summary else None

        all_tags = list({content_type.value} | {t.label for t in topics})

        return TagResult(
            content_type=content_type,
            content_type_confidence=ct_conf,
            topics=topics,
            keywords=keywords,
            sentiment=sentiment,
            sentiment_confidence=sentiment_conf,
            entities=entities,
            language=language,
            summary=summary,
            all_tags=all_tags,
            model_used=cfg.model,
            processing_time_ms=round((time.perf_counter() - start) * 1000, 2),
            input_chars=input_chars,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_result(
        input_chars: int, start: float, warnings: list[str]
    ) -> TagResult:
        return TagResult(
            content_type=ContentType.OTHER,
            content_type_confidence=0.0,
            topics=[],
            keywords=[],
            sentiment=None,
            sentiment_confidence=None,
            entities=[],
            language=None,
            summary=None,
            all_tags=[],
            model_used="",
            processing_time_ms=round((time.perf_counter() - start) * 1000, 2),
            input_chars=input_chars,
            warnings=warnings,
        )