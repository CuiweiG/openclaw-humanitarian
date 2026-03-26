"""
Citation Linker
Ensures every factual claim links back to its original source document.
Critical for maintaining credibility in humanitarian reporting.
"""

import re
import hashlib
from typing import Optional

class CitationLinker:
    """Link extracted facts to their original source documents."""
    
    def __init__(self):
        self.source_index = {}  # hash -> source info
    
    def register_source(self, text: str, url: str, org: str, date: str = "") -> str:
        """Register a source document and return its citation key.
        
        Args:
            text: Full text of the source
            url: Source URL
            org: Publishing organization
            date: Publication date
            
        Returns:
            Citation key (e.g., "src_a1b2c3")
        """
        key = "src_" + hashlib.sha256(url.encode()).hexdigest()[:6]
        self.source_index[key] = {
            'url': url,
            'organization': org,
            'date': date,
            'text_hash': hashlib.sha256(text.encode()).hexdigest()[:16],
        }
        return key
    
    def find_source(self, claim: str, sources: list) -> dict:
        """Find which source document a claim originates from.
        
        Args:
            claim: The factual claim to trace
            sources: List of source dicts with 'text', 'url', 'source'
            
        Returns:
            {source_url, organization, confidence, matched_text}
        """
        claim_words = set(claim.lower().split())
        best = {'source_url': '', 'organization': '', 'confidence': 0.0, 'matched_text': ''}
        
        for source in sources:
            text = source.get('text', '').lower()
            # Check if key phrases from claim appear in source
            overlap = sum(1 for w in claim_words if w in text and len(w) > 3)
            confidence = min(1.0, overlap / max(len(claim_words) * 0.5, 1))
            
            if confidence > best['confidence']:
                best = {
                    'source_url': source.get('url', ''),
                    'organization': source.get('source', ''),
                    'confidence': round(confidence, 3),
                    'matched_text': claim[:100],
                }
        
        return best
    
    def add_citations(self, report_text: str, sources: list) -> str:
        """Add inline citations to a report text.
        
        Appends [Source: ORG] after sentences that match source documents.
        """
        sentences = re.split(r'(?<=[.!?])\s+', report_text)
        cited = []
        
        for sent in sentences:
            match = self.find_source(sent, sources)
            if match['confidence'] > 0.5 and match['organization']:
                cited.append(f"{sent} [Source: {match['organization']}]")
            else:
                cited.append(sent)
        
        return ' '.join(cited)
