"""MCP tool router"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class MCPRouter:
    """Route queries to appropriate MCP tools"""

    def __init__(self, registry: Optional[dict] = None):
        """
        registry format:
        {
            "github": connector,
            "jira": connector,
            "gdrive": connector,
            "gmail": connector,
            "sql": connector
        }
        """
        self.registry = registry or {}

    async def route_and_execute(self, query: str, intent: str) -> list:
        """Route to MCP tool and execute"""

        if not query or not query.strip():
            return []

        intent = (intent or "unknown").lower()

        tool = self._select_tool(intent)

        if not tool:
            return []

        return await self._execute(tool, query)

    def _select_tool(self, intent: str):
        """Map intent -> MCP tool"""

        mapping = {
            "code": "github",
            "dev": "github",
            "engineering": "github",
            "issue": "jira",
            "ticket": "jira",
            "doc": "gdrive",
            "file": "gdrive",
            "email": "gmail",
            "message": "gmail",
            "sql": "sql",
            "database": "sql",
            "analytics": "sql",
        }

        tool_name = mapping.get(intent)

        if not tool_name:
            return None

        return self.registry.get(tool_name)

    async def _execute(self, tool, query: str) -> list:
        """
        Try common MCP connector method names.
        """

        for method_name in [
            "search",
            "search_files",
            "search_repositories",
            "search_emails",
            "search_issues",
            "execute_query",
        ]:
            if hasattr(tool, method_name):
                method = getattr(tool, method_name)
                try:
                    result = method(query)
                    if hasattr(result, "__await__"):
                        return await result
                    return result
                except Exception:
                    continue

        return []