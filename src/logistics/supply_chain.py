"""
supply_chain.py — Humanitarian supply chain status tracker.

The Hormuz Strait shipping crisis has effectively suspended commercial
vessel transit, impacting UN agencies' ability to deliver life-saving
supplies.  This module tracks supply chain status for humanitarian
workers (B2B/NGO audience, not civilian-facing).

Data sources (planned):
  - WFP Logistics Cluster updates
  - OCHA humanitarian access reports
  - Port status data (Port Sudan, Beirut, Bandar Abbas)
  - UNHAS flight schedules

Output:
  Weekly supply chain digest for humanitarian coordinators, including
  estimated delivery windows and route alternatives.

Status: SCAFFOLD — data model defined, no API integration yet.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

logger = logging.getLogger(__name__)


class RouteStatus(Enum):
    OPEN = auto()
    RESTRICTED = auto()
    CLOSED = auto()
    UNKNOWN = auto()


class PortStatus(Enum):
    OPERATIONAL = auto()
    PARTIAL = auto()
    CLOSED = auto()
    UNKNOWN = auto()


@dataclass
class SupplyRoute:
    """A single supply chain route segment."""
    name: str                    # e.g. "Hormuz Strait", "Beirut Port"
    route_type: str              # "sea", "air", "land"
    status: RouteStatus = RouteStatus.UNKNOWN
    last_updated: datetime | None = None
    notes: str = ""
    alternative: str = ""        # Suggested alternative if blocked


@dataclass
class SupplyChainSnapshot:
    """Point-in-time summary of humanitarian supply chain status."""
    timestamp: datetime
    routes: list[SupplyRoute] = field(default_factory=list)
    summary: str = ""
    sources: list[str] = field(default_factory=list)


# ──────────────────────────────────────────
# Known critical routes
# ──────────────────────────────────────────

CRITICAL_ROUTES: list[SupplyRoute] = [
    SupplyRoute(
        name="Hormuz Strait",
        route_type="sea",
        notes="Primary maritime route for Gulf humanitarian shipments",
        alternative="Overland via Turkey or airlift via UNHAS",
    ),
    SupplyRoute(
        name="Beirut Port",
        route_type="sea",
        notes="Primary entry for Lebanon humanitarian supplies",
        alternative="Tripoli port or overland from Syria/Jordan",
    ),
    SupplyRoute(
        name="Bandar Abbas Port",
        route_type="sea",
        notes="Major Iranian port for WFP shipments",
        alternative="Chabahar port (limited capacity)",
    ),
    SupplyRoute(
        name="Port Sudan",
        route_type="sea",
        notes="Critical for Sudan humanitarian corridor",
        alternative="Airlift via UNHAS from Nairobi/Addis",
    ),
    SupplyRoute(
        name="Bab al-Hawa Crossing",
        route_type="land",
        notes="Primary cross-border aid route into NW Syria",
        alternative="Damascus hub (access restricted)",
    ),
]


def get_current_snapshot() -> SupplyChainSnapshot:
    """
    Fetch current supply chain status from all data sources.

    TODO: implement actual API polling. Currently returns a skeleton
    with static route definitions and UNKNOWN status.
    """
    logger.info("Supply chain snapshot requested — returning static data")
    return SupplyChainSnapshot(
        timestamp=datetime.utcnow(),
        routes=CRITICAL_ROUTES,
        summary="Supply chain status tracking not yet operational. "
                "See docs/supply-chain-roadmap.md for implementation plan.",
        sources=["static"],
    )
