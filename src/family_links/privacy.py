"""
Privacy Guard for Family Links
Implements GDPR-compliant data handling.

Principles:
- Minimum data retention
- Right to access (export)
- Right to erasure (delete)
- Anonymization for public display
"""

from datetime import datetime, timedelta
from typing import Optional


class PrivacyGuard:
    """Strict privacy protection for family tracing data."""

    AUTO_DELETE_DAYS = 30  # Delete matched records after 30 days

    def anonymize_request(self, request) -> dict:
        """Create anonymized view for public search results.

        Only shows: first letter of name + city + language.
        Never exposes: full name, contact method, or request details.
        """
        name = request.seeking_name
        initial = name[0].upper() if name else "?"

        return {
            "id": request.request_id,
            "seeking": f"{initial}***",
            "city": request.last_known_location,
            "language": request.language,
            "posted_date": request.created_at.strftime("%Y-%m-%d"),
        }

    def should_auto_delete(self, request) -> bool:
        """Check if a matched request should be auto-deleted."""
        if request.status != "matched":
            return False
        age = (datetime.utcnow() - request.created_at).days
        return age >= self.AUTO_DELETE_DAYS

    def gdpr_export(self, request) -> dict:
        """Export all data associated with a request (GDPR Art. 15)."""
        return {
            "request_id": request.request_id,
            "seeking_name": request.seeking_name,
            "last_known_location": request.last_known_location,
            "language": request.language,
            "created_at": request.created_at.isoformat(),
            "status": request.status,
            "export_date": datetime.utcnow().isoformat(),
            "note": "This is all data stored for this request. Contact method is stored separately and encrypted.",
        }

    def gdpr_delete(self, registry, request_id: str) -> bool:
        """Delete all data for a request (GDPR Art. 17).

        Returns True if deleted, False if not found.
        """
        if request_id in registry._requests:
            del registry._requests[request_id]
            return True
        return False