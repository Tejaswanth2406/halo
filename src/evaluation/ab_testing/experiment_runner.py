class ExperimentRunner:

    def __init__(self, metrics_store):
        self.metrics_store = metrics_store

    def assign_variant(self, user_id: str, split: dict) -> str:
        """
        split example:
        {
            "A": 0.5,
            "B": 0.5
        }
        """

        value = hash(user_id) % 100

        return "A" if value < split["A"] * 100 else "B"

    async def run_experiment(self, experiment_config: dict) -> dict:

        user_id = experiment_config["user_id"]
        split = experiment_config.get("split", {"A": 0.5, "B": 0.5})

        variant = self.assign_variant(user_id, split)

        return {
            "variant": variant,
            "experiment_id": experiment_config.get("id"),
            "params": experiment_config.get("params", {})
        }

    def log_result(self, experiment_id: str, variant: str, metrics: dict) -> None:
        """Store evaluation results."""

        self.metrics_store.append({
            "experiment_id": experiment_id,
            "variant": variant,
            "metrics": metrics
        })