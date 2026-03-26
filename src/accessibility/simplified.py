"""
Simplified Language Generator
Makes humanitarian bulletins accessible to low-literacy populations.

Uses emoji markers for universal understanding:
- Medical: hospital/health/doctor
- Food: hunger/ration
- Water: wash
- Shelter: housing/camp
- Danger: warning/evacuate/attack
"""

import re
from typing import Optional

EMOJI_MAP = {
    "medical": "\U0001F3E5",
    "hospital": "\U0001F3E5",
    "health": "\U0001F3E5",
    "doctor": "\U0001F3E5",
    "food": "\U0001F35E",
    "hunger": "\U0001F35E",
    "ration": "\U0001F35E",
    "water": "\U0001F4A7",
    "wash": "\U0001F4A7",
    "shelter": "\U0001F3E0",
    "housing": "\U0001F3E0",
    "camp": "\U0001F3E0",
    "danger": "\u26A0\uFE0F",
    "warning": "\u26A0\uFE0F",
    "evacuate": "\u26A0\uFE0F",
    "attack": "\u26A0\uFE0F",
    "displaced": "\U0001F6B6",
    "refugee": "\U0001F6B6",
    "children": "\U0001F476",
    "phone": "\U0001F4DE",
    "help": "\U0001F198",
}


class SimplifiedLanguage:
    """Generate simplified versions of humanitarian text."""

    def simplify(self, text: str, language: str = "en", target_level: str = "basic") -> str:
        """Simplify text for low-literacy readers.

        Args:
            text: Original text
            language: Target language
            target_level: 'basic' (primary school) or 'intermediate'

        Returns:
            Simplified text with emoji markers
        """
        simplified = text

        # Split into short sentences
        simplified = re.sub(r'([.!?])\s+', r'\1\n', simplified)

        # Remove parenthetical information
        simplified = re.sub(r'\([^)]+\)', '', simplified)

        # Remove source citations for basic level
        if target_level == "basic":
            simplified = re.sub(r'Source:.*?(?:\n|$)', '', simplified)
            simplified = re.sub(r'\*[^*]+\*', '', simplified)

        return simplified.strip()

    def add_emoji_markers(self, text: str) -> str:
        """Add emoji markers next to key humanitarian terms.

        Example: "food distribution" -> "food distribution"
        """
        result = text
        for keyword, emoji in EMOJI_MAP.items():
            # Add emoji before the keyword (case-insensitive)
            pattern = re.compile(rf'\b({keyword})\b', re.IGNORECASE)
            result = pattern.sub(rf'{emoji} \1', result)

        return result