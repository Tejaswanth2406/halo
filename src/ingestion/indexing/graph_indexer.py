"""
Graph indexing primitives for future GraphRAG support.

Week 1:
- Store entities
- Store relationships
- Validate graph data

Week 3:
- Add Neo4j persistence
- Add graph traversal
- Add GraphRAG retrieval
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Entity:
    id: str
    label: str
    entity_type: str


@dataclass
class Relationship:
    source: str
    relation: str
    target: str


class GraphIndexer:
    """
    In-memory graph index.

    Acts as a placeholder until Neo4j is introduced.
    """

    def __init__(self) -> None:
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []

    def add_entity(self, entity: Entity) -> None:
        """
        Add entity to graph.
        """

        self.entities[entity.id] = entity

    def add_relationship(
        self,
        relationship: Relationship
    ) -> None:
        """
        Add relationship between entities.
        """

        if relationship.source not in self.entities:
            raise ValueError(
                f"Unknown source entity: "
                f"{relationship.source}"
            )

        if relationship.target not in self.entities:
            raise ValueError(
                f"Unknown target entity: "
                f"{relationship.target}"
            )

        self.relationships.append(
            relationship
        )

    def get_entity(
        self,
        entity_id: str
    ) -> Entity | None:
        """
        Fetch entity by id.
        """

        return self.entities.get(entity_id)

    def get_neighbors(
        self,
        entity_id: str
    ) -> List[Relationship]:
        """
        Get all connected relationships.
        """

        return [
            rel
            for rel in self.relationships
            if rel.source == entity_id
            or rel.target == entity_id
        ]

    def entity_count(self) -> int:
        """
        Number of indexed entities.
        """

        return len(self.entities)

    def relationship_count(self) -> int:
        """
        Number of indexed relationships.
        """

        return len(self.relationships)

    def clear(self) -> None:
        """
        Reset graph.
        """

        self.entities.clear()
        self.relationships.clear()