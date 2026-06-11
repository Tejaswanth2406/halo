"""MCP tool registry"""

from __future__ import annotations

from typing import List, Dict, Any, Optional


class ToolRegistry:
    """Registry of available MCP tools"""

    def __init__(self, tools: Optional[dict] = None):
        """
        tools format:
        {
            "github": connector,
            "jira": connector,
            "gdrive": connector,
            "gmail": connector,
            "sql": connector
        }
        """
        self.tools = tools or {}

    def get_tools(self, intent: str) -> list:
        """Get available tools for intent"""

        if not intent:
            return []

        intent = intent.lower().strip()

        intent_map = {
            "code": ["github"],
            "dev": ["github"],
            "engineering": ["github"],
            "issue": ["jira"],
            "ticket": ["jira"],
            "doc": ["gdrive"],
            "file": ["gdrive"],
            "email": ["gmail"],
            "message": ["gmail"],
            "sql": ["sql"],
            "database": ["sql"],
            "analytics": ["sql"],
            "research": ["github", "gdrive"],
            "productivity": ["gmail", "gdrive", "jira"],
        }

        tool_names = intent_map.get(intent, [])

        return [
            self.tools[name]
            for name in tool_names
            if name in self.tools
        ]