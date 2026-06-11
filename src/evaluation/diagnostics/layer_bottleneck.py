"""Layer bottleneck diagnostics"""

from typing import Dict, Any


class LayerBottleneckDetector:
    """Detect which layer caused RAGAS drop"""

    async def diagnose(self, before_metrics: dict, after_metrics: dict) -> dict:
        """Diagnose performance drop"""

        deltas = {}
        for metric, before_value in before_metrics.items():
            after_value = after_metrics.get(metric, before_value)

            try:
                deltas[metric] = round(after_value - before_value, 4)
            except (TypeError, ValueError):
                continue

        if not deltas:
            return {
                "status": "insufficient_data",
                "bottleneck_layer": None,
                "impact_score": 0.0,
                "metric_deltas": {},
            }

        bottleneck_metric = min(deltas, key=deltas.get)
        impact_score = abs(min(0.0, deltas[bottleneck_metric]))

        layer_mapping = {
            "context_precision": "retrieval",
            "context_recall": "retrieval",
            "faithfulness": "generation",
            "answer_relevancy": "generation",
            "noise_sensitivity": "reranking",
            "semantic_similarity": "embedding",
        }

        bottleneck_layer = layer_mapping.get(
            bottleneck_metric,
            "unknown",
        )

        return {
            "status": "diagnosed",
            "bottleneck_layer": bottleneck_layer,
            "root_metric": bottleneck_metric,
            "impact_score": round(impact_score, 4),
            "metric_deltas": deltas,
            "severity": (
                "critical"
                if impact_score >= 0.20
                else "high"
                if impact_score >= 0.10
                else "medium"
                if impact_score >= 0.05
                else "low"
            ),
        }