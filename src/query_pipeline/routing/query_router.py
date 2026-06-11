"""Query router for intent-based routing"""

from __future__ import annotations

from typing import Dict, Any, Optional


class QueryRouter:
    """Route query based on intent"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._default_config()

    def route(self, query: str, intent: str) -> dict:
        """Get routing config for query"""

        if not query:
            return self.config["fallback"]

        intent = (intent or "unknown").lower()

        route_config = self.config.get(intent)

        if not route_config:
            return self.config["fallback"]

        return {
            "intent": intent,
            "query": query,
            "retrievers": route_config.get("retrievers", []),
            "filters": route_config.get("filters", []),
            "rerankers": route_config.get("rerankers", []),
            "compressor": route_config.get("compressor"),
            "top_k": route_config.get("top_k", 10),
            "hybrid": route_config.get("hybrid", False),
            "fallback_used": False,
        }

    def _default_config(self) -> dict:
        return {
            "qa": {
                "retrievers": ["bm25", "vector"],
                "filters": ["freshness", "permission", "quality"],
                "rerankers": ["cross_encoder", "cohere"],
                "compressor": "llmlingua",
                "top_k": 10,
                "hybrid": True,
            },
            "factual": {
                "retrievers": ["vector"],
                "filters": ["permission", "quality"],
                "rerankers": ["cross_encoder"],
                "compressor": "extractive",
                "top_k": 5,
                "hybrid": False,
            },
            "analytical": {
                "retrievers": ["vector", "hyde"],
                "filters": ["quality"],
                "rerankers": ["cross_encoder", "rankgpt"],
                "compressor": "llmlingua",
                "top_k": 15,
                "hybrid": True,
            },
            "creative": {
                "retrievers": ["vector"],
                "filters": ["quality"],
                "rerankers": [],
                "compressor": None,
                "top_k": 20,
                "hybrid": False,
            },
            "fallback": {
                "retrievers": ["vector"],
                "filters": [],
                "rerankers": [],
                "compressor": None,
                "top_k": 10,
                "hybrid": False,
                "fallback_used": True,
            },
        }
