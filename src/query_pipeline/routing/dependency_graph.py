"""Dependency graph for sub-queries"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from collections import defaultdict, deque


class DependencyGraph:
    """Build dependency graph for sub-queries"""

    def build_graph(self, subqueries: list) -> dict:
        """Build execution graph for sub-queries"""

        if not subqueries:
            return {
                "nodes": [],
                "edges": [],
                "adjacency": {},
                "topological_order": [],
            }

        nodes = []
        edges = []
        adjacency = defaultdict(list)
        indegree = defaultdict(int)

        # Normalize nodes
        for i, q in enumerate(subqueries):
            if isinstance(q, dict):
                node_id = q.get("id", f"q{i}")
                depends_on = q.get("depends_on", [])
            else:
                node_id = f"q{i}"
                depends_on = []

            nodes.append(node_id)

            # Ensure indegree entry exists
            indegree[node_id] = indegree.get(node_id, 0)

        # Build edges
        for i, q in enumerate(subqueries):
            if isinstance(q, dict):
                node_id = q.get("id", f"q{i}")
                depends_on = q.get("depends_on", [])
            else:
                node_id = f"q{i}"
                depends_on = []

            # Explicit dependencies
            if depends_on:
                for dep in depends_on:
                    edges.append((dep, node_id))
                    adjacency[dep].append(node_id)
                    indegree[node_id] += 1

            # Default: sequential dependency chain
            else:
                if i > 0:
                    prev_id = (
                        subqueries[i - 1].get("id", f"q{i-1}")
                        if isinstance(subqueries[i - 1], dict)
                        else f"q{i-1}"
                    )
                    edges.append((prev_id, node_id))
                    adjacency[prev_id].append(node_id)
                    indegree[node_id] += 1

        # Topological sort (Kahn's algorithm)
        queue = deque([n for n in nodes if indegree[n] == 0])
        topo_order = []

        while queue:
            node = queue.popleft()
            topo_order.append(node)

            for nei in adjacency[node]:
                indegree[nei] -= 1
                if indegree[nei] == 0:
                    queue.append(nei)

        return {
            "nodes": nodes,
            "edges": edges,
            "adjacency": dict(adjacency),
            "topological_order": topo_order,
        }