"""Language detection"""

from __future__ import annotations

import re
from typing import Dict


class LanguageDetector:
    """Detect query language"""

    def __init__(self):
        # lightweight heuristic scripts
        self.scripts = {
            "en": r"[a-zA-Z]",
            "hi": r"[\u0900-\u097F]",
            "ta": r"[\u0B80-\u0BFF]",
            "te": r"[\u0C00-\u0C7F]",
            "zh": r"[\u4E00-\u9FFF]",
            "ja": r"[\u3040-\u30FF\u31F0-\u31FF]",
            "ko": r"[\uAC00-\uD7AF]",
        }

    def detect(self, query: str) -> str:
        """Detect query language"""

        if not query or not query.strip():
            return "unknown"

        scores: Dict[str, int] = {}

        for lang, pattern in self.scripts.items():
            matches = re.findall(pattern, query)
            scores[lang] = len(matches)

        best_lang = max(scores.items(), key=lambda x: x[1])

        lang, score = best_lang

        if score == 0:
            return "unknown"

        # if multiple scripts exist, fallback to multilingual
        non_zero = sum(1 for v in scores.values() if v > 0)

        if non_zero > 1:
            return "multilingual"

        return lang