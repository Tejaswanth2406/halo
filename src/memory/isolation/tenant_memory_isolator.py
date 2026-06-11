"""Tenant memory isolation"""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Dict, Any, Optional


class TenantMemoryIsolator:
    """
    Strong tenant isolation layer.

    Guarantees:
    - No cross-tenant memory access
    - Async-safe access
    - Deep-copy protection
    - Lazy tenant initialization
    """

    def __init__(
        self,
        default_memory: Optional[Dict[str, Any]] = None,
    ):
        self._tenant_memory: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._default_memory = default_memory or {
            "conversation_history": [],
            "preferences": {},
            "metadata": {},
        }

    async def get_tenant_memory(
        self,
        tenant_id: str,
    ) -> dict:
        """Get tenant-specific memory"""

        if not tenant_id:
            raise ValueError("tenant_id cannot be empty")

        async with self._lock:
            if tenant_id not in self._tenant_memory:
                self._tenant_memory[tenant_id] = deepcopy(
                    self._default_memory
                )

            # Return deep copy to prevent
            # accidental mutation outside
            return deepcopy(
                self._tenant_memory[tenant_id]
            )

    async def update_tenant_memory(
        self,
        tenant_id: str,
        updates: Dict[str, Any],
    ) -> None:
        """Update tenant memory"""

        if not tenant_id:
            raise ValueError("tenant_id cannot be empty")

        async with self._lock:
            if tenant_id not in self._tenant_memory:
                self._tenant_memory[tenant_id] = deepcopy(
                    self._default_memory
                )

            self._tenant_memory[tenant_id].update(
                deepcopy(updates)
            )

    async def delete_tenant_memory(
        self,
        tenant_id: str,
    ) -> bool:
        """Delete tenant memory"""

        async with self._lock:
            return (
                self._tenant_memory.pop(
                    tenant_id,
                    None,
                )
                is not None
            )

    async def tenant_exists(
        self,
        tenant_id: str,
    ) -> bool:
        """Check tenant existence"""

        async with self._lock:
            return tenant_id in self._tenant_memory

    async def clear_all(self) -> None:
        """Administrative purge"""

        async with self._lock:
            self._tenant_memory.clear()