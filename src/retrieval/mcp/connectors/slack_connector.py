"""Slack MCP connector"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class SlackConnector:
    """MCP connector for Slack operations"""

    def __init__(self, client=None):
        """
        client: Slack SDK client (optional)
        """
        self.client = client

    async def search_messages(self, query: str) -> list:
        """Search Slack messages"""

        if not query:
            return []

        if not self.client:
            # fallback mock behavior (useful for local testing)
            return []

        try:
            # Typical Slack API usage: search.messages
            result = self.client.search_messages(query=query)

            # handle async or sync SDKs
            if hasattr(result, "__await__"):
                result = await result

            messages = (
                result.get("messages", {}).get("matches", [])
                if isinstance(result, dict)
                else []
            )

            return messages

        except Exception:
            return []