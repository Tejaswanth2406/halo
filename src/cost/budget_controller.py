class BudgetController:

    def __init__(self, limits: dict):
        """
        limits example:
        {
            "default": 1.0,
            "premium": 10.0
        }
        """
        self.limits = limits
        self.usage = {}

    def _get_limit(self, user_id: str, tier: str = "default"):
        return self.limits.get(tier, self.limits["default"])

    def check_budget(
        self,
        user_id: str,
        estimated_cost: float,
        tier: str = "default"
    ) -> bool:

        used = self.usage.get(user_id, 0.0)
        limit = self._get_limit(user_id, tier)

        if used + estimated_cost > limit:
            return False

        self.usage[user_id] = used + estimated_cost
        return True