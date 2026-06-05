"""Redis cache for exact queries"""

class L2RedisCache:
    """Redis cache by query hash"""
    
    async def get(self, query_hash: str) -> Any:
        """Get from Redis"""
        pass
