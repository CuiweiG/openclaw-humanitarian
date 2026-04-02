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

import hashlib
import logging
import os
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import IntEnum
from urllib.parse import urlencode

try:
    import requests
except ImportError:  # graceful degradation for minimal installs
    requests = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────
# Kill switch
#
# This module is a RED-TIER restricted module.  It is DISABLED by
# default and must only be activated after satisfying the checklist
# in docs/technical-readiness-matrix.md.
#
# The kill switch can be triggered by:
#   1. Setting env var ALERT_KILL_SWITCH=1
#   2. Calling kill_alerts() at runtime
#   3. Creating the file .alert_kill (in working directory)
#
# When killed, check_alerts() returns an empty list and logs a
# warning.  Re-enable by clearing all three triggers.
# ──────────────────────────────────────────

_kill_switch_lock = threading.Lock()
_kill_switch_active: bool = True  # DEFAULT: KILLED (red-tier module)


def is_alert_enabled() -> bool:
    """Check whether the alert system is currently enabled."""
    # Env var override (highest priority)
    if os.getenv("ALERT_KILL_SWITCH", "").strip() in ("1", "true", "yes"):
        return False
    # File-based kill switch
    if os.path.exists(".alert_kill"):
        return False
    # Runtime kill switch
    with _kill_switch_lock:
        return not _kill_switch_active


def enable_alerts() -> None:
    """Enable the alert system (requires all other kill switches cleared)."""
    global _kill_switch_active
    with _kill_switch_lock:
        _kill_switch_active = False
    logger.warning("ALERT SYSTEM ENABLED by runtime call")


def kill_alerts() -> None:
    """Emergency kill switch — immediately disable all alert processing."""
    global _kill_switch_active
    with _kill_switch_lock:
        _kill_switch_active = True
    logger.critical("ALERT SYSTEM KILLED by runtime call")


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
    """OCHA Flash Updates from ReliefWeb API v2.

    Polls for flash updates and situation reports tagged as
    'Flash Update' from OCHA, which typically indicate rapid-onset
    events including airstrikes and escalations.
    """

    RELIEFWEB_API = "https://api.reliefweb.int/v1/reports"
    FLASH_FORMAT = "Flash Update"
    # Countries of interest (ISO3)
    COUNTRIES = ["IRN", "LBN", "SYR", "AFG", "IRQ"]

    def poll(self, since_minutes: int = 15) -> list[CivilianAlert]:
        if requests is None:
            logger.warning("OCHAFlashSource: requests library not installed")
            return []

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        params = {
            "appname": "crisisbridge",
            "preset": "latest",
            "limit": 10,
            "filter[field]": "date.created",
            "filter[value][from]": cutoff_str,
            "fields[include][]": ["title", "source", "date", "country", "url"],
        }

        alerts: list[CivilianAlert] = []
        try:
            resp = requests.get(
                self.RELIEFWEB_API,
                params=params,  # type: ignore[arg-type]
                timeout=15,
                headers={"User-Agent": "CrisisBridge/1.0 (humanitarian)"},
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("OCHAFlashSource request failed: %s", exc)
            return []

        for item in data.get("data", []):
            fields = item.get("fields", {})
            title = fields.get("title", "")

            # Only process flash updates (rapid-onset events)
            if self.FLASH_FORMAT.lower() not in title.lower():
                continue

            countries = fields.get("country", [])
            country_names = [c.get("name", "") for c in countries]
            region = ", ".join(country_names) or "Unknown"

            source_list = fields.get("source", [])
            source_name = source_list[0].get("name", "OCHA") if source_list else "OCHA"
            source_url = fields.get("url", "")

            # Determine severity from title keywords
            severity = AlertSeverity.INFO
            title_lower = title.lower()
            if any(kw in title_lower for kw in ("strike", "attack", "bombing", "shelling", "killed")):
                severity = AlertSeverity.CRITICAL
            elif any(kw in title_lower for kw in ("escalation", "displacement", "emergency")):
                severity = AlertSeverity.WARNING

            alerts.append(CivilianAlert(
                severity=severity,
                region=region,
                summary_en=title,
                source=source_name,
                source_url=source_url,
                timestamp=datetime.now(timezone.utc),
            ))

        logger.info("OCHAFlashSource: found %d flash alerts", len(alerts))
        return alerts


# ──────────────────────────────────────────
# Alert dispatcher
# ──────────────────────────────────────────

_SOURCES: list[AlertSource] = [
    ACLEDSource(),
    OCHAFlashSource(),
]


_seen_hashes: set[str] = set()


def _alert_hash(alert: CivilianAlert) -> str:
    """Compute a dedup key from alert content."""
    raw = f"{alert.region}|{alert.severity}|{alert.source}|{alert.summary_en[:80]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_status() -> dict[str, object]:
    """Return current alert system status for monitoring."""
    return {
        "enabled": is_alert_enabled(),
        "runtime_killed": _kill_switch_active,
        "env_killed": os.getenv("ALERT_KILL_SWITCH", "").strip() in ("1", "true", "yes"),
        "file_killed": os.path.exists(".alert_kill"),
        "seen_hashes": len(_seen_hashes),
        "sources": [type(s).__name__ for s in _SOURCES],
    }


def check_alerts(since_minutes: int = 15) -> list[CivilianAlert]:
    """
    Poll all alert sources and return de-duplicated alerts.

    De-duplication is by (region, severity, source, summary_prefix)
    within the process lifetime.  Hash set resets on restart.

    Returns an empty list if the kill switch is active.
    """
    if not is_alert_enabled():
        logger.warning("check_alerts called but alert system is KILLED — returning empty")
        return []

    all_alerts: list[CivilianAlert] = []
    for source in _SOURCES:
        try:
            all_alerts.extend(source.poll(since_minutes))
        except Exception as exc:
            logger.error("Alert source %s failed: %s", type(source).__name__, exc)

    deduped: list[CivilianAlert] = []
    for alert in all_alerts:
        h = _alert_hash(alert)
        if h not in _seen_hashes:
            _seen_hashes.add(h)
            deduped.append(alert)

    if len(all_alerts) != len(deduped):
        logger.info(
            "Dedup: %d alerts → %d after removing duplicates",
            len(all_alerts), len(deduped),
        )
    return deduped
