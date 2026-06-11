"""Emerging Benchmark: Latency-Quality Tradeoff Curve (LQTC)"""

from __future__ import annotations

from typing import List, Dict, Any
import time
import asyncio


class LatencyQualityTradeoffCurve:
    """
    Measure: How does response quality degrade with time constraints?
    Importance: Production systems must trade quality for speed
    Framework: Maps latency budgets to achievable quality scores
    """

    def __init__(self, pipeline=None, quality_scorer=None):
        """
        pipeline: async function(query, config)->response
        quality_scorer: function(query, response)->float
        """
        self.pipeline = pipeline
        self.quality_scorer = quality_scorer

    async def evaluate(self, query: str, latency_budgets: list) -> dict:
        """Evaluate quality at different latency constraints"""

        if not query or not latency_budgets:
            return {"lqtc": {}, "curve": []}

        results = {}
        curve = []

        for budget_ms in sorted(latency_budgets):
            start = time.perf_counter()

            response = await self._run_with_budget(query, budget_ms)

            latency = (time.perf_counter() - start) * 1000.0
            quality = self._score_quality(query, response)

            point = {
                "latency_budget_ms": budget_ms,
                "actual_latency_ms": latency,
                "quality": quality,
                "response": response,
            }

            curve.append(point)
            results[budget_ms] = quality

        return {
            "lqtc": results,
            "curve": curve,
            "best_quality": max(results.values()) if results else 0.0,
            "worst_quality": min(results.values()) if results else 0.0,
        }

    async def _run_with_budget(self, query: str, budget_ms: int):
        """
        Simulate latency-constrained execution.
        Real systems would truncate retrieval/reranking depth.
        """

        if self.pipeline:
            try:
                # pass budget hint into pipeline if supported
                result = self.pipeline(query, {"latency_budget_ms": budget_ms})

                if hasattr(result, "__await__"):
                    return await result

                return result
            except Exception:
                pass

        # fallback simulated response
        await asyncio.sleep(min(budget_ms / 1000.0, 0.01))
        return f"Simulated response under {budget_ms}ms budget"

    def _score_quality(self, query: str, response: Any) -> float:
        """
        Compute quality score using external scorer or heuristic fallback.
        """

        if self.quality_scorer:
            try:
                return float(self.quality_scorer(query, response))
            except Exception:
                pass

        if not response:
            return 0.0

        text = str(response).lower()
        q_tokens = set(query.lower().split())
        r_tokens = set(text.split())

        if not q_tokens:
            return 0.0

        return len(q_tokens & r_tokens) / len(q_tokens)