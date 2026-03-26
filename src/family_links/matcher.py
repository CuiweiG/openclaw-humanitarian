"""
Fuzzy Name Matcher
Handles name variation in Persian, Arabic, and Dari scripts.

Challenges:
- Arabic/Persian names can be transliterated many ways
- Diacritics may or may not be present
- Common prefixes (al-, ibn-, abu-)
"""

import re
from typing import Optional

# Common Arabic/Persian name prefixes to normalize
NAME_PREFIXES = ["al-", "el-", "al ", "el ", "ibn ", "abu ", "bin "]

# Known location aliases
LOCATION_ALIASES = {
    "tehran": ["\u062a\u0647\u0631\u0627\u0646", "tehran", "teheran"],
    "beirut": ["\u0628\u064a\u0631\u0648\u062a", "beirut", "beyrouth"],
    "kabul": ["\u06a9\u0627\u0628\u0644", "kabul"],
    "damascus": ["\u062f\u0645\u0634\u0642", "damascus", "dimashq"],
    "khuzestan": ["\u062e\u0648\u0632\u0633\u062a\u0627\u0646", "khuzestan", "khuzistan"],
    "isfahan": ["\u0627\u0635\u0641\u0647\u0627\u0646", "isfahan", "esfahan"],
}


class FuzzyMatcher:
    """Fuzzy matching engine for names and locations."""

    def normalize_name(self, name: str, language: str = "en") -> str:
        """Normalize a name for matching.

        - Lowercase
        - Remove diacritics (Arabic tashkeel)
        - Remove common prefixes
        - Strip whitespace
        """
        normalized = name.lower().strip()

        # Remove Arabic diacritics (tashkeel): U+064B-U+065F
        normalized = re.sub(r'[\u064B-\u065F]', '', normalized)

        # Remove common prefixes
        for prefix in NAME_PREFIXES:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]

        return normalized.strip()

    def match_score(self, name_a: str, name_b: str) -> float:
        """Calculate match score between two names (0.0 - 1.0).

        Uses character-level similarity (no external dependencies).
        """
        a = self.normalize_name(name_a)
        b = self.normalize_name(name_b)

        if a == b:
            return 1.0

        if not a or not b:
            return 0.0

        # Simple Jaccard similarity on character bigrams
        bigrams_a = set(a[i:i+2] for i in range(len(a)-1))
        bigrams_b = set(b[i:i+2] for i in range(len(b)-1))

        if not bigrams_a or not bigrams_b:
            return 0.0

        intersection = bigrams_a & bigrams_b
        union = bigrams_a | bigrams_b

        return len(intersection) / len(union)

    def location_match(self, loc_a: str, loc_b: str) -> bool:
        """Check if two locations refer to the same area."""
        a_lower = loc_a.lower().strip()
        b_lower = loc_b.lower().strip()

        if a_lower == b_lower:
            return True

        # Check aliases
        for canonical, aliases in LOCATION_ALIASES.items():
            a_match = any(alias in a_lower for alias in aliases) or canonical in a_lower
            b_match = any(alias in b_lower for alias in aliases) or canonical in b_lower
            if a_match and b_match:
                return True

        return False