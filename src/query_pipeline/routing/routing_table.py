"""Routing table lookup"""

from __future__ import annotations

from typing import Dict, Any, Optional


class RoutingTableLookup:
    """Look up routing decisions from config"""

    def __init__(self, routing_table: Optional[dict] = None):
        self.routing_table = routing_table or self._default_table()

    def lookup(self, intent: str) -> dict:
        """Get routing config for intent"""

        if not intent:
            return self.routing_table["fallback"]

        key = intent.strip().lower()

        config = self.routing_table.get(key)

        if not config:
            return self.routing_table["fallback"]

        return {
            "intent": key,
            "retrievers": config.get("retrievers", []),
            "filters": config.get("filters", []),
            "rerankers": config.get("rerankers", []),
            "compressor": config.get("compressor"),
            "top_k": config.get("top_k", 10),
            "hybrid": config.get("hybrid", False),
            "cache_enabled": config.get("cache_enabled", True),
        }

    def _default_table(self) -> dict:
        return {
            "qa": {
                "retrievers": ["bm25", "vector"],
                "filters": ["freshness", "permission", "quality"],
                "rerankers": ["cross_encoder", "cohere"],
                "compressor": "llmlingua",
                "top_k": 10,
                "hybrid": True,
                "cache_enabled": True,
            },
            "factual": {
                "retrievers": ["vector"],
                "filters": ["permission", "quality"],
                "rerankers": ["cross_encoder"],
                "compressor": "extractive",
                "top_k": 5,
                "hybrid": False,
                "cache_enabled": True,
            },
            "analytical": {
                "retrievers": ["vector", "hyde"],
                "filters": ["quality", "freshness"],
                "rerankers": ["cross_encoder", "rankgpt"],
                "compressor": "llmlingua",
                "top_k": 15,
                "hybrid": True,
                "cache_enabled": True,
            },
            "creative": {
                "retrievers": ["vector"],
                "filters": ["quality"],
                "rerankers": [],
                "compressor": None,
                "top_k": 20,
                "hybrid": False,
                "cache_enabled": False,
            },
            "fallback": {
                "retrievers": ["vector"],
                "filters": [],
                "rerankers": [],
                "compressor": None,
                "top_k": 10,
                "hybrid": False,
                "cache_enabled": False,
            },
        }