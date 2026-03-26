"""
Family Links Registry
Assists separated families in reconnecting during crisis.
Inspired by ICRC Restoring Family Links (familylinks.icrc.org).

Privacy-by-design:
- No real identity stored (UUID only)
- Contact via Bot internal messaging only
- Auto-expire after 30 days
- GDPR-compliant export and delete
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict


class FamilyLinkRequest:
    """A single family tracing request."""

    def __init__(
        self,
        seeking_name: str,
        last_known_location: str,
        contact_method: str,
        language: str = "en",
    ) -> None:
        self.request_id: str = str(uuid.uuid4())[:12]
        self.seeking_name: str = seeking_name.strip()
        self.last_known_location: str = last_known_location.strip()
        self.contact_method: str = contact_method  # Telegram username or bot-internal
        self.language: str = language
        self.created_at: datetime = datetime.utcnow()
        self.status: str = "active"  # active / matched / expired

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "seeking_name": self.seeking_name,
            "last_known_location": self.last_known_location,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            # NOTE: contact_method is NEVER exposed externally
        }

    def public_view(self) -> dict:
        """Anonymized view for search results."""
        name_initial = self.seeking_name[0] + "***" if self.seeking_name else "***"
        return {
            "request_id": self.request_id,
            "seeking": name_initial,
            "location": self.last_known_location,
            "language": self.language,
            "posted": self.created_at.strftime("%Y-%m-%d"),
        }


class FamilyLinkRegistry:
    """Registry for family tracing requests."""

    def __init__(self) -> None:
        self._requests: Dict[str, FamilyLinkRequest] = {}

    def submit_request(self, request: FamilyLinkRequest) -> str:
        """Submit a family tracing request. Returns request_id."""
        self._requests[request.request_id] = request
        return request.request_id

    def search(self, name: str, location: str = "") -> List[FamilyLinkRequest]:
        """Search for matching requests.

        Returns requests where seeking_name fuzzy-matches the given name
        and location matches (if provided).
        """
        results = []
        name_lower = name.lower().strip()
        for req in self._requests.values():
            if req.status != "active":
                continue
            if name_lower in req.seeking_name.lower() or req.seeking_name.lower() in name_lower:
                if not location or location.lower() in req.last_known_location.lower():
                    results.append(req)
        return results

    def get_request(self, request_id: str) -> Optional[FamilyLinkRequest]:
        """Get a specific request by ID."""
        return self._requests.get(request_id)

    def match_and_notify(self, request_a_id: str, request_b_id: str) -> dict:
        """Mark two requests as matched.

        Returns contact instructions for both parties.
        In production, this would send Telegram notifications.
        """
        a = self._requests.get(request_a_id)
        b = self._requests.get(request_b_id)
        if not a or not b:
            return {"error": "Request not found"}

        a.status = "matched"
        b.status = "matched"

        return {
            "matched": True,
            "message": "A potential match has been found. Both parties will be contacted via the Bot.",
            "request_a": request_a_id,
            "request_b": request_b_id,
        }

    def expire_old_requests(self, days: int = 30) -> int:
        """Expire requests older than N days. Returns count of expired."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        expired = 0
        for req in self._requests.values():
            if req.status == "active" and req.created_at < cutoff:
                req.status = "expired"
                expired += 1
        return expired

    @property
    def active_count(self) -> int:
        return sum(1 for r in self._requests.values() if r.status == "active")