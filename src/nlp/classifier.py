"""
Humanitarian Sector Classifier
Classifies extracted information into OCHA standard humanitarian sectors.

Reference: OCHA Coordination Framework — Standard Sector/Cluster System
"""

from typing import Optional

# OCHA Standard Humanitarian Sectors/Clusters
OCHA_SECTORS = {
    'protection': {
        'name': 'Protection',
        'lead': 'UNHCR',
        'keywords': ['protection', 'violence', 'abuse', 'trafficking', 'child protection',
                     'GBV', 'gender-based violence', 'human rights', 'detention', 'displacement'],
    },
    'food_security': {
        'name': 'Food Security',
        'lead': 'WFP / FAO',
        'keywords': ['food', 'hunger', 'malnutrition', 'nutrition', 'ration', 'feeding',
                     'food assistance', 'food distribution', 'IPC', 'famine'],
    },
    'health': {
        'name': 'Health',
        'lead': 'WHO',
        'keywords': ['health', 'medical', 'hospital', 'clinic', 'disease', 'outbreak',
                     'vaccination', 'trauma', 'injury', 'cholera', 'epidemic', 'ambulance'],
    },
    'wash': {
        'name': 'WASH (Water, Sanitation & Hygiene)',
        'lead': 'UNICEF',
        'keywords': ['water', 'sanitation', 'hygiene', 'WASH', 'latrine', 'sewage',
                     'clean water', 'water supply', 'contamination'],
    },
    'shelter': {
        'name': 'Shelter & NFI',
        'lead': 'UNHCR / IFRC',
        'keywords': ['shelter', 'housing', 'collective center', 'camp', 'tent',
                     'blanket', 'NFI', 'non-food items', 'winterization'],
    },
    'education': {
        'name': 'Education',
        'lead': 'UNICEF / Save the Children',
        'keywords': ['education', 'school', 'learning', 'children', 'students',
                     'teacher', 'classroom'],
    },
    'logistics': {
        'name': 'Logistics',
        'lead': 'WFP',
        'keywords': ['logistics', 'supply chain', 'transport', 'cargo', 'warehouse',
                     'pipeline', 'delivery', 'access', 'road'],
    },
    'coordination': {
        'name': 'Coordination',
        'lead': 'OCHA',
        'keywords': ['coordination', 'humanitarian access', 'deconfliction', 'ceasefire',
                     'humanitarian corridor', 'crossing', 'checkpoint'],
    },
}

class SectorClassifier:
    """Classify text into OCHA humanitarian sectors."""
    
    def classify(self, text: str, threshold: int = 2) -> list:
        """Classify text into humanitarian sectors.
        
        Args:
            text: Input text
            threshold: Minimum keyword matches for classification
            
        Returns:
            List of dicts: [{sector, name, lead, confidence, matched_keywords}]
        """
        text_lower = text.lower()
        results = []
        
        for sector_id, sector_info in OCHA_SECTORS.items():
            matched = [kw for kw in sector_info['keywords'] if kw.lower() in text_lower]
            if len(matched) >= threshold:
                results.append({
                    'sector': sector_id,
                    'name': sector_info['name'],
                    'lead_agency': sector_info['lead'],
                    'confidence': min(1.0, len(matched) / 5),
                    'matched_keywords': matched,
                })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)
    
    def get_primary_sector(self, text: str) -> Optional[dict]:
        """Get the most relevant sector for a text."""
        results = self.classify(text, threshold=1)
        return results[0] if results else None
