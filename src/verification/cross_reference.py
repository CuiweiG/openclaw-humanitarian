"""
Cross-Reference Engine
Validates facts by checking if multiple independent sources confirm them.
Flags conflicting data for manual review.
"""

import re
from collections import defaultdict
from typing import Optional

class CrossReferencer:
    """Cross-reference facts across multiple source documents."""
    
    CONFLICT_THRESHOLD = 0.2  # 20% difference = conflict
    
    def check_claim(self, claim: str, sources: list) -> dict:
        """Check if a claim is supported by multiple sources.
        
        Args:
            claim: Factual claim to verify
            sources: List of source dicts with 'text', 'source', 'url'
            
        Returns:
            {status: str, supporting_sources: int, total_sources: int, 
             conflicts: list, verification_level: str}
        """
        supporting = []
        claim_lower = claim.lower()
        
        # Extract key terms from claim
        key_terms = [w for w in claim_lower.split() if len(w) > 4]
        
        for source in sources:
            text = source.get('text', '').lower()
            matches = sum(1 for t in key_terms if t in text)
            if matches >= len(key_terms) * 0.4:
                supporting.append(source.get('source', 'unknown'))
        
        unique_sources = list(set(supporting))
        
        if len(unique_sources) >= 3:
            level = 'cross_verified'
            status = '✅ Cross-verified by 3+ sources'
        elif len(unique_sources) == 2:
            level = 'double_sourced'
            status = '✅ Confirmed by 2 sources'
        elif len(unique_sources) == 1:
            level = 'single_source'
            status = '⚠️ Single source — awaiting independent verification'
        else:
            level = 'unverified'
            status = '❌ No supporting sources found'
        
        return {
            'status': status,
            'supporting_sources': len(unique_sources),
            'source_names': unique_sources,
            'total_sources_checked': len(sources),
            'verification_level': level,
        }
    
    def check_number_consistency(self, numbers: list) -> dict:
        """Check if numbers from different sources are consistent.
        
        Args:
            numbers: List of {value: int, source: str, context: str}
            
        Returns:
            {consistent: bool, range: {min, max}, conflict_details: str}
        """
        if not numbers:
            return {'consistent': True, 'range': None, 'conflict_details': ''}
        
        values = [n['value'] for n in numbers if isinstance(n.get('value'), (int, float))]
        if not values:
            return {'consistent': True, 'range': None, 'conflict_details': ''}
        
        min_val, max_val = min(values), max(values)
        
        if max_val == 0:
            return {'consistent': True, 'range': {'min': 0, 'max': 0}, 'conflict_details': ''}
        
        variance = (max_val - min_val) / max_val
        consistent = variance <= self.CONFLICT_THRESHOLD
        
        return {
            'consistent': consistent,
            'range': {'min': min_val, 'max': max_val},
            'variance': round(variance, 3),
            'conflict_details': '' if consistent else 
                f'⚠️ Data conflict: values range from {min_val:,} to {max_val:,} ({variance:.0%} variance)',
        }
