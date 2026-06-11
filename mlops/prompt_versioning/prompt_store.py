"""
Prompt version control
"""

from datetime import datetime


class PromptStore:
    """Git-like prompt versioning."""

    def __init__(self):
        self.prompts = {}

    def store_version(
        self,
        prompt: str,
        version: str,
        metadata: dict | None = None
    ) -> None:
        """
        Store a prompt version.
        """

        self.prompts[version] = {
            "prompt": prompt,
            "version": version,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }

    def get_version(
        self,
        version: str
    ) -> dict | None:
        """
        Retrieve a prompt version.
        """

        return self.prompts.get(version)

    def list_versions(
        self
    ) -> list:
        """
        Return all stored versions.
        """

        return list(self.prompts.values())