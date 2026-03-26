"""
Humanitarian Named Entity Recognition
Identifies locations, organizations, and key entities in crisis reports.
Optimized for Middle East crisis context with Arabic/Persian name handling.
"""

import re
from typing import Optional

# Known humanitarian organizations
KNOWN_ORGS = {
    'OCHA': 'UN Office for the Coordination of Humanitarian Affairs',
    'WFP': 'World Food Programme',
    'UNHCR': "UN High Commissioner for Refugees",
    'UNICEF': "UN Children's Fund",
    'WHO': 'World Health Organization',
    'ICRC': 'International Committee of the Red Cross',
    'IFRC': 'International Federation of Red Cross',
    'IOM': 'International Organization for Migration',
    'MSF': 'Médecins Sans Frontières',
    'IRC': 'International Rescue Committee',
    'FAO': 'Food and Agriculture Organization',
    'UNRWA': 'UN Relief and Works Agency',
}

# Known crisis-relevant locations (expandable)
KNOWN_LOCATIONS = {
    # Countries
    'Iran': {'type': 'country', 'iso': 'IRN', 'region': 'Middle East'},
    'Lebanon': {'type': 'country', 'iso': 'LBN', 'region': 'Middle East'},
    'Syria': {'type': 'country', 'iso': 'SYR', 'region': 'Middle East'},
    'Afghanistan': {'type': 'country', 'iso': 'AFG', 'region': 'Central Asia'},
    'Iraq': {'type': 'country', 'iso': 'IRQ', 'region': 'Middle East'},
    'Yemen': {'type': 'country', 'iso': 'YEM', 'region': 'Middle East'},
    # Major cities
    'Tehran': {'type': 'city', 'country': 'Iran', 'region': 'Tehran Province'},
    'Beirut': {'type': 'city', 'country': 'Lebanon', 'region': 'Beirut'},
    'Damascus': {'type': 'city', 'country': 'Syria', 'region': 'Damascus'},
    'Kabul': {'type': 'city', 'country': 'Afghanistan', 'region': 'Kabul'},
    'Khuzestan': {'type': 'province', 'country': 'Iran', 'region': 'Southwest'},
    'Tripoli': {'type': 'city', 'country': 'Lebanon', 'region': 'North'},
    'Sidon': {'type': 'city', 'country': 'Lebanon', 'region': 'South'},
    'Tyre': {'type': 'city', 'country': 'Lebanon', 'region': 'South'},
}

class HumanitarianNER:
    """Named Entity Recognition for humanitarian reports."""
    
    def extract_entities(self, text: str) -> dict:
        """Extract named entities from text.
        
        Returns:
            {organizations: [...], locations: [...], dates: [...]}
        """
        return {
            'organizations': self._find_organizations(text),
            'locations': self._find_locations(text),
            'dates': self._find_dates(text),
        }

    def _find_organizations(self, text: str) -> list:
        found = []
        for abbrev, full_name in KNOWN_ORGS.items():
            if abbrev in text or full_name.lower() in text.lower():
                found.append({'abbreviation': abbrev, 'full_name': full_name})
        return found

    def _find_locations(self, text: str) -> list:
        found = []
        for name, info in KNOWN_LOCATIONS.items():
            if name.lower() in text.lower():
                found.append({'name': name, **info})
        return found

    def _find_dates(self, text: str) -> list:
        patterns = [
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'\d{4}-\d{2}-\d{2}',
        ]
        dates = []
        for p in patterns:
            dates.extend(re.findall(p, text))
        return list(set(dates))
