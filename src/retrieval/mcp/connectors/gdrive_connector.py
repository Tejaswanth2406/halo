"""Google Drive MCP connector"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class GDriveConnector:
    """MCP connector for Google Drive operations"""

    def __init__(self, client):
        """
        client: Google Drive API client (or MCP wrapper)
        """
        self.client = client

    async def search_files(self, query: str) -> list:
        """Search Google Drive files"""

        if not query or not query.strip():
            return []

        q = {
            "q": f"name contains '{query}' or fullText contains '{query}'",
            "fields": "files(id, name, mimeType, modifiedTime, webViewLink)",
            "pageSize": 10,
        }

        response = await self._execute(q)

        files = response.get("files", []) if isinstance(response, dict) else []

        results = []

        for f in files:
            results.append(
                {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "mimeType": f.get("mimeType"),
                    "modifiedTime": f.get("modifiedTime"),
                    "url": f.get("webViewLink"),
                    "source": "gdrive",
                }
            )

        return results

    async def _execute(self, params: dict) -> dict:
        """
        Supports both async MCP-style clients and sync Google API clients.
        """
        if hasattr(self.client, "files"):
            try:
                # async MCP-like wrapper
                return await self.client.files().list(**params).execute()
            except TypeError:
                # sync fallback
                return self.client.files().list(**params).execute()

        raise RuntimeError("Unsupported Google Drive client")
