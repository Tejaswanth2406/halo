"""Embedding model manager for swapping models"""

from __future__ import annotations

from threading import RLock
from typing import Dict, Any, Optional

from sentence_transformers import SentenceTransformer


class EmbeddingModelManager:
    """Manage embedding models with versioning"""

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._current_model_name = self.DEFAULT_MODEL
        self._lock = RLock()

    def get_model(self, model_name: str):
        """Load embedding model"""

        if not model_name:
            raise ValueError("model_name cannot be empty")

        with self._lock:
            if model_name not in self._models:
                self._models[model_name] = SentenceTransformer(
                    model_name
                )

            return self._models[model_name]

    def set_active_model(
        self,
        model_name: str,
    ) -> None:
        """Switch active embedding model"""

        self.get_model(model_name)

        with self._lock:
            self._current_model_name = model_name

    def embed(
        self,
        text: str,
    ) -> list:
        """Embed text with current model"""

        if not text:
            raise ValueError("text cannot be empty")

        with self._lock:
            model = self.get_model(
                self._current_model_name
            )

        embedding = model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embedding.tolist()

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Batch embedding"""

        if not texts:
            return []

        with self._lock:
            model = self.get_model(
                self._current_model_name
            )

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            batch_size=128,
            show_progress_bar=False,
        )

        return embeddings.tolist()

    @property
    def active_model(self) -> str:
        return self._current_model_name

    @property
    def loaded_models(self) -> list[str]:
        return list(self._models.keys())