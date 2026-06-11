"""
Drift detector using Evidently AI
"""

import pandas as pd
from evidently.report import Report
from evidently.presets import DataDriftPreset


class DriftDetector:
    """Detect data drift."""

    def detect_drift(
        self,
        current_data: list,
        baseline_data: list
    ) -> bool:
        """
        Returns:
            True  -> drift detected
            False -> no drift
        """

        current_df = pd.DataFrame(
            current_data
        )

        baseline_df = pd.DataFrame(
            baseline_data
        )

        report = Report(
            metrics=[
                DataDriftPreset()
            ]
        )

        report.run(
            reference_data=baseline_df,
            current_data=current_df
        )

        result = report.as_dict()

        return result["metrics"][0][
            "result"
        ]["dataset_drift"]