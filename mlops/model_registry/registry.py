"""
Model registry
"""

from datetime import datetime


class ModelRegistry:
    """Track embedding model → index version."""

    def __init__(self):
        self.models = {}

    def register_model(
        self,
        model_name: str,
        version: str
    ) -> None:
        """
        Register a model version.
        """

        self.models[version] = {
            "model_name": model_name,
            "version": version,
            "registered_at": datetime.utcnow().isoformat()
        }

    def get_model(
        self,
        version: str
    ) -> dict | None:
        """
        Retrieve model metadata.
        """

        return self.models.get(version)

    def list_models(
        self
    ) -> list:
        """
        Return all registered models.
        """

        return list(self.models.values())