"""
canary.py — Canary token system for detecting systematic scraping.

In adversarial environments (e.g. Iran internet shutdown), state actors
may use privileged network access ("white SIM cards") to interact with
the Telegram bot and systematically scrape user lists or content.

This module provides lightweight heuristics to detect such behaviour
without storing any personally identifiable information.

Design principles:
  - No PII storage: we track interaction *patterns*, not identities.
  - No IP logging: Telegram doesn't expose IPs anyway.
  - Alerts only: detection triggers a log alert, never an automatic ban.
    Human review is mandatory before any action.
  - Canary commands: special "honeypot" commands that a normal user would
    never discover but an automated scraper might enumerate.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Rate-based anomaly detection
# ──────────────────────────────────────────

@dataclass
class _UserWindow:
    """Sliding window of interaction timestamps for a single user."""
    timestamps: list[float] = field(default_factory=list)

    def record(self, ts: float | None = None) -> None:
        self.timestamps.append(ts or time.time())
        # Keep only last 100 interactions
        if len(self.timestamps) > 100:
            self.timestamps = self.timestamps[-100:]

    def rate(self, window_seconds: int = 60) -> float:
        """Interactions per minute over the last *window_seconds*."""
        now = time.time()
        cutoff = now - window_seconds
        recent = [t for t in self.timestamps if t >= cutoff]
        return len(recent) * (60.0 / window_seconds)


class ScrapeDetector:
    """
    Stateless (in-memory) detector for automated scraping patterns.

    NOTE: user_id here is the *hashed* Telegram user ID, not the raw
    integer.  The bot layer must hash before calling record().
    This ensures we detect patterns without storing real identifiers.

    Thresholds are intentionally conservative to avoid false positives
    against legitimate power-users.
    """

    def __init__(
        self,
        rate_threshold: float = 30.0,     # interactions/min to trigger alert
        enum_threshold: int = 10,          # unique canary hits to trigger alert
    ) -> None:
        self._rate_threshold = rate_threshold
        self._enum_threshold = enum_threshold
        self._windows: dict[str, _UserWindow] = defaultdict(_UserWindow)
        self._canary_hits: dict[str, set[str]] = defaultdict(set)

    def record_interaction(self, hashed_uid: str) -> list[str]:
        """
        Record a user interaction and return any triggered alerts.

        Returns:
            List of alert strings (empty if no anomaly detected).
        """
        alerts: list[str] = []
        window = self._windows[hashed_uid]
        window.record()

        rate = window.rate()
        if rate >= self._rate_threshold:
            msg = (
                f"CANARY ALERT: user {hashed_uid[:8]}… "
                f"rate={rate:.1f}/min exceeds threshold={self._rate_threshold}"
            )
            logger.warning(msg)
            alerts.append(msg)

        return alerts

    def record_canary_hit(self, hashed_uid: str, canary_id: str) -> list[str]:
        """
        Record a hit on a canary (honeypot) command.

        Normal users never discover canary commands.  A single hit is
        noteworthy; multiple distinct canary hits from one user strongly
        suggest automated enumeration.

        Returns:
            List of alert strings.
        """
        alerts: list[str] = []
        self._canary_hits[hashed_uid].add(canary_id)

        hit_count = len(self._canary_hits[hashed_uid])
        msg = (
            f"CANARY HIT: user {hashed_uid[:8]}… "
            f"triggered canary '{canary_id}' (total unique: {hit_count})"
        )
        logger.warning(msg)
        alerts.append(msg)

        if hit_count >= self._enum_threshold:
            escalation = (
                f"CANARY ESCALATION: user {hashed_uid[:8]}… "
                f"hit {hit_count} distinct canaries — likely automated enumeration"
            )
            logger.critical(escalation)
            alerts.append(escalation)

        return alerts


# ──────────────────────────────────────────
# Canary command definitions
# ──────────────────────────────────────────

# These commands are never advertised in /help or the bot menu.
# A legitimate user has no way to discover them.  If they are invoked,
# the caller is probing the bot's command surface — a strong signal of
# automated behaviour.

CANARY_COMMANDS: set[str] = {
    "/debug_mode",
    "/admin_panel",
    "/dump_users",
    "/export_data",
    "/internal_status",
}
