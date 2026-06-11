"""Rate limiting using Redis"""

import time
from typing import Optional


class RateLimiter:
    """Rate limit queries per user/tenant"""

    def __init__(
        self,
        redis_client,
        max_requests: int = 100,
        window_seconds: int = 60,
    ):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def check_limit(self, user_id: str) -> bool:
        """Check if user exceeded rate limit"""

        key = f"rate_limit:{user_id}"
        current = self.redis.incr(key)

        if current == 1:
            self.redis.expire(key, self.window_seconds)

        return current <= self.max_requests