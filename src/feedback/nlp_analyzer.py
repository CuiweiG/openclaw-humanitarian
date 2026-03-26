"""
Feedback NLP Analyzer
Applies NLP to community feedback reports to extract structured needs data.

References:
- Kreutzer et al. 2020 (IBM/WFP) "Improving Humanitarian Needs Assessments through NLP"
- Otal & Canbaz 2024 "LLM-Assisted Crisis Management"
"""

import re
from typing import Optional

class FeedbackAnalyzer:
    """Analyze community feedback using NLP techniques."""
    
    NEED_PATTERNS = {
        'shelter': [r'shelter', r'no.*(?:house|home|roof)', r'sleep.*(?:street|outside)', r'displaced'],
        'food': [r'hungry', r'no.*food', r'starving', r'no.*eat', r'ration'],
        'water': [r'no.*water', r'thirsty', r'dirty.*water', r'contaminated'],
        'medical': [r'injur', r'sick', r'hospital', r'doctor', r'medicine', r'wound', r'bleed'],
        'safety': [r'danger', r'attack', r'bomb', r'shoot', r'threat', r'fear'],
        'electricity': [r'no.*power', r'no.*electric', r'blackout', r'dark'],
        'communication': [r'no.*internet', r'no.*phone', r'cannot.*call', r'offline'],
    }
    
    URGENCY_SIGNALS = {
        'critical': [r'dying', r'bleeding', r'trapped', r'under.*rubble', r'no.*breathe'],
        'high': [r'urgent', r'emergency', r'please.*help', r'desperate', r'critical'],
        'moderate': [r'need', r'running.*out', r'limited', r'difficult'],
        'low': [r'concerned', r'worried', r'would.*like', r'request'],
    }

    def analyze(self, text: str, language: str = 'en') -> dict:
        """Analyze a feedback report text.
        
        Returns:
            {needs: list, urgency: str, estimated_people: int|None,
             location_mentioned: str|None, key_phrases: list}
        """
        text_lower = text.lower()
        
        return {
            'needs': self._detect_needs(text_lower),
            'urgency': self._assess_urgency(text_lower),
            'estimated_people': self._extract_people_count(text),
            'location_mentioned': self._extract_location(text),
            'key_phrases': self._extract_key_phrases(text_lower),
        }
    
    def _detect_needs(self, text: str) -> list:
        detected = []
        for need, patterns in self.NEED_PATTERNS.items():
            for p in patterns:
                if re.search(p, text, re.IGNORECASE):
                    detected.append(need)
                    break
        return detected
    
    def _assess_urgency(self, text: str) -> str:
        for level in ['critical', 'high', 'moderate', 'low']:
            for p in self.URGENCY_SIGNALS[level]:
                if re.search(p, text, re.IGNORECASE):
                    return level
        return 'moderate'
    
    def _extract_people_count(self, text: str) -> int:
        patterns = [
            r'(\d+)\s*(?:people|persons|families|children|women|men)',
            r'(?:about|approximately|around)\s*(\d+)',
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_location(self, text: str) -> str:
        # Simple location extraction
        location_patterns = [
            r'(?:in|at|near|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        for p in location_patterns:
            match = re.search(p, text)
            if match:
                return match.group(1)
        return None
    
    def _extract_key_phrases(self, text: str) -> list:
        # Extract phrases that indicate specific needs
        phrases = []
        important_patterns = [
            r'no\s+\w+', r'need\s+\w+', r'running\s+out\s+of\s+\w+',
            r'cannot\s+\w+', r'lost\s+\w+',
        ]
        for p in important_patterns:
            matches = re.findall(p, text)
            phrases.extend(matches)
        return phrases[:5]
