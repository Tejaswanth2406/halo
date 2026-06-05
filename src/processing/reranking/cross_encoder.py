"""Cross-encoder reranking"""

class CrossEncoderReranker:
    """Stage 2: ms-marco-MiniLM cross-encoder reranking"""
    
    async def rerank(self, query: str, documents: list, k: int = 10) -> list:
        """Rerank using cross-encoder"""
        pass
