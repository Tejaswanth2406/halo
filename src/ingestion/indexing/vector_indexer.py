"""
Vector indexing with Qdrant
"""

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


class VectorIndexer:
    """Index embeddings in vector database."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "documents"
    ):
        self.collection_name = collection_name

        self.client = QdrantClient(
            host=host,
            port=port
        )

    def index_documents(
        self,
        documents: list
    ) -> None:
        """
        Index documents into vector store.
        """

        points = []

        for idx, doc in enumerate(documents):

            points.append(
                PointStruct(
                    id=idx,
                    vector=doc["embedding"],
                    payload={
                        "text": doc["text"],
                        "source": doc.get(
                            "source"
                        ),
                        "page": doc.get(
                            "page"
                        ),
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
