"""BM25 pre-filter for reranking"""

class BM25Prefilter:
    """Stage 1: cheap BM25 scoring filter"""
    
    def filter(self, documents: list, k: int = 50) -> list:
        """Filter using BM25 scores"""
        pass
