"""SQL MCP connector for text-to-SQL"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class SQLConnector:
    """MCP connector for SQL operations"""

    def __init__(self, client, llm_client=None):
        """
        client: DB client / connection pool
        llm_client: optional LLM for text-to-SQL
        """
        self.client = client
        self.llm_client = llm_client

    async def execute_query(self, natural_language_query: str) -> list:
        """Convert natural language to SQL and execute"""

        if not natural_language_query or not natural_language_query.strip():
            return []

        sql = self._to_sql(natural_language_query)

        if not sql:
            return []

        result = await self._run_sql(sql)

        return result if isinstance(result, list) else [result]

    def _to_sql(self, query: str) -> str:
        """
        Convert natural language to SQL.
        Falls back to simple heuristic if no LLM provided.
        """

        if self.llm_client and hasattr(self.llm_client, "generate"):
            try:
                prompt = (
                    "Convert the following natural language query into SQL.\n"
                    "Return ONLY SQL, no explanation.\n\n"
                    f"Query:\n{query}\n"
                )
                return self.llm_client.generate(prompt).strip()
            except Exception:
                pass

        # naive fallback (NOT production-safe)
        lowered = query.lower()

        if "users" in lowered:
            return "SELECT * FROM users LIMIT 10;"
        if "orders" in lowered:
            return "SELECT * FROM orders LIMIT 10;"

        return ""

    async def _run_sql(self, sql: str):
        """
        Execute SQL against underlying DB client.
        """

        if hasattr(self.client, "fetch"):
            return await self.client.fetch(sql)

        if hasattr(self.client, "execute"):
            try:
                return await self.client.execute(sql)
            except TypeError:
                return self.client.execute(sql)

        raise RuntimeError("Unsupported SQL client")