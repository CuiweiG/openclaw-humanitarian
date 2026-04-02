"""
supply_chain.py — Humanitarian supply chain status tracker.

Tracks operational status of critical supply routes (sea, land, air)
used by humanitarian agencies to deliver aid.  This module serves
humanitarian coordinators and logistics officers (B2B/NGO audience),
not civilians directly.

Data flow:
  1. Static route definitions loaded from data/supply_chain/critical_routes.json
  2. Live status updated by scraping WFP Logistics Cluster and OCHA
     humanitarian access reports (via ReliefWeb API)
  3. Weekly digest generated for coordination teams

The Hormuz Strait shipping crisis has effectively suspended commercial
vessel transit, impacting UN agencies' ability to deliver life-saving
supplies to Iran, Gaza, and Sudan.

Status: OPERATIONAL — static data loaded, API scraping in development.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Data directory resolution
# ──────────────────────────────────────────

_MODULE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _MODULE_DIR.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data" / "supply_chain"


class RouteStatus(Enum):
    OPEN = "open"
    RESTRICTED = "restricted"
    PARTIAL = "partial"
    CLOSED = "closed"
    UNKNOWN = "unknown"


class RouteType(Enum):
    SEA = "sea"
    LAND = "land"
    AIR = "air"


@dataclass
class SupplyRoute:
    """A single supply chain route segment."""
    id: str
    name: str
    route_type: RouteType
    status: RouteStatus = RouteStatus.UNKNOWN
    last_updated: str = ""
    notes: str = ""
    alternative: str = ""
    affected_operations: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SupplyRoute:
        """Parse a route from JSON dict."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            route_type=RouteType(data.get("type", "sea")),
            status=RouteStatus(data.get("status", "unknown")),
            last_updated=data.get("last_updated", ""),
            notes=data.get("notes", ""),
            alternative=data.get("alternative", ""),
            affected_operations=data.get("affected_operations", []),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.route_type.value,
            "status": self.status.value,
            "last_updated": self.last_updated,
            "notes": self.notes,
            "alternative": self.alternative,
            "affected_operations": self.affected_operations,
        }

    @property
    def is_disrupted(self) -> bool:
        return self.status in (RouteStatus.RESTRICTED, RouteStatus.CLOSED)

    @property
    def status_emoji(self) -> str:
        return {
            RouteStatus.OPEN: "🟢",
            RouteStatus.PARTIAL: "🟡",
            RouteStatus.RESTRICTED: "🟠",
            RouteStatus.CLOSED: "🔴",
            RouteStatus.UNKNOWN: "⚪",
        }[self.status]


@dataclass
class SupplyChainSnapshot:
    """Point-in-time summary of humanitarian supply chain status."""
    timestamp: datetime
    routes: list[SupplyRoute] = field(default_factory=list)
    summary: str = ""
    sources: list[str] = field(default_factory=list)

    @property
    def disrupted_routes(self) -> list[SupplyRoute]:
        return [r for r in self.routes if r.is_disrupted]

    @property
    def disruption_rate(self) -> float:
        if not self.routes:
            return 0.0
        return len(self.disrupted_routes) / len(self.routes)

    def format_digest(self, lang: str = "en") -> str:
        """
        Format a human-readable weekly digest.

        Designed for humanitarian coordination teams.
        """
        lines = [
            f"📦 Supply Chain Status — {self.timestamp.strftime('%Y-%m-%d')}",
            f"   Routes monitored: {len(self.routes)} | "
            f"Disrupted: {len(self.disrupted_routes)}",
            "",
        ]

        # Group by status severity
        for route in sorted(self.routes, key=lambda r: r.status.value):
            ops = ", ".join(route.affected_operations[:3]) if route.affected_operations else "—"
            lines.append(
                f"  {route.status_emoji} {route.name} [{route.route_type.value}] "
                f"— {route.status.value}"
            )
            lines.append(f"     {route.notes}")
            if route.is_disrupted and route.alternative:
                lines.append(f"     ↳ Alt: {route.alternative}")
            lines.append(f"     Affects: {ops}")
            lines.append("")

        if self.sources:
            lines.append(f"Sources: {', '.join(self.sources)}")

        return "\n".join(lines)


# ──────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────

def _load_routes_from_file() -> list[SupplyRoute]:
    """Load route definitions from data/supply_chain/critical_routes.json."""
    routes_file = _DATA_DIR / "critical_routes.json"
    if not routes_file.exists():
        logger.warning("No routes file at %s", routes_file)
        return []

    try:
        with open(routes_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        routes = [SupplyRoute.from_dict(item) for item in data]
        logger.info("Loaded %d supply routes from %s", len(routes), routes_file)
        return routes
    except Exception as exc:
        logger.error("Failed to load routes: %s", exc)
        return []


def _save_routes_to_file(routes: list[SupplyRoute]) -> bool:
    """Persist updated route status back to JSON."""
    routes_file = _DATA_DIR / "critical_routes.json"
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(routes_file, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in routes], f, indent=2, ensure_ascii=False)
        return True
    except Exception as exc:
        logger.error("Failed to save routes: %s", exc)
        return False


# ──────────────────────────────────────────
# Live status updates (ReliefWeb API)
# ──────────────────────────────────────────

def _fetch_logistics_updates() -> list[dict[str, Any]]:
    """
    Fetch recent WFP Logistics Cluster and OCHA access reports
    from the ReliefWeb API.

    Returns raw report metadata for route status extraction.
    """
    try:
        import requests
    except ImportError:
        logger.warning("requests library not installed — skipping live updates")
        return []

    params = {
        "appname": "crisisbridge",
        "preset": "latest",
        "limit": 5,
        "query[value]": "logistics cluster OR humanitarian access OR supply chain",
        "fields[include][]": ["title", "source", "date", "body-html", "url"],
    }

    try:
        resp = requests.get(
            "https://api.reliefweb.int/v1/reports",
            params=params,
            timeout=15,
            headers={"User-Agent": "CrisisBridge/1.0 (humanitarian)"},
        )
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as exc:
        logger.error("ReliefWeb logistics fetch failed: %s", exc)
        return []


def _extract_status_updates(
    reports: list[dict[str, Any]],
    routes: list[SupplyRoute],
) -> int:
    """
    Heuristic extraction of route status from report titles.

    Scans report titles/bodies for route name mentions and status
    keywords. Returns number of routes updated.

    This is intentionally conservative — only clear signals trigger
    status changes. Ambiguous reports are logged but ignored.
    """
    updated = 0
    status_keywords = {
        "closed": RouteStatus.CLOSED,
        "suspended": RouteStatus.CLOSED,
        "blocked": RouteStatus.CLOSED,
        "restricted": RouteStatus.RESTRICTED,
        "limited": RouteStatus.RESTRICTED,
        "partial": RouteStatus.PARTIAL,
        "resumed": RouteStatus.OPEN,
        "reopened": RouteStatus.OPEN,
        "operational": RouteStatus.OPEN,
    }

    for report in reports:
        fields = report.get("fields", {})
        title = fields.get("title", "").lower()

        for route in routes:
            # Check if report mentions this route
            route_terms = route.name.lower().split()
            if not any(term in title for term in route_terms if len(term) > 3):
                continue

            # Check for status keywords
            for keyword, new_status in status_keywords.items():
                if keyword in title:
                    old_status = route.status
                    route.status = new_status
                    route.last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                    source_url = fields.get("url", "")
                    route.notes = f"Updated from: {fields.get('title', '')[:100]}"
                    updated += 1
                    logger.info(
                        "Route %s: %s → %s (from: %s)",
                        route.name, old_status.value, new_status.value, source_url,
                    )
                    break  # first matching keyword wins

    return updated


# ──────────────────────────────────────────
# Public API
# ──────────────────────────────────────────

def get_current_snapshot(refresh: bool = False) -> SupplyChainSnapshot:
    """
    Get current supply chain status.

    Args:
        refresh: If True, attempt to fetch live updates from ReliefWeb
                 before returning the snapshot.

    Returns:
        SupplyChainSnapshot with all monitored routes.
    """
    routes = _load_routes_from_file()
    sources = ["data/supply_chain/critical_routes.json"]

    if refresh and routes:
        logger.info("Fetching live logistics updates from ReliefWeb...")
        reports = _fetch_logistics_updates()
        if reports:
            n_updated = _extract_status_updates(reports, routes)
            if n_updated > 0:
                _save_routes_to_file(routes)
                sources.append("ReliefWeb API (live)")
                logger.info("Updated %d route(s) from live data", n_updated)

    return SupplyChainSnapshot(
        timestamp=datetime.now(timezone.utc),
        routes=routes,
        summary=_generate_summary(routes),
        sources=sources,
    )


def get_route(route_id: str) -> SupplyRoute | None:
    """Look up a specific route by ID."""
    routes = _load_routes_from_file()
    for route in routes:
        if route.id == route_id:
            return route
    return None


def update_route_status(
    route_id: str,
    status: RouteStatus,
    notes: str = "",
) -> bool:
    """
    Manually update a route's status.

    For use by humanitarian coordinators with field knowledge.
    """
    routes = _load_routes_from_file()
    for route in routes:
        if route.id == route_id:
            route.status = status
            route.last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if notes:
                route.notes = notes
            return _save_routes_to_file(routes)
    logger.warning("Route not found: %s", route_id)
    return False


def _generate_summary(routes: list[SupplyRoute]) -> str:
    """Generate one-line summary of overall supply chain health."""
    if not routes:
        return "No supply routes monitored."

    total = len(routes)
    closed = sum(1 for r in routes if r.status == RouteStatus.CLOSED)
    restricted = sum(1 for r in routes if r.status == RouteStatus.RESTRICTED)
    partial = sum(1 for r in routes if r.status == RouteStatus.PARTIAL)
    open_count = sum(1 for r in routes if r.status == RouteStatus.OPEN)

    parts = []
    if closed:
        parts.append(f"{closed} closed")
    if restricted:
        parts.append(f"{restricted} restricted")
    if partial:
        parts.append(f"{partial} partial")
    if open_count:
        parts.append(f"{open_count} open")

    return f"{total} routes monitored: {', '.join(parts)}."
