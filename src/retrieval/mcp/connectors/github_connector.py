"""GitHub MCP connector"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class GitHubConnector:
    """MCP connector for GitHub operations"""

    def __init__(self, client, token: Optional[str] = None):
        """
        client: GitHub API client (PyGithub or MCP wrapper)
        token: optional auth token if needed
        """
        self.client = client
        self.token = token

    async def search_repositories(self, query: str) -> list:
        """Search GitHub repositories"""

        if not query or not query.strip():
            return []

        response = await self._execute(query)

        items = response.get("items", []) if isinstance(response, dict) else []

        results = []

        for repo in items:
            results.append(
                {
                    "id": repo.get("id"),
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "url": repo.get("html_url"),
                    "stars": repo.get("stargazers_count"),
                    "language": repo.get("language"),
                    "source": "github",
                }
            )

        return results

    async def _execute(self, query: str) -> dict:
        """
        Supports GitHub REST search API or MCP-style wrappers.
        """

        if hasattr(self.client, "search_repositories"):
            try:
                return await self.client.search_repositories(query=query)
            except TypeError:
                return self.client.search_repositories(query=query)

        if hasattr(self.client, "get"):
            # generic MCP-style call
            return await self.client.get(
                "/search/repositories",
                params={"q": query},
            )

        raise RuntimeError("Unsupported GitHub client")