"""Neo4j graph-based retriever"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class Neo4jRetriever:
    """Retrieve using graph traversal"""

    def __init__(
        self,
        driver,
        embedder=None,
        max_hops: int = 2,
    ):
        """
        driver: Neo4j driver instance
        embedder: optional function(text)->vector for semantic scoring
        """
        self.driver = driver
        self.embedder = embedder
        self.max_hops = max_hops

    async def retrieve(self, query: str, k: int = 10) -> list:
        """Retrieve from knowledge graph"""

        if not query or not query.strip():
            return []

        query_vec = self._embed(query)

        cypher = self._build_cypher(query)

        results = await self._run_query(cypher)

        scored = []

        for r in results:
            score = self._score_node(r, query_vec)
            scored.append((r, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [node for node, _ in scored[:k]]

    def _build_cypher(self, query: str) -> str:
        # simple keyword-based traversal; replace with LLM planner if needed
        return f"""
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower('{query}')
           OR toLower(n.description) CONTAINS toLower('{query}')
        OPTIONAL MATCH (n)-[*1..{self.max_hops}]-(m)
        RETURN DISTINCT n, m
        LIMIT 200
        """

    async def _run_query(self, cypher: str) -> list:
        def _exec(tx):
            return list(tx.run(cypher))

        async with self.driver.session() as session:
            result = await session.execute_read(_exec)
            return result

    def _embed(self, text: str):
        if not self.embedder:
            return None
        return self.embedder(text)

    def _score_node(self, node: Any, query_vec) -> float:
        if query_vec is None:
            return 1.0

        try:
            n = node.get("n") if isinstance(node, dict) else getattr(node, "n", None)

            if not n:
                return 0.0

            vec = n.get("embedding") if isinstance(n, dict) else getattr(n, "embedding", None)

            if vec is None:
                return 0.0

            import numpy as np

            return float(np.dot(query_vec, vec))

        except Exception:
            return 0.0