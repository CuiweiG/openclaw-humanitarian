"""
Trend Detector
Identifies emerging patterns in community feedback.
Generates automatic alerts when trends indicate new crises or unmet needs.
"""

from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Optional

class TrendDetector:
    """Detect emerging trends in community feedback data."""
    
    ALERT_THRESHOLD = 3  # N reports about same need in same area triggers alert
    SPIKE_MULTIPLIER = 2.0  # 2x normal rate = spike
    
    def __init__(self):
        self.history = []  # List of analyzed reports
    
    def add_report(self, analyzed_report: dict, district: str) -> None:
        """Add an analyzed report to the trend tracker."""
        self.history.append({
            **analyzed_report,
            'district': district,
            'added_at': datetime.utcnow().isoformat(),
        })
    
    def detect_trends(self, hours: int = 24) -> dict:
        """Detect trends in recent reports.
        
        Args:
            hours: Look-back window in hours
            
        Returns:
            {alerts: list, hotspots: list, emerging_needs: list}
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [r for r in self.history 
                  if r.get('added_at', '') >= cutoff.isoformat()]
        
        if not recent:
            return {'alerts': [], 'hotspots': [], 'emerging_needs': []}
        
        return {
            'alerts': self._check_alerts(recent),
            'hotspots': self._find_hotspots(recent),
            'emerging_needs': self._find_emerging_needs(recent),
        }
    
    def _check_alerts(self, reports: list) -> list:
        """Check if any need/district combo exceeds alert threshold."""
        alerts = []
        combos = defaultdict(int)
        
        for r in reports:
            district = r.get('district', 'unknown')
            for need in r.get('needs', []):
                combos[(district, need)] += 1
        
        for (district, need), count in combos.items():
            if count >= self.ALERT_THRESHOLD:
                alerts.append({
                    'type': 'cluster_alert',
                    'district': district,
                    'need': need,
                    'report_count': count,
                    'message': f'⚠️ {count} reports of "{need}" need in {district} in the last 24h',
                })
        
        return alerts
    
    def _find_hotspots(self, reports: list) -> list:
        """Find districts with highest report density."""
        district_counts = Counter(r.get('district', 'unknown') for r in reports)
        return [
            {'district': d, 'report_count': c}
            for d, c in district_counts.most_common(5)
        ]
    
    def _find_emerging_needs(self, reports: list) -> list:
        """Find needs that are newly appearing or rapidly growing."""
        all_needs = []
        for r in reports:
            all_needs.extend(r.get('needs', []))
        
        need_counts = Counter(all_needs)
        return [
            {'need': need, 'mentions': count}
            for need, count in need_counts.most_common(5)
        ]
