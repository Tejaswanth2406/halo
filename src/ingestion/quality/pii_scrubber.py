from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


class PIIScrubber:
    """Detect and remove PII from documents."""

    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def scrub(self, text: str) -> str:
        """
        Replace detected PII with placeholders.
        """

        if not text:
            return ""

        results = self.analyzer.analyze(
            text=text,
            language="en"
        )

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results
        )

        return anonymized.text

    def contains_pii(self, text: str) -> bool:
        """
        Check whether text contains PII.
        """

        results = self.analyzer.analyze(
            text=text,
            language="en"
        )

        return len(results) > 0