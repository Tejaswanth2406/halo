"""
Shadow mode for silent evaluation
"""

from datetime import datetime


class ShadowMode:
    """Run new model silently for evaluation."""

    def __init__(
        self,
        production_pipeline,
        shadow_pipeline,
        metrics_store=None
    ):
        self.production_pipeline = (
            production_pipeline
        )

        self.shadow_pipeline = (
            shadow_pipeline
        )

        self.metrics_store = metrics_store

    async def run_shadow(
        self,
        query: str,
        new_model: str
    ) -> dict:
        """
        Execute shadow model and record results.
        """

        production_response = (
            await self.production_pipeline.ask(
                query
            )
        )

        shadow_response = (
            await self.shadow_pipeline.ask(
                query,
                model=new_model
            )
        )

        result = {
            "timestamp":
                datetime.utcnow().isoformat(),

            "query":
                query,

            "production_response":
                production_response,

            "shadow_response":
                shadow_response,

            "shadow_model":
                new_model,
        }

        if self.metrics_store:
            await self.metrics_store.save(
                result
            )

        return result