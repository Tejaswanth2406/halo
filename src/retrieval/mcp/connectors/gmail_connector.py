"""Gmail MCP connector"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class GmailConnector:
    """MCP connector for Gmail operations"""

    def __init__(self, client):
        """
        client: Gmail API client or MCP wrapper
        """
        self.client = client

    async def search_emails(self, query: str) -> list:
        """Search emails"""

        if not query or not query.strip():
            return []

        response = await self._execute(query)

        messages = response.get("messages", []) if isinstance(response, dict) else []

        results = []

        for msg in messages:
            payload = msg.get("payload", {}) if isinstance(msg, dict) else {}

            headers = payload.get("headers", [])

            subject = self._get_header(headers, "Subject")
            sender = self._get_header(headers, "From")
            date = self._get_header(headers, "Date")

            results.append(
                {
                    "id": msg.get("id"),
                    "threadId": msg.get("threadId"),
                    "subject": subject,
                    "from": sender,
                    "date": date,
                    "snippet": msg.get("snippet"),
                    "source": "gmail",
                }
            )

        return results

    async def _execute(self, query: str) -> dict:
        """
        Supports Gmail API / MCP wrappers.
        """

        if hasattr(self.client, "users"):
            try:
                return (
                    await self.client.users()
                    .messages()
                    .list(userId="me", q=query)
                    .execute()
                )
            except TypeError:
                return (
                    self.client.users()
                    .messages()
                    .list(userId="me", q=query)
                    .execute()
                )

        if hasattr(self.client, "get"):
            return await self.client.get(
                "/gmail/v1/users/me/messages",
                params={"q": query},
            )

        raise RuntimeError("Unsupported Gmail client")

    def _get_header(self, headers: list, name: str) -> Optional[str]:
        for h in headers:
            if h.get("name", "").lower() == name.lower():
                return h.get("value")
        return None