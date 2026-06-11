"""Table-to-SQL retriever"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class TableSQLRetriever:
    """Convert natural language to SQL for structured tables"""

    def __init__(self, db_client, llm_client=None, schema: Optional[dict] = None):
        """
        db_client: database execution client
        llm_client: optional LLM for text-to-SQL
        schema: optional table schema metadata
        """
        self.db_client = db_client
        self.llm_client = llm_client
        self.schema = schema or {}

    async def retrieve(self, query: str, k: int = 10) -> list:
        """Retrieve using text-to-SQL"""

        if not query or not query.strip():
            return []

        sql = self._generate_sql(query)

        if not sql:
            return []

        rows = await self._execute(sql)

        if isinstance(rows, list):
            return rows[:k]

        return [rows]

    def _generate_sql(self, query: str) -> str:
        """
        Generate SQL from natural language query.
        """

        if self.llm_client and hasattr(self.llm_client, "generate"):
            try:
                prompt = self._build_prompt(query)
                return self.llm_client.generate(prompt).strip()
            except Exception:
                pass

        # fallback heuristic (unsafe but minimal)
        q = query.lower()

        if "users" in q:
            return "SELECT * FROM users LIMIT 10;"
        if "orders" in q:
            return "SELECT * FROM orders LIMIT 10;"
        if "sales" in q:
            return "SELECT * FROM sales LIMIT 10;"

        return ""

    def _build_prompt(self, query: str) -> str:
        schema_text = str(self.schema)

        return (
            "You are a text-to-SQL generator.\n"
            "Generate a SQL query for the given question.\n"
            "Return ONLY SQL, no explanation.\n\n"
            f"Schema:\n{schema_text}\n\n"
            f"Question:\n{query}\n"
        )

    async def _execute(self, sql: str):
        """
        Execute SQL query on DB client.
        """

        if hasattr(self.db_client, "fetch"):
            return await self.db_client.fetch(sql)

        if hasattr(self.db_client, "execute"):
            try:
                return await self.db_client.execute(sql)
            except TypeError:
                return self.db_client.execute(sql)

        raise RuntimeError("Unsupported database client")