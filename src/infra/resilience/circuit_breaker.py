"""Circuit breaker pattern"""

from __future__ import annotations

import asyncio
import time
from enum import Enum
from typing import Any, Callable, Awaitable


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for fault tolerance"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
        timeout_seconds: float = 15.0,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0

    async def call(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs,
    ) -> Any:
        """Execute with circuit breaker"""

        now = time.monotonic()

        if self.state == CircuitState.OPEN:
            if (
                now - self.last_failure_time
                < self.recovery_timeout
            ):
                raise RuntimeError(
                    "Circuit breaker is OPEN"
                )

            self.state = CircuitState.HALF_OPEN
            self.success_count = 0

        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.timeout_seconds,
            )

            await self._on_success()

            return result

        except Exception:
            await self._on_failure()
            raise

    async def _on_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1

            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0

        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    async def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.monotonic()

        if (
            self.failure_count >= self.failure_threshold
        ):
            self.state = CircuitState.OPEN

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED

    @property
    def is_half_open(self) -> bool:
        return self.state == CircuitState.HALF_OPEN

    def reset(self) -> None:
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0