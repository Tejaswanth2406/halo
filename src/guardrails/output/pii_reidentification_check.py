"""PII re-identification check on output"""

from __future__ import annotations

import re
from typing import List, Dict, Any


class PIIReidentificationCheck:
    """Detect PII leakage in outputs"""

    _PATTERNS = {
        "email": re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        "phone": re.compile(
            r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4,6}"
        ),
        "credit_card": re.compile(
            r"\b(?:\d[ -]*?){13,19}\b"
        ),
        "aadhaar": re.compile(
            r"\b\d{4}\s?\d{4}\s?\d{4}\b"
        ),
        "pan": re.compile(
            r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
        ),
        "passport": re.compile(
            r"\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b"
        ),
        "ipv4": re.compile(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ),
        "ipv6": re.compile(
            r"\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b"
        ),
        "ssn": re.compile(
            r"\b\d{3}-\d{2}-\d{4}\b"
        ),
        "bank_account": re.compile(
            r"\b\d{9,18}\b"
        ),
        "upi_id": re.compile(
            r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b"
        ),
        "api_key": re.compile(
            r"\b(?:sk-|pk_|AKIA|AIza)[A-Za-z0-9_\-]{12,}\b"
        ),
        "jwt_token": re.compile(
            r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+\b"
        ),
    }

    def check(self, response: str) -> List[Dict[str, Any]]:
        """Find PII in response"""

        if not response:
            return []

        findings: List[Dict[str, Any]] = []

        for pii_type, pattern in self._PATTERNS.items():
            for match in pattern.finditer(response):
                value = match.group(0)

                findings.append(
                    {
                        "type": pii_type,
                        "severity": self._severity(pii_type),
                        "start": match.start(),
                        "end": match.end(),
                        "value": self._mask(value),
                    }
                )

        findings.sort(
            key=lambda x: (
                {"critical": 0, "high": 1, "medium": 2, "low": 3}[x["severity"]],
                x["start"],
            )
        )

        return findings

    @staticmethod
    def _mask(value: str) -> str:
        if len(value) <= 6:
            return "*" * len(value)

        return f"{value[:3]}{'*' * (len(value) - 6)}{value[-3:]}"

    @staticmethod
    def _severity(pii_type: str) -> str:
        critical = {
            "credit_card",
            "aadhaar",
            "pan",
            "passport",
            "api_key",
            "jwt_token",
            "bank_account",
        }

        high = {
            "email",
            "phone",
            "upi_id",
        }

        if pii_type in critical:
            return "critical"

        if pii_type in high:
            return "high"

        return "medium"