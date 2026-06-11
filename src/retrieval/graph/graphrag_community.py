"""GraphRAG community detection retriever"""

from __future__ import annotations

from typing import List, Any, Dict, Optional


class GraphRAGCommunityRetriever:
    """Retrieve using community detection"""

    def __init__(self, graph_store, embedder=None, top_k_communities: int = 3):
        """
        graph_store: expected to expose:
            - get_communities()
            - get_nodes_in_community(community_id)
        embedder: function(text)->vector (optional for scoring)
        """
        self.graph_store = graph_store
        self.embedder = embedder
        self.top_k_communities = top_k_communities

    async def retrieve(self, query: str, k: int = 10) -> list:
        """Retrieve using community-based retrieval"""

        if not query or not query.strip():
            return []

        communities = self.graph_store.get_communities()

        if not communities:
            return []

        query_vec = self._embed(query)

        scored_communities = []

        for c in communities:
            nodes = self.graph_store.get_nodes_in_community(c)

            if not nodes:
                continue

            # score community by max similarity to query
            score = self._score_community(query_vec, nodes)

            scored_communities.append((c, score))

        scored_communities.sort(key=lambda x: x[1], reverse=True)

        selected_communities = [
            c for c, _ in scored_communities[: self.top_k_communities]
        ]

        results = []

        for c in selected_communities:
            nodes = self.graph_store.get_nodes_in_community(c)

            # flatten nodes into retrievable docs
            for n in nodes:
                results.append(n)

                if len(results) >= k:
                    return results

        return results

    def _embed(self, text: str):
        if not self.embedder:
            return None
        return self.embedder(text)

    def _score_community(self, query_vec, nodes: list) -> float:
        if query_vec is None:
            return 1.0  # fallback uniform scoring

        import numpy as np

        best = 0.0

        for n in nodes:
            vec = None

            if isinstance(n, dict):
                vec = n.get("embedding")
            else:
                vec = getattr(n, "embedding", None)

            if vec is None:
                continue

            sim = float(np.dot(query_vec, vec))
            best = max(best, sim)

        return best