"""Human-in-the-loop queue for flagged responses"""

from datetime import datetime
from typing import Dict, List, Any
import uuid


class HumanInTheLoop:
    """Queue responses for human review"""

    def __init__(self):
        self.review_queue: List[Dict[str, Any]] = []

    def queue_for_review(self, response: str, reason: str) -> None:
        """Queue response for human review"""

        if not response:
            raise ValueError("response cannot be empty")

        review_item = {
            "review_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending",
            "reason": reason,
            "response": response,
            "priority": "high",
        }

        self.review_queue.append(review_item)