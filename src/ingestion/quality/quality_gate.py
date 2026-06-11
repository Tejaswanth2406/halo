"""
Quality gate orchestration
"""

from src.ingestion.quality.quality_scorer import QualityScorer
from src.ingestion.quality.pii_scrubber import PIIScrubber


class QualityGate:
    """Orchestrate all quality checks."""

    MIN_TEXT_LENGTH = 50
    MIN_QUALITY_SCORE = 0.5

    def __init__(self):
        self.quality_scorer = QualityScorer()
        self.pii_scrubber = PIIScrubber()

    def check_document(
        self,
        document: dict
    ) -> bool:
        """
        Run quality checks on document.

        Expected format:
        {
            "text": "..."
        }
        """

        text = document.get(
            "text",
            ""
        )

        # Empty document
        if not text:
            return False

        # Tiny documents usually useless
        if len(text.strip()) < self.MIN_TEXT_LENGTH:
            return False

        # Content quality check
        score = self.quality_scorer.score(
            text
        )

        if score < self.MIN_QUALITY_SCORE:
            return False

        return True
