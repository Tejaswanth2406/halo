"""Embedding cache to avoid recomputation"""

class EmbeddingCache:
    """Cache embeddings by content hash"""
    
    def get(self, content_hash: str) -> list:
        """Get cached embedding"""
        pass
    
    def set(self, content_hash: str, embedding: list):
        """Cache embedding"""
        pass
