"""
Index version controller
"""

from datetime import datetime


class IndexVersionController:
    """Manage index versions by model version."""

    def __init__(self):
        self.current_version = None
        self.version_history = []

    def tag_index(self, model_version: str) -> None:
        """
        Tag the current index with a model version.

        Example:
            text-embedding-3-small-v1
            text-embedding-3-large-v2
        """

        self.current_version = model_version

        self.version_history.append(
            {
                "model_version": model_version,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def get_current_version(self) -> str | None:
        """
        Return active index version.
        """

        return self.current_version

    def get_version_history(self) -> list:
        """
        Return all tagged versions.
        """

        return self.version_history