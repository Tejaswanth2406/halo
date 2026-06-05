"""Budget controller"""

class BudgetController:
    """Enforce per-user / per-tenant budget limits"""
    
    def check_budget(self, user_id: str, estimated_cost: float) -> bool:
        """Check if within budget"""
        pass
