"""Grounding verification"""

import re
from typing import List


class GroundingVerifier:
    """Verify claims are grounded in source chunks"""

    def verify(self, claim: str, chunks: list) -> bool:
        """Check if claim is grounded in chunks"""

        if not claim or not chunks:
            return False

        claim_tokens = {
            token
            for token in re.findall(r"\w+", claim.lower())
            if len(token) > 3
        }

        if not claim_tokens:
            return False

        for chunk in chunks:
            chunk_tokens = {
                token
                for token in re.findall(r"\w+", str(chunk).lower())
                if len(token) > 3
            }

            overlap = len(claim_tokens & chunk_tokens)
            coverage = overlap / len(claim_tokens)

            if coverage >= 0.7:
                return True

        return False