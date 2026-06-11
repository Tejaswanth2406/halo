"""Query pipeline orchestration"""

from __future__ import annotations

from typing import Dict, Any, Optional


class QueryPipeline:
    """Orchestrate query understanding, rewriting, and routing"""

    def __init__(
        self,
        intent_classifier,
        language_detector,
        entity_extractor,
        complexity_scorer,
        decomposer=None,
        router=None,
    ):
        self.intent_classifier = intent_classifier
        self.language_detector = language_detector
        self.entity_extractor = entity_extractor
        self.complexity_scorer = complexity_scorer
        self.decomposer = decomposer
        self.router = router

    async def process(self, query: str) -> dict:
        """Process query through pipeline"""

        if not query or not query.strip():
            return {
                "query": query,
                "intent": "unknown",
                "language": "unknown",
                "entities": [],
                "complexity": "simple",
                "subqueries": [],
                "routing": {},
            }

        intent = self.intent_classifier.classify(query)
        language = self.language_detector.detect(query)
        entities = self.entity_extractor.extract(query)
        complexity = self.complexity_scorer.score(query)

        subqueries = []
        if self.decomposer and complexity in {"multi-hop"}:
            try:
                subqueries = self.decomposer.decompose(query)
            except Exception:
                subqueries = []

        routing = {}
        if self.router:
            try:
                routing = self.router.route(query, intent)
            except Exception:
                routing = {}

        return {
            "query": query,
            "intent": intent,
            "language": language,
            "entities": entities,
            "complexity": complexity,
            "subqueries": subqueries,
            "routing": routing,
        }