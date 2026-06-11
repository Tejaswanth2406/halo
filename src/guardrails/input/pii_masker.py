"""PII masking before LLM sees query"""

import re


class PIIMasker:
    """Mask PII in user queries"""

    def mask(self, query: str) -> str:
        """Mask PII in query"""

        if not query:
            return query

        patterns = {
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b": "[EMAIL]",
            r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{10})\b": "[PHONE]",
            r"\b(?:\d[ -]*?){13,19}\b": "[CARD]",
            r"\b\d{3}-\d{2}-\d{4}\b": "[SSN]",
            r"\b(?:\d{4}[ -]?){3}\d{4}\b": "[CARD]",
            r"\b[A-Z]{5}[0-9]{4}[A-Z]\b": "[PAN]",
            r"\b\d{12}\b": "[AADHAAR]",
            r"\b\d{6}\b": "[PINCODE]",
        }

        masked = query

        for pattern, replacement in patterns.items():
            masked = re.sub(
                pattern,
                replacement,
                masked,
                flags=re.IGNORECASE,
            )

        return masked
