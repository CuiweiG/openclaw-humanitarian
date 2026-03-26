"""
Source Credibility Checker
Evaluates the trustworthiness of information sources.

Whitelist approach: only verified humanitarian sources get high scores.
Everything else requires manual review.
"""

from typing import Optional

# Source credibility tiers
TIER_1_SOURCES = {
    'OCHA': 1.0, 'WHO': 1.0, 'UNHCR': 1.0, 'WFP': 1.0,
    'UNICEF': 1.0, 'ICRC': 1.0, 'IOM': 1.0, 'UNRWA': 1.0,
    'FAO': 1.0, 'IFRC': 1.0,
}

TIER_2_SOURCES = {
    'AP': 0.85, 'Reuters': 0.85, 'BBC': 0.85, 'AFP': 0.85,
    'Al Jazeera': 0.8, 'MSF': 0.9, 'IRC': 0.9,
    'Human Rights Watch': 0.85, 'Amnesty International': 0.85,
    'NetBlocks': 0.85, 'ACLED': 0.9,
}

class SourceChecker:
    """Evaluate source credibility for humanitarian information."""
    
    def check(self, source_name: str, source_url: str = "") -> dict:
        """Check the credibility of a source.
        
        Returns:
            {credibility: float, tier: str, requires_review: bool, note: str}
        """
        name_upper = source_name.upper().strip()
        
        # Check Tier 1 (UN agencies, ICRC)
        for name, score in TIER_1_SOURCES.items():
            if name.upper() in name_upper:
                return {
                    'credibility': score,
                    'tier': 'tier_1_un_agency',
                    'requires_review': False,
                    'note': f'Verified UN/ICRC source: {name}',
                }
        
        # Check Tier 2 (major media, established NGOs)
        for name, score in TIER_2_SOURCES.items():
            if name.upper() in name_upper:
                return {
                    'credibility': score,
                    'tier': 'tier_2_established',
                    'requires_review': False,
                    'note': f'Established source: {name}',
                }
        
        # Check if URL is from known domain
        if source_url:
            known_domains = ['reliefweb.int', 'unocha.org', 'unhcr.org',
                           'wfp.org', 'who.int', 'icrc.org']
            if any(d in source_url for d in known_domains):
                return {
                    'credibility': 0.95,
                    'tier': 'tier_1_verified_domain',
                    'requires_review': False,
                    'note': 'Verified domain',
                }
        
        # Unknown source
        return {
            'credibility': 0.3,
            'tier': 'unverified',
            'requires_review': True,
            'note': 'Unknown source — requires manual verification before publication',
        }
