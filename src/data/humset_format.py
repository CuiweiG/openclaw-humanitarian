"""
HumSet-Compatible Data Format
Outputs structured humanitarian data in a format compatible with
the HumSet benchmark dataset (Frontiers in Big Data).

This enables interoperability with academic research tools
and UN information management systems.
"""

import json
import hashlib
from datetime import datetime
from typing import Optional

class HumSetFormatter:
    """Format extracted data in HumSet-compatible JSON."""
    
    VERSION = "1.0"
    
    def format_entry(
        self,
        text: str,
        language: str,
        source_url: str,
        sectors: list,
        severity: str = "moderate",
        confidence: float = 0.0,
        extraction_date: Optional[str] = None,
        original_title: str = "",
        source_org: str = "",
    ) -> dict:
        """Create a HumSet-compatible entry.
        
        Args:
            text: Extracted/translated text
            language: ISO 639-1 language code
            source_url: URL of the original report
            sectors: List of OCHA sector codes
            severity: Urgency level (critical/high/moderate/low)
            confidence: AI confidence score (0.0-1.0)
            extraction_date: ISO date string (defaults to now)
            original_title: Title of the source document
            source_org: Publishing organization
            
        Returns:
            HumSet-compatible dictionary
        """
        doc_id = hashlib.sha256(
            f"{source_url}:{language}:{text[:100]}".encode()
        ).hexdigest()[:16]
        
        return {
            "document_id": doc_id,
            "text": text,
            "language": language,
            "original_title": original_title,
            "source_url": source_url,
            "source_organization": source_org,
            "sectors": sectors,
            "severity": severity,
            "confidence_score": round(confidence, 3),
            "extraction_date": extraction_date or datetime.utcnow().isoformat(),
            "format_version": self.VERSION,
            "generator": "crisisbridge",
            "license": "MIT",
        }
    
    def to_json(self, entries: list, indent: int = 2) -> str:
        """Serialize entries to JSON string."""
        return json.dumps({
            "metadata": {
                "format": "humset-compatible",
                "version": self.VERSION,
                "generator": "crisisbridge",
                "generated_at": datetime.utcnow().isoformat(),
                "entry_count": len(entries),
            },
            "entries": entries,
        }, indent=indent, ensure_ascii=False)
    
    def save(self, entries: list, filepath: str) -> None:
        """Save entries to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json(entries))
