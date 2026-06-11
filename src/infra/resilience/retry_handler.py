"""Retry handler with exponential backoff"""

from __future__ import annotations

import asyncio
import random
from typing import Any, Awaitable, Callable, Tuple, Type


class RetryHandler:
    """Retry with exponential backoff + jitter"""

    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 0.5,
        max_delay: float = 30.0,
        retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_exceptions = retry_exceptions

    async def retry(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs,
    ) -> Any:
        """Execute with retries"""

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)

            except self.retry_exceptions as exc:
                last_exception = exc

                if attempt >= self.max_retries:
                    break

                delay = min(
                    self.base_delay * (2**attempt),
                    self.max_delay,
                )

                # Full jitter strategy (AWS recommended)
                delay = random.uniform(0, delay)

                await asyncio.sleep(delay)

        raise last_exception