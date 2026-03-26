"""
Community Feedback Collector
Collects anonymized reports from affected civilians via Telegram.
Strictly follows ICRC data protection principles.

Privacy guarantees:
- No user IDs stored
- No phone numbers recorded
- Location at district level only (not coordinates)
- Reports anonymized immediately upon submission
"""

import hashlib
import json
from datetime import datetime
from typing import Optional

class FeedbackCollector:
    """Collect and anonymize community reports."""
    
    VALID_NEED_TYPES = [
        'shelter', 'food', 'water', 'medical', 'safety',
        'electricity', 'communication', 'transport', 'other',
    ]
    
    def process_report(
        self,
        district: str,
        need_type: str,
        description: str,
        language: str = 'en',
    ) -> dict:
        """Process a community report with immediate anonymization.
        
        Args:
            district: District-level location (NOT coordinates)
            need_type: Type of need (from VALID_NEED_TYPES)
            description: Free-text description
            language: Language of the description
            
        Returns:
            Anonymized report dict (no user-identifiable information)
        """
        if need_type not in self.VALID_NEED_TYPES:
            need_type = 'other'
        
        # Generate anonymous report ID (NOT linked to any user)
        report_id = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}:{district}:{description[:20]}".encode()
        ).hexdigest()[:12]
        
        return {
            'report_id': report_id,
            'district': district.strip(),
            'need_type': need_type,
            'description': description[:500],  # Limit length
            'language': language,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'new',
            # NO user_id, NO phone, NO coordinates, NO IP
        }
