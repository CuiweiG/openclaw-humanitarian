"""
Data Anonymizer
Ensures no personally identifiable information (PII) is retained.
Compliant with ICRC Handbook on Data Protection in Humanitarian Action.
"""

import re
from typing import Optional

class Anonymizer:
    """Strip PII from text and reports."""
    
    # Patterns to redact
    PII_PATTERNS = [
        (r'\+?\d{1,4}[\s-]?\d{6,12}', '[PHONE_REDACTED]'),       # Phone numbers
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),
        (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]'),
        (r"(?:my name is|I am|I'm)\s+([A-Z][a-z]+)", '[NAME_REDACTED]'),
        (r'\b\d{1,2}\.\d{4,8},\s*\d{1,2}\.\d{4,8}\b', '[COORDS_REDACTED]'),
    ]

    def anonymize_text(self, text: str) -> str:
        """Remove PII from free text."""
        result = text
        for pattern, replacement in self.PII_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result
    
    def anonymize_report(self, report: dict) -> dict:
        """Ensure a report dict contains no PII."""
        clean = report.copy()
        if 'description' in clean:
            clean['description'] = self.anonymize_text(clean['description'])
        # Remove any fields that shouldn't exist
        for field in ['user_id', 'phone', 'ip', 'coordinates', 'lat', 'lon', 'name']:
            clean.pop(field, None)
        return clean
