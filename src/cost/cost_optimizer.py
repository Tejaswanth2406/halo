class CostOptimizer:

    def __init__(self, budget_controller, cost_calculator):
        self.budget_controller = budget_controller
        self.cost_calculator = cost_calculator

    def estimate_complexity(self, query: str) -> float:
        """Very simple heuristic complexity score."""

        score = 0

        if "why" in query.lower():
            score += 1
        if "compare" in query.lower():
            score += 2
        if len(query.split()) > 20:
            score += 1
        if "explain" in query.lower():
            score += 1

        return score

    def optimize_routing(self, query: str) -> dict:

        complexity = self.estimate_complexity(query)

        # default assumptions
        model = "gpt-3.5"
        retrieval_depth = 3

        if complexity <= 1:
            model = "gpt-3.5"
        elif complexity <= 3:
            model = "gpt-4-mini"
        else:
            model = "gpt-4"

        return {
            "model": model,
            "retrieval_depth": retrieval_depth,
            "complexity": complexity
        }