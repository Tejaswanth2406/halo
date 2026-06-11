"""
Evaluation gate for CI/CD
"""


class EvalGate:
    """Block deployment if evaluation metrics drop."""

    MAX_DROP_PERCENT = 5.0

    async def check_gate(
        self,
        current_score: float,
        baseline: float
    ) -> bool:
        """
        Returns:
            True  -> deploy allowed
            False -> deploy blocked
        """

        if baseline <= 0:
            raise ValueError(
                "Baseline must be > 0"
            )

        drop_percent = (
            (baseline - current_score)
            / baseline
        ) * 100

        return (
            drop_percent
            <= self.MAX_DROP_PERCENT
        )