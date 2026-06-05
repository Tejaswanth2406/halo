"""Quality regression alerter"""

class QualityRegressionAlert:
    """Alert on RAGAS drop"""
    
    async def check_regression(self, current_score: float, threshold: float) -> None:
        """Check for quality regression"""
        pass
