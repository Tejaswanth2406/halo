"""Agent scratchpad for working memory"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid


class AgentScratchpad:
    """Working memory for agent reasoning"""

    def __init__(self, max_thoughts: int = 1000):
        self.max_thoughts = max_thoughts
        self._thoughts: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def add_thought(self, thought: str) -> None:
        """Add reasoning thought"""

        if not thought or not thought.strip():
            raise ValueError("thought cannot be empty")

        record = {
            "id": str(uuid.uuid4()),
            "thought": thought.strip(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        async with self._lock:
            self._thoughts.append(record)

            if len(self._thoughts) > self.max_thoughts:
                self._thoughts = self._thoughts[
                    -self.max_thoughts :
                ]

    async def get_thoughts(self) -> list:
        """Get all stored thoughts"""

        async with self._lock:
            return list(self._thoughts)

    async def clear(self) -> None:
        """Clear scratchpad"""

        async with self._lock:
            self._thoughts.clear()

    async def last_thought(self) -> Optional[Dict[str, Any]]:
        """Get most recent thought"""

        async with self._lock:
            if not self._thoughts:
                return None
            return self._thoughts[-1]

    async def size(self) -> int:
        """Number of stored thoughts"""

        async with self._lock:
            return len(self._thoughts)