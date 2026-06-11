"""Signal collector for user feedback"""

from datetime import datetime
from typing import Dict, Any, List


class SignalCollector:
    """Collect user feedback signals"""

    def __init__(self):
        self._signals: List[Dict[str, Any]] = []

    async def collect(
        self,
        query: str,
        response: str,
        feedback: dict,
    ) -> None:
        """Record user feedback"""

        signal = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "response": response,
            "feedback": feedback,
            "rating": feedback.get("rating"),
            "liked": feedback.get("liked"),
            "comment": feedback.get("comment"),
        }

        self._signals.append(signal)