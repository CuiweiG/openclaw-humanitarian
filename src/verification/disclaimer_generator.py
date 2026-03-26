"""
Automatic Disclaimer Generator
Generates appropriate disclaimers based on source credibility
and verification status of information.
"""

from typing import Optional

class DisclaimerGenerator:
    """Generate contextual disclaimers for humanitarian bulletins."""
    
    TEMPLATES = {
        'cross_verified': '✅ This information has been cross-verified across {count} independent sources.',
        'double_sourced': '✅ Confirmed by 2 independent sources: {sources}.',
        'single_source': '⚠️ Based on a single source ({source}). Awaiting independent verification.',
        'unverified': '❌ This information could not be independently verified. Please refer to official sources.',
        'data_conflict': '⚠️ Sources report conflicting numbers (range: {min}–{max}). Refer to original reports.',
        'ai_translated': '⚠️ AI-translated from English. May contain translation errors. Original: {url}',
        'stale': '⏰ Based on data from {date}. More recent information may be available.',
    }

    def generate(self, verification_result: dict, language: str = 'en') -> str:
        """Generate a disclaimer based on verification results.
        
        Args:
            verification_result: Output from CrossReferencer or SourceChecker
            language: Target language for disclaimer
            
        Returns:
            Formatted disclaimer string
        """
        level = verification_result.get('verification_level', 'unverified')
        template = self.TEMPLATES.get(level, self.TEMPLATES['unverified'])
        
        return template.format(
            count=verification_result.get('supporting_sources', 0),
            sources=', '.join(verification_result.get('source_names', [])),
            source=verification_result.get('source_names', ['unknown'])[0] if verification_result.get('source_names') else 'unknown',
            min=verification_result.get('range', {}).get('min', '?'),
            max=verification_result.get('range', {}).get('max', '?'),
            url=verification_result.get('source_url', ''),
            date=verification_result.get('date', ''),
        )
    
    def standard_footer(self) -> str:
        """Standard footer for all bulletins."""
        return (
            "---\n"
            "⚠️ AI-generated bulletin from official UN sources. "
            "May contain errors. Always verify with local authorities "
            "for critical decisions.\n"
            "📧 Report errors: aid@agentmail.to"
        )
