"""Feedback tracker"""

from datetime import datetime
from typing import Dict, Any


class FeedbackTracker:
    """Track session metrics"""

    def __init__(self):
        self._sessions: Dict[str, list] = {}

    async def track(self, session_id: str, metrics: dict) -> None:
        """Track feedback"""

        if not session_id:
            raise ValueError("session_id cannot be empty")

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics.copy(),
        }

        self._sessions.setdefault(session_id, []).append(record)