"""Jira MCP connector"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class JiraConnector:
    """MCP connector for Jira operations"""

    def __init__(self, client):
        self.client = client

    async def search_issues(self, query: str) -> list:
        """Search Jira issues"""

        if not query or not query.strip():
            return []

        response = await self._execute(query)

        issues = response.get("issues", []) if isinstance(response, dict) else []

        results = []

        for issue in issues:
            fields = issue.get("fields", {}) if isinstance(issue, dict) else {}

            results.append(
                {
                    "id": issue.get("id"),
                    "key": issue.get("key"),
                    "summary": fields.get("summary"),
                    "status": (fields.get("status") or {}).get("name"),
                    "assignee": (
                        (fields.get("assignee") or {}).get("displayName")
                    ),
                    "priority": (fields.get("priority") or {}).get("name"),
                    "created": fields.get("created"),
                    "updated": fields.get("updated"),
                    "url": issue.get("self"),
                    "source": "jira",
                }
            )

        return results

    async def _execute(self, query: str) -> dict:
        """
        Supports Jira REST API or MCP-style wrappers.
        """

        if hasattr(self.client, "search_issues"):
            try:
                return await self.client.search_issues(jql=query)
            except TypeError:
                return self.client.search_issues(jql=query)

        if hasattr(self.client, "get"):
            return await self.client.get(
                "/rest/api/3/search",
                params={"jql": query},
            )

        raise RuntimeError("Unsupported Jira client")