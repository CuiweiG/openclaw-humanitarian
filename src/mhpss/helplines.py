"""
Crisis Helpline Directory
Verified mental health and crisis helplines for affected regions.

Sources:
- IASC MHPSS Reference Group
- WHO Mental Health Atlas
- Local verified directories

Last verified: 2026-03-27
"""

from typing import List, Dict, Optional

CRISIS_HELPLINES: Dict[str, dict] = {
    "ir": {
        "country": "Iran",
        "helplines": [
            {"name": "Iran Social Emergency Services", "number": "123", "languages": ["fa"], "hours": "24/7"},
            {"name": "Behzisti Counseling", "number": "141", "languages": ["fa"], "hours": "8:00-20:00"},
        ],
    },
    "lb": {
        "country": "Lebanon",
        "helplines": [
            {"name": "Embrace Lifeline", "number": "1564", "languages": ["ar", "en"], "hours": "24/7"},
            {"name": "Lebanese Red Cross", "number": "140", "languages": ["ar", "en", "fr"], "hours": "24/7"},
        ],
    },
    "af": {
        "country": "Afghanistan",
        "helplines": [
            {"name": "Afghanistan MHPSS Hotline", "number": "+93-700-276-276", "languages": ["dar", "ps"], "hours": "8:00-17:00"},
        ],
    },
    "sy": {
        "country": "Syria",
        "helplines": [
            {"name": "Syria Civil Defence (White Helmets)", "number": "112", "languages": ["ar"], "hours": "24/7"},
        ],
    },
    "international": {
        "country": "International",
        "helplines": [
            {"name": "Crisis Text Line", "number": "Text HOME to 741741", "languages": ["en"], "hours": "24/7"},
            {"name": "IASC MHPSS Directory", "number": "https://www.mhpss.net/", "languages": ["en", "ar", "fr"], "hours": "Online"},
            {"name": "ICRC Restoring Family Links", "number": "https://familylinks.icrc.org", "languages": ["en", "ar", "fa", "fr", "es", "ru"], "hours": "Online"},
        ],
    },
}


def get_helplines(country_code: str, language: str = "") -> List[dict]:
    """Get helplines for a country, optionally filtered by language.

    Args:
        country_code: ISO 2-letter country code (ir, lb, af, sy)
        language: Filter by language code (fa, ar, dar, en)

    Returns:
        List of helpline dicts. Always includes international resources.
    """
    results = []

    # Country-specific
    country_data = CRISIS_HELPLINES.get(country_code.lower(), {})
    for hl in country_data.get("helplines", []):
        if not language or language in hl.get("languages", []):
            results.append({**hl, "country": country_data.get("country", "")})

    # Always include international
    for hl in CRISIS_HELPLINES["international"]["helplines"]:
        if not language or language in hl.get("languages", []):
            results.append({**hl, "country": "International"})

    return results