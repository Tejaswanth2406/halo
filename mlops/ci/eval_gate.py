"""Evaluation gate for CI/CD"""

class EvalGate:
    """Block deploy if RAGAS drops"""
    
    async def check_gate(self, current_score: float, baseline: float) -> bool:
        """Check if metrics pass gate"""
        pass
