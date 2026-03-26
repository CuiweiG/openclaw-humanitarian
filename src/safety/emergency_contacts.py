"""
Emergency Contact Database
Verified emergency numbers for crisis-affected countries.

Last verified: 2026-03-27
"""

from typing import List, Dict, Optional

EMERGENCY_CONTACTS: Dict[str, Dict[str, List[dict]]] = {
    "ir": {
        "country": "Iran",
        "police": [{"number": "110", "name": "Police Emergency"}],
        "ambulance": [{"number": "115", "name": "Emergency Medical Services"}],
        "fire": [{"number": "125", "name": "Fire Department"}],
        "redcross": [{"number": "+98-21-88849-077", "name": "Iranian Red Crescent Society"}],
    },
    "lb": {
        "country": "Lebanon",
        "police": [{"number": "112", "name": "ISF Emergency"}],
        "ambulance": [{"number": "140", "name": "Lebanese Red Cross Ambulance"}],
        "fire": [{"number": "175", "name": "Civil Defense"}],
        "redcross": [{"number": "140", "name": "Lebanese Red Cross"}],
        "unhcr": [{"number": "+961-1-849-201", "name": "UNHCR Lebanon"}],
    },
    "af": {
        "country": "Afghanistan",
        "police": [{"number": "119", "name": "Police Emergency"}],
        "ambulance": [{"number": "112", "name": "Emergency Medical"}],
        "fire": [{"number": "119", "name": "Fire/Police Combined"}],
        "redcross": [{"number": "+93-20-230-1401", "name": "Afghan Red Crescent Society"}],
        "unhcr": [{"number": "+93-20-210-1475", "name": "UNHCR Afghanistan"}],
    },
    "sy": {
        "country": "Syria",
        "police": [{"number": "112", "name": "General Emergency"}],
        "ambulance": [{"number": "110", "name": "Ambulance"}],
        "fire": [{"number": "113", "name": "Fire Brigade"}],
        "redcross": [{"number": "+963-11-333-0810", "name": "Syrian Arab Red Crescent"}],
    },
}


def get_emergency_contacts(country_code: str, category: str = "") -> List[dict]:
    """Get emergency contacts for a country.

    Args:
        country_code: ISO 2-letter code (ir, lb, af, sy)
        category: Optional filter (police/ambulance/fire/redcross/unhcr)

    Returns:
        List of contact dicts with 'number' and 'name'
    """
    country = EMERGENCY_CONTACTS.get(country_code.lower(), {})

    if category:
        return country.get(category, [])

    # Return all contacts
    all_contacts = []
    for cat, contacts in country.items():
        if cat == "country":
            continue
        for c in contacts:
            all_contacts.append({**c, "category": cat})
    return all_contacts