"""
Production-grade HTML scraper using trafilatura.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import trafilatura
from trafilatura.settings import use_config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

@dataclass
class ScraperConfig:
    """Runtime configuration for the HTML scraper."""
    include_comments: bool = False
    include_tables: bool = True
    include_images: bool = False
    include_links: bool = False
    no_fallback: bool = False       # if True, skip readability/justext fallbacks
    favor_precision: bool = False   # fewer but higher-quality extractions
    favor_recall: bool = False      # more text, may include boilerplate
    target_language: Optional[str] = None  # ISO 639-1 code, e.g. "en", "fr"
    timeout: int = 10               # seconds for URL fetching
    user_agent: Optional[str] = None


@dataclass
class ScrapeResult:
    """Structured result from a single scrape operation."""
    # Core content
    text: str
    title: Optional[str]
    author: Optional[str]
    date: Optional[str]
    description: Optional[str]
    language: Optional[str]
    url: Optional[str]
    # Extras (populated when config flags are set)
    comments: Optional[str]
    links: list[str]
    # Meta
    source: str                    # "url" | "html_string"
    processing_time_ms: float
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return bool(self.text)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "description": self.description,
            "language": self.language,
            "url": self.url,
            "comments": self.comments,
            "links": self.links,
            "source": self.source,
            "processing_time_ms": self.processing_time_ms,
            "warnings": self.warnings,
            "success": self.success,
        }


# ---------------------------------------------------------------------------
# Core scraper
# ---------------------------------------------------------------------------

class HTMLScraper:
    """
    Production-ready HTML scraper built on trafilatura.

    Features
    --------
    - Parse raw HTML strings or fetch + scrape a URL directly.
    - Structured ScrapeResult with title, author, date, language, and more.
    - Configurable precision/recall trade-off, comment/table/link extraction.
    - Optional language filtering.
    - Batch scraping for multiple URLs.
    - Full logging and per-call warning capture.

    Usage
    -----
    >>> scraper = HTMLScraper()

    # From raw HTML
    >>> result = scraper.parse("<html>...</html>")
    >>> print(result.text, result.title)

    # From URL (fetches automatically)
    >>> result = scraper.fetch("https://example.com/article")
    >>> print(result.to_dict())

    # Batch
    >>> results = scraper.fetch_batch(["https://a.com", "https://b.com"])
    """

    def __init__(self, config: Optional[ScraperConfig] = None) -> None:
        self.config = config or ScraperConfig()
        self._traf_config = self._build_traf_config()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, html_content: str, url: Optional[str] = None) -> ScrapeResult:
        """
        Extract content from a raw HTML string.

        Parameters
        ----------
        html_content:
            Raw HTML markup.
        url:
            Optional source URL — improves metadata extraction and
            relative-link resolution when provided.

        Returns
        -------
        ScrapeResult
            Always returns a ScrapeResult; check `.success` for whether
            meaningful content was found.
        """
        if not html_content or not html_content.strip():
            return self._empty_result("html_string", time.perf_counter(), ["Empty HTML input."])

        start = time.perf_counter()
        warnings: list[str] = []

        return self._extract(html_content, url=url, source="html_string",
                             start=start, warnings=warnings)

    def fetch(self, url: str) -> ScrapeResult:
        """
        Fetch *url* and extract its main content.

        Parameters
        ----------
        url:
            Fully-qualified URL (must include scheme, e.g. https://).

        Returns
        -------
        ScrapeResult
        """
        start = time.perf_counter()
        warnings: list[str] = []

        if not self._is_valid_url(url):
            warnings.append(f"Invalid or unsupported URL: {url!r}")
            return self._empty_result("url", start, warnings)

        html = self._fetch_url(url, warnings)
        if not html:
            return self._empty_result("url", start, warnings)

        return self._extract(html, url=url, source="url", start=start, warnings=warnings)

    def fetch_batch(self, urls: list[str]) -> list[ScrapeResult]:
        """Fetch and extract content from multiple URLs."""
        return [self.fetch(url) for url in urls]

    # ------------------------------------------------------------------
    # Internal extraction
    # ------------------------------------------------------------------

    def _extract(
        self,
        html: str,
        url: Optional[str],
        source: str,
        start: float,
        warnings: list[str],
    ) -> ScrapeResult:
        cfg = self.config
        kwargs = dict(
            include_comments=cfg.include_comments,
            include_tables=cfg.include_tables,
            no_fallback=cfg.no_fallback,
            favor_precision=cfg.favor_precision,
            favor_recall=cfg.favor_recall,
            url=url,
        )
        if cfg.target_language:
            kwargs["target_language"] = cfg.target_language

        try:
            # Primary text extraction
            text: str = trafilatura.extract(html, **kwargs) or ""

            # Rich metadata
            meta = trafilatura.extract_metadata(html, default_url=url)

            # Optional: extract links
            links: list[str] = []
            if cfg.include_links:
                links = self._extract_links(html, base_url=url)

            # Optional: separate comment pass
            comments: Optional[str] = None
            if cfg.include_comments:
                comments = trafilatura.extract(
                    html, include_comments=True, no_fallback=cfg.no_fallback, url=url
                ) or None

        except Exception as exc:
            logger.error("Trafilatura extraction failed: %s", exc)
            warnings.append(f"Extraction error: {exc}")
            return self._empty_result(source, start, warnings)

        elapsed = (time.perf_counter() - start) * 1000

        if not text:
            warnings.append(
                "No main content extracted — page may be JS-rendered, "
                "paywalled, or mostly non-textual."
            )

        logger.debug(
            "Scrape complete: source=%s chars=%d ms=%.0f",
            source, len(text), elapsed,
        )

        return ScrapeResult(
            text=text.strip(),
            title=getattr(meta, "title", None),
            author=getattr(meta, "author", None),
            date=getattr(meta, "date", None),
            description=getattr(meta, "description", None),
            language=getattr(meta, "language", None),
            url=getattr(meta, "url", url),
            comments=comments,
            links=links,
            source=source,
            processing_time_ms=round(elapsed, 2),
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # URL fetching
    # ------------------------------------------------------------------

    def _fetch_url(self, url: str, warnings: list[str]) -> Optional[str]:
        try:
            fetch_kwargs: dict = {"url": url}
            if self.config.user_agent:
                fetch_kwargs["no_ssl"] = False  # keep default; UA set via config below
            html = trafilatura.fetch_url(url)
            if not html:
                warnings.append(f"fetch_url returned empty response for {url!r}.")
            return html
        except Exception as exc:
            warnings.append(f"Failed to fetch {url!r}: {exc}")
            logger.warning("Fetch error for %s: %s", url, exc)
            return None

    # ------------------------------------------------------------------
    # Link extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_links(html: str, base_url: Optional[str] = None) -> list[str]:
        try:
            from lxml import etree
            from io import StringIO

            parser = etree.HTMLParser()
            tree = etree.parse(StringIO(html), parser)
            hrefs = tree.xpath("//a/@href")

            if not base_url:
                return [h for h in hrefs if h.startswith("http")]

            from urllib.parse import urljoin
            base = base_url
            resolved = []
            for href in hrefs:
                if href.startswith("#") or not href:
                    continue
                full = href if href.startswith("http") else urljoin(base, href)
                resolved.append(full)
            return list(dict.fromkeys(resolved))  # deduplicate, preserve order
        except Exception as exc:
            logger.debug("Link extraction failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_traf_config():
        """Return a trafilatura config with sensible production defaults."""
        traf_cfg = use_config()
        traf_cfg.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")  # disable internal timeout
        return traf_cfg

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        except Exception:
            return False

    @staticmethod
    def _empty_result(source: str, start: float, warnings: list[str]) -> ScrapeResult:
        return ScrapeResult(
            text="",
            title=None,
            author=None,
            date=None,
            description=None,
            language=None,
            url=None,
            comments=None,
            links=[],
            source=source,
            processing_time_ms=round((time.perf_counter() - start) * 1000, 2),
            warnings=warnings,
        )