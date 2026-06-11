"""Alert manager"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import aiohttp


class AlertManager:
    """Send alerts to PagerDuty/Slack"""

    SEVERITIES = {"critical", "high", "medium", "low"}

    def __init__(
        self,
        slack_webhook_url: Optional[str] = None,
        pagerduty_integration_key: Optional[str] = None,
        service_name: str = "rag-platform",
    ):
        self.slack_webhook_url = slack_webhook_url
        self.pagerduty_integration_key = pagerduty_integration_key
        self.service_name = service_name
        self.logger = logging.getLogger(__name__)

    async def alert(self, severity: str, message: str) -> None:
        """Send alert"""

        severity = severity.lower().strip()

        if severity not in self.SEVERITIES:
            raise ValueError(
                f"severity must be one of {self.SEVERITIES}"
            )

        if not message:
            raise ValueError("message cannot be empty")

        tasks = []

        if self.slack_webhook_url:
            tasks.append(
                self._send_slack_alert(
                    severity=severity,
                    message=message,
                )
            )

        if (
            self.pagerduty_integration_key
            and severity in {"critical", "high"}
        ):
            tasks.append(
                self._send_pagerduty_alert(
                    severity=severity,
                    message=message,
                )
            )

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self.logger.warning(
            "[%s] %s",
            severity.upper(),
            message,
        )

    async def _send_slack_alert(
        self,
        severity: str,
        message: str,
    ) -> None:
        payload = {
            "text": (
                f"🚨 [{severity.upper()}] "
                f"{self.service_name}\n{message}"
            )
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.slack_webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()

    async def _send_pagerduty_alert(
        self,
        severity: str,
        message: str,
    ) -> None:
        payload = {
            "routing_key": self.pagerduty_integration_key,
            "event_action": "trigger",
            "payload": {
                "summary": message,
                "severity": (
                    "critical"
                    if severity == "critical"
                    else "error"
                ),
                "source": self.service_name,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()