"""Canary deployment controller"""

class CanaryController:
    """5% traffic split for new versions"""
    
    def get_variant(self, user_id: str) -> str:
        """Get variant (canary or stable)"""
        pass
