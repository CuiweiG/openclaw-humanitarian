"""
Report Quality Scorer
Automatically evaluates the quality of generated situation reports.

Scoring dimensions:
- Completeness: How many OCHA sections have findings
- Timeliness: How recent are the source documents
- Source diversity: How many independent sources cited
- Citation accuracy: What % of claims have traceable sources
"""

from datetime import datetime, timedelta
from typing import Optional

class QualityScorer:
    """Score the quality of generated situation reports."""
    
    WEIGHTS = {
        'completeness': 0.3,
        'timeliness': 0.2,
        'source_diversity': 0.25,
        'citation_coverage': 0.25,
    }
    
    def score(self, report: dict) -> dict:
        """Score a situation report on multiple dimensions.
        
        Args:
            report: Structured report from AutoSitrepGenerator
            
        Returns:
            {overall: float, dimensions: {name: {score, explanation}}}
        """
        dimensions = {
            'completeness': self._score_completeness(report),
            'timeliness': self._score_timeliness(report),
            'source_diversity': self._score_diversity(report),
            'citation_coverage': self._score_citations(report),
        }
        
        overall = sum(
            d['score'] * self.WEIGHTS[name]
            for name, d in dimensions.items()
        )
        
        return {
            'overall': round(overall, 3),
            'grade': self._grade(overall),
            'dimensions': dimensions,
        }
    
    def _score_completeness(self, report: dict) -> dict:
        sections = report.get('sections', {})
        filled = sum(1 for s in sections.values() if s.get('findings'))
        total = len(sections) or 1
        score = filled / total
        return {
            'score': round(score, 3),
            'explanation': f"{filled}/{total} sections have findings",
        }
    
    def _score_timeliness(self, report: dict) -> dict:
        try:
            report_date = datetime.fromisoformat(report.get('generated_at', ''))
            age_hours = (datetime.utcnow() - report_date).total_seconds() / 3600
            score = max(0, 1.0 - (age_hours / 48))  # Decays over 48 hours
        except (ValueError, TypeError):
            score = 0.5
        return {
            'score': round(score, 3),
            'explanation': f"Report age factor",
        }
    
    def _score_diversity(self, report: dict) -> dict:
        sources = report.get('sources', [])
        orgs = set(s.get('org', '') for s in sources if s.get('org'))
        score = min(1.0, len(orgs) / 3)  # 3+ orgs = perfect
        return {
            'score': round(score, 3),
            'explanation': f"{len(orgs)} independent source organizations",
        }
    
    def _score_citations(self, report: dict) -> dict:
        sections = report.get('sections', {})
        total_findings = 0
        cited_findings = 0
        for section in sections.values():
            for f in section.get('findings', []):
                total_findings += 1
                if f.get('source') and f.get('url'):
                    cited_findings += 1
        score = cited_findings / max(total_findings, 1)
        return {
            'score': round(score, 3),
            'explanation': f"{cited_findings}/{total_findings} findings have source citations",
        }
    
    @staticmethod
    def _grade(score: float) -> str:
        if score >= 0.9: return 'A'
        if score >= 0.8: return 'B'
        if score >= 0.7: return 'C'
        if score >= 0.5: return 'D'
        return 'F'
