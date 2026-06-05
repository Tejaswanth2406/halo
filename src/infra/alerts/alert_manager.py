"""Alert manager"""

class AlertManager:
    """Send alerts to PagerDuty/Slack"""
    
    async def alert(self, severity: str, message: str) -> None:
        """Send alert"""
        pass
