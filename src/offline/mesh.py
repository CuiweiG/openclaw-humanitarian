"""
mesh.py — Offline mesh network transport layer.

Provides a unified interface for delivering humanitarian bulletins
through internet-independent channels when Telegram and SMS are
unreachable (e.g. Iran 28+ day internet blackout).

Planned transports:
  1. Briar (Android)  — Tor / Wi-Fi / Bluetooth P2P
  2. Meshtastic       — LoRa 915/868 MHz long-range mesh
  3. D2C Satellite    — Starlink Direct-to-Cell / AST SpaceMobile

Architecture note:
  This module defines the *transport interface* and message format.
  Each transport backend is a separate class implementing
  MeshTransport.send().  The bulletin pipeline calls
  dispatch_bulletin() which fans out to all available transports.

Status: SCAFFOLD — interfaces defined, no working implementation yet.
  See docs/offline-roadmap.md for implementation plan.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

logger = logging.getLogger(__name__)


class TransportType(Enum):
    BRIAR = auto()
    MESHTASTIC = auto()
    D2C_SATELLITE = auto()


@dataclass(frozen=True)
class MeshMessage:
    """
    Compact message format for bandwidth-constrained mesh networks.

    Meshtastic LoRa packets are limited to ~230 bytes.  Messages must
    be pre-compressed and optionally split into numbered fragments.
    """
    payload: bytes          # UTF-8 compressed bulletin content
    language: str           # ISO 639-1 language code
    priority: int = 0       # 0=normal, 1=urgent, 2=life-safety
    fragment_index: int = 0
    fragment_total: int = 1
    bulletin_hash: str = "" # SHA-256 prefix for dedup at receiver


class MeshTransport(ABC):
    """Abstract base class for offline transport backends."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this transport is currently operational."""
        ...

    @abstractmethod
    def send(self, message: MeshMessage, region: str = "") -> bool:
        """
        Attempt to send a message via this transport.

        Args:
            message: Compressed bulletin fragment.
            region: Target geographic region (governorate-level).

        Returns:
            True if accepted for delivery (not necessarily received).
        """
        ...


class BriarTransport(MeshTransport):
    """Briar P2P transport — Wi-Fi / Bluetooth / Tor."""

    def is_available(self) -> bool:
        # TODO: check for Briar headless daemon on localhost
        logger.info("BriarTransport: not yet implemented")
        return False

    def send(self, message: MeshMessage, region: str = "") -> bool:
        raise NotImplementedError("Briar transport pending implementation")


class MeshtasticTransport(MeshTransport):
    """Meshtastic LoRa mesh transport."""

    def is_available(self) -> bool:
        # TODO: check for Meshtastic serial/TCP node
        logger.info("MeshtasticTransport: not yet implemented")
        return False

    def send(self, message: MeshMessage, region: str = "") -> bool:
        raise NotImplementedError("Meshtastic transport pending implementation")


class D2CSatelliteTransport(MeshTransport):
    """
    Direct-to-Cell satellite transport.

    Pre-reserved interface for Starlink D2C / AST SpaceMobile APIs.
    When operational, this allows ordinary smartphones to receive
    messages without any ground-based infrastructure.
    """

    def is_available(self) -> bool:
        logger.info("D2CSatelliteTransport: awaiting API access")
        return False

    def send(self, message: MeshMessage, region: str = "") -> bool:
        raise NotImplementedError("D2C satellite API not yet available")


# ──────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────

_TRANSPORTS: list[MeshTransport] = [
    BriarTransport(),
    MeshtasticTransport(),
    D2CSatelliteTransport(),
]


def dispatch_bulletin(message: MeshMessage, region: str = "") -> dict[str, bool]:
    """
    Fan out a bulletin to all available offline transports.

    Returns:
        Dict of transport_name → success/failure.
    """
    results: dict[str, bool] = {}
    for transport in _TRANSPORTS:
        name = type(transport).__name__
        if not transport.is_available():
            results[name] = False
            continue
        try:
            results[name] = transport.send(message, region)
        except Exception as exc:
            logger.error("%s failed: %s", name, exc)
            results[name] = False
    return results
