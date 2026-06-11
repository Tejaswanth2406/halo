"""Permission-based post-retrieval filtering"""

from __future__ import annotations

from typing import List, Any, Set, Optional


class PermissionFilter:
    """Filter documents by user permissions"""

    def __init__(self, permission_checker):
        self.permission_checker = permission_checker

    def filter(
        self,
        documents: list,
        user_id: str,
    ) -> list:
        """Filter by RBAC permissions"""

        if not documents:
            return []

        if not user_id:
            return []

        filtered: List[Any] = []

        for doc in documents:
            doc_id = self._extract_doc_id(doc)

            if not doc_id:
                continue

            try:
                if self.permission_checker.has_permission(
                    user_id,
                    doc_id,
                    "read",
                ):
                    filtered.append(doc)
            except Exception:
                # fail-closed for security
                continue

        return filtered

    def _extract_doc_id(self, doc: Any) -> Optional[str]:
        """Extract document id safely"""

        if isinstance(doc, dict):
            return (
                doc.get("doc_id")
                or doc.get("id")
                or doc.get("document_id")
            )

        return getattr(doc, "doc_id", None) or getattr(doc, "id", None)