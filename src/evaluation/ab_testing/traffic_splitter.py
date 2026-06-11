"""Traffic splitter for AB testing"""

import hashlib


class TrafficSplitter:
    """Split traffic for variants"""

    def get_variant(self, user_id: str, experiment_id: str) -> str:
        """
        Deterministically assign a user to A or B (50/50 split).
        Same user + experiment always gets the same variant.
        """
        key = f"{experiment_id}:{user_id}"
        bucket = int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16) % 100

        return "A" if bucket < 50 else "B"