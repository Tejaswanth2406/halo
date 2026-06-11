"""Procedural memory for user preferences"""

from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class ProceduralMemory:
    """
    Store user preferences and procedures.

    Features:
    - Async-safe access
    - Per-user isolation
    - Deep-copy protection
    - Preference versioning
    - Automatic timestamps
    """

    def __init__(self):
        self._preferences: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get_preferences(
        self,
        user_id: str,
    ) -> dict:
        """Get user preferences"""

        if not user_id:
            raise ValueError("user_id cannot be empty")

        async with self._lock:
            prefs = self._preferences.get(
                user_id,
                {
                    "preferences": {},
                    "version": 1,
                    "created_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "updated_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                },
            )

            return deepcopy(prefs)

    async def update_preferences(
        self,
        user_id: str,
        updates: Dict[str, Any],
    ) -> None:
        """Update user preferences"""

        if not user_id:
            raise ValueError("user_id cannot be empty")

        async with self._lock:
            current = self._preferences.get(
                user_id,
                {
                    "preferences": {},
                    "version": 0,
                    "created_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                },
            )

            current["preferences"].update(
                deepcopy(updates)
            )

            current["version"] += 1
            current["updated_at"] = datetime.now(
                timezone.utc
            ).isoformat()

            self._preferences[user_id] = current

    async def delete_preferences(
        self,
        user_id: str,
    ) -> bool:
        """Delete user preferences"""

        async with self._lock:
            return (
                self._preferences.pop(
                    user_id,
                    None,
                )
                is not None
            )

    async def preference_exists(
        self,
        user_id: str,
    ) -> bool:
        """Check if preferences exist"""

        async with self._lock:
            return user_id in self._preferences