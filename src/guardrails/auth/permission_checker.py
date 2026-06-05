"""RBAC permission checking"""

class PermissionChecker:
    """Check user permissions on documents"""
    
    def has_permission(self, user_id: str, doc_id: str) -> bool:
        """Check if user can access document"""
        pass
