"""Quality regression alerter"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Callable, Awaitable


class QualityRegressionAlert:
    """Alert on RAGAS drop"""

    def __init__(
        self,
        alert_callback: Optional[
            Callable[[str, str], Awaitable[None]]
        ] = None,
        baseline_score: float = 0.85,
    ):
        self.alert_callback = alert_callback
        self.baseline_score = baseline_score

    async def check_regression(
        self,
        current_score: float,
        threshold: float,
    ) -> None:
        """Check for quality regression"""

        if not 0.0 <= current_score <= 1.0:
            raise ValueError(
                "current_score must be between 0 and 1"
            )

        if threshold < 0:
            raise ValueError(
                "threshold must be non-negative"
            )

        regression = self.baseline_score - current_score

        if regression < threshold:
            return

        severity = (
            "critical"
            if regression >= 0.20
            else "high"
            if regression >= 0.10
            else "medium"
        )

        message = (
            f"RAGAS quality regression detected | "
            f"baseline={self.baseline_score:.4f} | "
            f"current={current_score:.4f} | "
            f"drop={regression:.4f} | "
            f"threshold={threshold:.4f} | "
            f"time={datetime.now(timezone.utc).isoformat()}"
        )

        if self.alert_callback:
            await self.alert_callback(
                severity,
                message,
            )