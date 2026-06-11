class CostCalculator:
    """Calculate cost per query."""

    def __init__(self):
        self.pricing = {
            "gpt-4": {
                "input": 0.00001,
                "output": 0.00003
            },
            "gpt-3.5": {
                "input": 0.000001,
                "output": 0.000002
            },
            "embedding": {
                "default": 0.0000001
            }
        }

    def calculate(self, tokens: dict) -> float:

        model = tokens.get("model", "gpt-3.5")

        input_tokens = tokens.get("input_tokens", 0)
        output_tokens = tokens.get("output_tokens", 0)
        embedding_tokens = tokens.get("embedding_tokens", 0)

        model_pricing = self.pricing.get(
            model,
            self.pricing["gpt-3.5"]
        )

        input_cost = input_tokens * model_pricing["input"]
        output_cost = output_tokens * model_pricing["output"]
        embedding_cost = embedding_tokens * self.pricing["embedding"]["default"]

        return round(
            input_cost + output_cost + embedding_cost,
            6
        )