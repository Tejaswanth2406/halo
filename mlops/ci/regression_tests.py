"""
Regression tests on golden dataset.
"""

from typing import Dict, List


class RegressionTests:
    """Test retrieval quality against golden dataset."""

    async def run_tests(
        self,
        golden_dataset: List[dict]
    ) -> Dict:
        """
        Run regression tests.

        Expected format:
        [
            {
                "question": "...",
                "expected_answer": "...",
                "predicted_answer": "..."
            }
        ]
        """

        total = len(golden_dataset)

        passed = 0

        results = []

        for sample in golden_dataset:

            expected = (
                sample["expected_answer"]
                .lower()
                .strip()
            )

            predicted = (
                sample["predicted_answer"]
                .lower()
                .strip()
            )

            success = (
                expected in predicted
            )

            if success:
                passed += 1

            results.append(
                {
                    "question":
                        sample["question"],
                    "passed":
                        success
                }
            )

        accuracy = (
            passed / total
            if total > 0
            else 0.0
        )

        return {
            "accuracy": accuracy,
            "passed": passed,
            "total": total,
            "results": results,
        }