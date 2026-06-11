"""Embedding manager for vector retrieval"""

from __future__ import annotations

from typing import List, Any, Optional


class EmbeddingManager:
    """Manage embeddings with model swapping"""

    def __init__(self, model_registry: dict, default_model: str):
        """
        model_registry: {"openai": model_obj, "local": model_obj, ...}
        default_model: active embedding model key
        """
        self.model_registry = model_registry
        self.default_model = default_model

    def embed_query(self, query: str) -> list:
        """Embed query for vector search"""

        if not query or not query.strip():
            return []

        model = self.model_registry.get(self.default_model)

        if not model:
            raise ValueError(f"Embedding model '{self.default_model}' not found")

        return self._embed(model, query)

    def _embed(self, model, text: str) -> list:
        """
        Supports common embedding interfaces:
        - model.embed(text)
        - model.encode(text)
        - model(text)
        """

        if hasattr(model, "embed"):
            return model.embed(text)

        if hasattr(model, "encode"):
            return model.encode(text)

        if callable(model):
            return model(text)

        raise RuntimeError("Unsupported embedding model interface")