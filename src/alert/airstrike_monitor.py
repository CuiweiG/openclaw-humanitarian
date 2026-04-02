"""
airstrike_monitor.py — Real-time civilian airstrike warning system.

Distinct from the hourly/daily humanitarian bulletin pipeline, this
module handles *minute-level* life-safety alerts.  It polls conflict
event APIs and OCHA flash updates to detect and push time-critical
warnings.

Data sources (planned):
  - ACLED (Armed Conflict Location & Event Data) — near-real-time
  - Airstrikes.live API — crowd-verified strike reports
  - OCHA Flash Updates — official rapid-onset event bulletins
  - LiveuaMap-style OSINT aggregators (with T3 trust scoring)

Output channels:
  - Telegram (where reachable)
  - SMS (with HMAC verification, Iran region paused)
  - Offline mesh (Briar / Meshtastic)

Privacy: No user geolocation is ever collected.  Alerts are broadcast
to region-level subscribers (governorate granularity) using opt-in
topic channels, not individual targeting.

Status: SCAFFOLD — interfaces only, no working implementation yet.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

logger = logging.getLogger(__name__)


class AlertSeverity(IntEnum):
    """Alert urgency level."""
    INFO = 0        # General conflict update
    WARNING = 1     # Elevated risk in region
    CRITICAL = 2    # Active strikes — seek shelter immediately


@dataclass(frozen=True)
class CivilianAlert:
    """Structured alert for civilian distribution."""
    severity: AlertSeverity
    region: str                  # Governorate-level identifier
    summary_en: str              # English summary (to be translated)
    source: str                  # Data source identifier
    source_url: str = ""
    timestamp: datetime | None = None
    ttl_minutes: int = 60        # Alert expires after this duration


class AlertSource(ABC):
    """Abstract interface for conflict event data sources."""

    @abstractmethod
    def poll(self, since_minutes: int = 15) -> list[CivilianAlert]:
        """
        Poll for recent events.

        Args:
            since_minutes: Look-back window.

        Returns:
            List of new alerts since last poll.
        """
        ...


class ACLEDSource(AlertSource):
    """ACLED conflict event data — requires API key."""

    def poll(self, since_minutes: int = 15) -> list[CivilianAlert]:
        # TODO: implement ACLED API polling
        logger.info("ACLEDSource: not yet implemented")
        return []


class OCHAFlashSource(AlertSource):
    """OCHA Flash Updates from ReliefWeb API."""

    def poll(self, since_minutes: int = 15) -> list[CivilianAlert]:
        # TODO: implement ReliefWeb flash update polling
        logger.info("OCHAFlashSource: not yet implemented")
        return []


# ──────────────────────────────────────────
# Alert dispatcher
# ──────────────────────────────────────────

_SOURCES: list[AlertSource] = [
    ACLEDSource(),
    OCHAFlashSource(),
]


def check_alerts(since_minutes: int = 15) -> list[CivilianAlert]:
    """
    Poll all alert sources and return de-duplicated alerts.

    De-duplication is by (region, severity, source) within the
    TTL window.
    """
    all_alerts: list[CivilianAlert] = []
    for source in _SOURCES:
        try:
            all_alerts.extend(source.poll(since_minutes))
        except Exception as exc:
            logger.error("Alert source %s failed: %s", type(source).__name__, exc)
    # TODO: implement de-duplication logic
    return all_alerts
