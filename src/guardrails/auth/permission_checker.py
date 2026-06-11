"""RBAC permission checking"""

from __future__ import annotations

from typing import Dict, Set, List, Optional


class PermissionChecker:
    """Check user permissions on documents"""

    def __init__(
        self,
        user_roles: Dict[str, Set[str]],
        document_acl: Dict[str, Dict[str, Set[str]]],
        role_permissions: Optional[Dict[str, Set[str]]] = None,
    ):
        """
        user_roles:
            {
                "user123": {"viewer", "analyst"}
            }

        document_acl:
            {
                "doc001": {
                    "users": {"owner1"},
                    "roles": {"viewer", "editor"}
                }
            }

        role_permissions:
            {
                "admin": {"read", "write", "delete"},
                "viewer": {"read"}
            }
        """

        self.user_roles = user_roles
        self.document_acl = document_acl
        self.role_permissions = role_permissions or {}

    def has_permission(
        self,
        user_id: str,
        doc_id: str,
        action: str = "read",
    ) -> bool:
        """Check if user can access document"""

        if not user_id or not doc_id:
            return False

        document = self.document_acl.get(doc_id)
        if not document:
            return False

        # Direct user access
        allowed_users = document.get("users", set())
        if user_id in allowed_users:
            return True

        user_roles = self.user_roles.get(user_id, set())
        allowed_roles = document.get("roles", set())

        matching_roles = user_roles.intersection(allowed_roles)

        if not matching_roles:
            return False

        for role in matching_roles:
            permissions = self.role_permissions.get(
                role,
                {"read"},
            )

            if action in permissions:
                return True

        return False