"""
Canary deployment controller
"""

import hashlib


class CanaryController:
    """
    Route a small percentage of users
    to the canary version.
    """

    CANARY_PERCENTAGE = 5

    def get_variant(
        self,
        user_id: str
    ) -> str:
        """
        Returns:
            "canary" or "stable"
        """

        bucket = (
            int(
                hashlib.md5(
                    user_id.encode("utf-8")
                ).hexdigest(),
                16
            )
            % 100
        )

        if bucket < self.CANARY_PERCENTAGE:
            return "canary"

        return "stable"