"""
Crisis Information Extractor
Automatically extracts structured humanitarian data from unstructured reports.

References:
- Rocca et al. 2023 "NLP for Humanitarian Action" (Frontiers in Big Data)
- IBM/WFP 2020 "Improving Humanitarian Needs Assessments through NLP"
"""

import re
import json
from typing import Optional

class CrisisExtractor:
    """Extract crisis-relevant information from humanitarian reports."""
    
    # Patterns for common humanitarian data points
    CASUALTY_PATTERNS = [
        r'(\d[\d,]*)\s*(?:people\s+)?(?:killed|dead|deaths|casualties|fatalities)',
        r'(\d[\d,]*)\s*(?:people\s+)?(?:injured|wounded|hurt)',
        r'death\s+toll\s+(?:of\s+)?(\d[\d,]*)',
    ]
    
    DISPLACEMENT_PATTERNS = [
        r'(\d[\d,.]*\s*(?:million|M))\s*(?:people\s+)?(?:displaced|fled|evacuated)',
        r'(\d[\d,]*)\s*(?:households?|families)\s*(?:displaced|fled|evacuated)',
        r'(?:displaced|IDPs?|refugees?)\s*(?:of\s+)?(\d[\d,.]*\s*(?:million|thousand|M|K)?)',
    ]
    
    LOCATION_PATTERNS = [
        r'(?:in|across|throughout)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    NEED_KEYWORDS = {
        'food': ['food', 'hunger', 'malnutrition', 'ration', 'feeding', 'WFP'],
        'water': ['water', 'WASH', 'sanitation', 'hygiene', 'cholera'],
        'shelter': ['shelter', 'housing', 'displacement', 'camp', 'collective center'],
        'health': ['medical', 'hospital', 'health', 'injury', 'trauma', 'WHO'],
        'protection': ['protection', 'violence', 'abuse', 'trafficking', 'UNHCR'],
    }
    
    URGENCY_KEYWORDS = {
        'critical': ['urgent', 'critical', 'emergency', 'immediate', 'life-saving', 'dire'],
        'high': ['severe', 'acute', 'escalating', 'deteriorating', 'alarming'],
        'moderate': ['concern', 'challenging', 'significant', 'growing'],
        'low': ['stable', 'improving', 'moderate', 'gradual'],
    }

    def extract(self, text: str) -> dict:
        """Extract structured crisis information from text.
        
        Args:
            text: Raw report text in English
            
        Returns:
            Dictionary with extracted fields:
            - casualties: {killed: int, injured: int}
            - displacement: {count: str, unit: str}
            - locations: list[str]
            - needs: list[str] (OCHA sector codes)
            - urgency: str (critical/high/moderate/low)
            - key_numbers: list[{value, context}]
        """
        return {
            'casualties': self._extract_casualties(text),
            'displacement': self._extract_displacement(text),
            'locations': self._extract_locations(text),
            'needs': self._classify_needs(text),
            'urgency': self._assess_urgency(text),
            'key_numbers': self._extract_numbers(text),
        }

    def _extract_casualties(self, text: str) -> dict:
        killed, injured = 0, 0
        for pattern in self.CASUALTY_PATTERNS[:3]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                num = int(match.group(1).replace(',', ''))
                if any(w in match.group(0).lower() for w in ['killed', 'dead', 'death']):
                    killed = max(killed, num)
                else:
                    injured = max(injured, num)
        return {'killed': killed, 'injured': injured}

    def _extract_displacement(self, text: str) -> dict:
        for pattern in self.DISPLACEMENT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                return {'count': value, 'raw_match': match.group(0)}
        return {'count': '0', 'raw_match': ''}

    def _extract_locations(self, text: str) -> list:
        # Known crisis locations for validation
        known = ['Iran', 'Lebanon', 'Syria', 'Afghanistan', 'Iraq', 'Yemen',
                 'Beirut', 'Tehran', 'Kabul', 'Damascus', 'Khuzestan', 'Tripoli']
        found = []
        for loc in known:
            if loc.lower() in text.lower():
                found.append(loc)
        return list(set(found))

    def _classify_needs(self, text: str) -> list:
        text_lower = text.lower()
        sectors = []
        for sector, keywords in self.NEED_KEYWORDS.items():
            if any(kw.lower() in text_lower for kw in keywords):
                sectors.append(sector)
        return sectors

    def _assess_urgency(self, text: str) -> str:
        text_lower = text.lower()
        for level in ['critical', 'high', 'moderate', 'low']:
            if any(kw in text_lower for kw in self.URGENCY_KEYWORDS[level]):
                return level
        return 'moderate'

    def _extract_numbers(self, text: str) -> list:
        """Extract all significant numbers with surrounding context."""
        results = []
        for match in re.finditer(r'(\d[\d,]*(?:\.\d+)?)\s*(million|thousand|M|K|%)?', text):
            value = match.group(0)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            results.append({'value': value, 'context': context})
        return results[:10]  # Top 10 numbers
