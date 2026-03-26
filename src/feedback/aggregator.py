"""
Report Aggregator
Aggregates multiple anonymized community reports by district and need type.
Generates summary statistics for humanitarian coordination.
"""

from collections import defaultdict
from datetime import datetime
from typing import Optional

class ReportAggregator:
    """Aggregate community reports into actionable summaries."""
    
    def __init__(self):
        self.reports = []
    
    def add_report(self, report: dict) -> None:
        """Add an anonymized report to the aggregation pool."""
        self.reports.append(report)
    
    def aggregate_by_district(self) -> dict:
        """Aggregate reports by district.
        
        Returns:
            {district: {need_type: count, total: count, latest: timestamp}}
        """
        result = defaultdict(lambda: defaultdict(int))
        timestamps = defaultdict(str)
        
        for r in self.reports:
            district = r.get('district', 'unknown')
            need = r.get('need_type', 'other')
            result[district][need] += 1
            result[district]['total'] += 1
            ts = r.get('timestamp', '')
            if ts > timestamps[district]:
                timestamps[district] = ts
        
        return {
            district: {
                'needs': dict(needs),
                'total_reports': needs['total'],
                'latest_report': timestamps[district],
            }
            for district, needs in result.items()
        }
    
    def generate_summary(self) -> dict:
        """Generate a high-level summary for coordination."""
        by_district = self.aggregate_by_district()
        
        # Find hotspots (districts with most reports)
        hotspots = sorted(
            by_district.items(),
            key=lambda x: x[1]['total_reports'],
            reverse=True
        )[:5]
        
        return {
            'generated_at': datetime.utcnow().isoformat(),
            'total_reports': len(self.reports),
            'districts_covered': len(by_district),
            'hotspots': [{'district': d, **info} for d, info in hotspots],
            'by_district': by_district,
        }
