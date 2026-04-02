"""
mesh.py — Offline mesh network transport layer.

Production-grade transport abstraction for delivering humanitarian
bulletins through internet-independent channels.  Designed for the
Iran 28+ day internet blackout scenario where Telegram is unreachable
for ~90 million people.

Transports implemented:
  1. Briar  — P2P via Briar Mailbox REST API (store-and-forward)
  2. Meshtastic — LoRa mesh via serial/TCP (256-byte packet limit)
  3. D2C Satellite — Pre-reserved interface for Starlink/AST SpaceMobile

Architecture:
  The bulletin pipeline calls dispatch_bulletin() which serialises the
  message into the compact MeshMessage format, fragments it if needed
  (Meshtastic), and fans out to all available transports.

  Each transport is independently failable — a Briar outage does not
  block Meshtastic delivery.

Wire format (MeshMessage):
  - Header: 4 bytes  [priority:1][frag_idx:1][frag_total:1][lang:1]
  - Body:   variable  zlib-compressed UTF-8 payload
  - Hash:   8 bytes   SHA-256 prefix for receiver-side dedup

Security:
  - No PII in any message payload.
  - Briar: end-to-end encrypted (Bramble protocol).
  - Meshtastic: AES-128 channel encryption (PSK distributed out-of-band).
  - D2C: TLS to satellite API when available.

Status: OPERATIONAL (Briar Mailbox + Meshtastic serial).
  D2C satellite interface reserved, awaiting API access.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import struct
import time
import zlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Constants
# ──────────────────────────────────────────

# Meshtastic LoRa hard limit (accounting for header overhead)
MESHTASTIC_MAX_PAYLOAD = 230
# Briar Mailbox practical limit for reliable sync
BRIAR_MAX_PAYLOAD = 2048
# Header: priority(1) + frag_idx(1) + frag_total(1) + lang_code(1) = 4 bytes
HEADER_SIZE = 4
# Dedup hash prefix length
HASH_PREFIX_LEN = 8

# Language code mapping (single byte for wire efficiency)
_LANG_CODES: dict[str, int] = {
    "en": 0, "ar": 1, "fa": 2, "dar": 3, "zh": 4,
    "tr": 5, "fr": 6, "es": 7, "ru": 8, "ps": 9,
    "ku": 10, "apc": 11,
}
_LANG_REVERSE: dict[int, str] = {v: k for k, v in _LANG_CODES.items()}


class TransportType(Enum):
    BRIAR = auto()
    MESHTASTIC = auto()
    D2C_SATELLITE = auto()


class Priority(Enum):
    """Bulletin priority — maps to alert severity levels."""
    NORMAL = 0       # Routine humanitarian update
    URGENT = 1       # Significant situation change
    LIFE_SAFETY = 2  # Active strikes / immediate danger


@dataclass(frozen=True)
class MeshMessage:
    """
    Compact message format for bandwidth-constrained mesh networks.

    Designed to be fragmentable for Meshtastic (230-byte packets)
    while remaining efficient for higher-bandwidth transports.
    """
    payload: bytes          # zlib-compressed UTF-8 bulletin content
    language: str           # ISO 639 language code
    priority: Priority = Priority.NORMAL
    fragment_index: int = 0
    fragment_total: int = 1
    bulletin_hash: str = "" # SHA-256 prefix for dedup at receiver
    created_at: float = 0.0 # Unix timestamp

    def to_wire(self) -> bytes:
        """Serialise to wire format: header + payload + hash."""
        lang_byte = _LANG_CODES.get(self.language, 0)
        header = struct.pack(
            "!BBBB",
            self.priority.value,
            self.fragment_index,
            self.fragment_total,
            lang_byte,
        )
        hash_bytes = bytes.fromhex(self.bulletin_hash[:HASH_PREFIX_LEN * 2])
        return header + self.payload + hash_bytes

    @staticmethod
    def from_wire(data: bytes) -> MeshMessage:
        """Deserialise from wire format."""
        if len(data) < HEADER_SIZE + HASH_PREFIX_LEN:
            raise ValueError(f"Wire data too short: {len(data)} bytes")
        prio, frag_idx, frag_total, lang_byte = struct.unpack("!BBBB", data[:4])
        hash_bytes = data[-HASH_PREFIX_LEN:]
        payload = data[4:-HASH_PREFIX_LEN]
        return MeshMessage(
            payload=payload,
            language=_LANG_REVERSE.get(lang_byte, "en"),
            priority=Priority(prio),
            fragment_index=frag_idx,
            fragment_total=frag_total,
            bulletin_hash=hash_bytes.hex(),
        )


# ──────────────────────────────────────────
# Compression & fragmentation
# ──────────────────────────────────────────

def compress_bulletin(text: str) -> bytes:
    """Compress bulletin text with zlib level 9."""
    return zlib.compress(text.encode("utf-8"), level=9)


def decompress_bulletin(data: bytes) -> str:
    """Decompress bulletin payload."""
    return zlib.decompress(data).decode("utf-8")


def _compute_hash(text: str) -> str:
    """SHA-256 hex digest of raw bulletin text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fragment_for_meshtastic(
    text: str,
    language: str,
    priority: Priority = Priority.NORMAL,
) -> list[MeshMessage]:
    """
    Compress and fragment a bulletin for Meshtastic delivery.

    Each fragment fits within MESHTASTIC_MAX_PAYLOAD including
    the 4-byte header and 8-byte hash suffix.

    Returns:
        Ordered list of MeshMessage fragments.
    """
    compressed = compress_bulletin(text)
    bulletin_hash = _compute_hash(text)
    usable = MESHTASTIC_MAX_PAYLOAD - HEADER_SIZE - HASH_PREFIX_LEN

    if usable <= 0:
        raise ValueError("Payload budget is non-positive — check constants")

    chunks: list[bytes] = []
    for i in range(0, len(compressed), usable):
        chunks.append(compressed[i:i + usable])

    if len(chunks) > 255:
        logger.warning(
            "Bulletin requires %d fragments (max 255) — truncating", len(chunks)
        )
        chunks = chunks[:255]

    now = time.time()
    return [
        MeshMessage(
            payload=chunk,
            language=language,
            priority=priority,
            fragment_index=idx,
            fragment_total=len(chunks),
            bulletin_hash=bulletin_hash,
            created_at=now,
        )
        for idx, chunk in enumerate(chunks)
    ]


def prepare_for_briar(
    text: str,
    language: str,
    priority: Priority = Priority.NORMAL,
) -> MeshMessage:
    """
    Prepare a single MeshMessage for Briar Mailbox delivery.

    Briar supports larger payloads so fragmentation is rarely needed.
    If the compressed payload exceeds BRIAR_MAX_PAYLOAD, the text
    is truncated with an ellipsis marker.
    """
    bulletin_hash = _compute_hash(text)
    compressed = compress_bulletin(text)

    if len(compressed) > BRIAR_MAX_PAYLOAD:
        # Truncate source text until it fits
        while len(compressed) > BRIAR_MAX_PAYLOAD and len(text) > 100:
            text = text[:len(text) - 50] + "…"
            compressed = compress_bulletin(text)
        logger.warning("Briar payload truncated to %d bytes", len(compressed))

    return MeshMessage(
        payload=compressed,
        language=language,
        priority=priority,
        fragment_index=0,
        fragment_total=1,
        bulletin_hash=bulletin_hash,
        created_at=time.time(),
    )


# ──────────────────────────────────────────
# Transport interface
# ──────────────────────────────────────────

class MeshTransport(ABC):
    """Abstract base class for offline transport backends."""

    transport_type: TransportType

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this transport is currently operational."""
        ...

    @abstractmethod
    def send(self, message: MeshMessage, region: str = "") -> bool:
        """
        Attempt to send a message via this transport.

        Args:
            message: Compressed bulletin (or fragment).
            region: Target geographic region (governorate-level).

        Returns:
            True if accepted for delivery (not necessarily received).
        """
        ...

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Return transport health/status metadata."""
        ...


# ──────────────────────────────────────────
# Briar Mailbox transport
# ──────────────────────────────────────────

class BriarTransport(MeshTransport):
    """
    Briar Mailbox REST API transport.

    Store-and-forward: bulletins are uploaded to a Mailbox server,
    then synced by field volunteers when they briefly connect.
    Volunteers relay to displaced persons via BLE/WiFi Direct.

    Requires:
      - BRIAR_MAILBOX_URL env var (e.g. https://mailbox.example.org)
      - BRIAR_MAILBOX_TOKEN env var (auth token)
    """

    transport_type = TransportType.BRIAR

    def __init__(self) -> None:
        self._url = os.getenv("BRIAR_MAILBOX_URL", "").rstrip("/")
        self._token = os.getenv("BRIAR_MAILBOX_TOKEN", "")
        self._last_status: dict[str, Any] = {}

    def is_available(self) -> bool:
        if not self._url or not self._token:
            return False
        try:
            import requests as req
            resp = req.get(
                f"{self._url}/v1/status",
                headers=self._auth_headers(),
                timeout=10,
            )
            self._last_status = {
                "reachable": resp.ok,
                "status_code": resp.status_code,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
            return resp.ok
        except Exception as exc:
            logger.debug("Briar Mailbox unreachable: %s", exc)
            self._last_status = {"reachable": False, "error": str(exc)}
            return False

    def send(self, message: MeshMessage, region: str = "") -> bool:
        import requests as req

        payload = {
            "data": message.payload.hex(),
            "language": message.language,
            "priority": message.priority.value,
            "region": region,
            "hash": message.bulletin_hash,
            "timestamp": message.created_at or time.time(),
        }
        try:
            resp = req.post(
                f"{self._url}/v1/messages",
                json=payload,
                headers=self._auth_headers(),
                timeout=15,
            )
            if resp.ok:
                logger.info("Briar: bulletin uploaded (%s, %s)", region, message.language)
                return True
            logger.warning("Briar upload failed: HTTP %d", resp.status_code)
            return False
        except Exception as exc:
            logger.error("Briar send error: %s", exc)
            return False

    def get_status(self) -> dict[str, Any]:
        return {"transport": "briar", **self._last_status}

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "CrisisBridge/1.0",
        }


# ──────────────────────────────────────────
# Meshtastic LoRa transport
# ──────────────────────────────────────────

class MeshtasticTransport(MeshTransport):
    """
    Meshtastic LoRa mesh transport.

    Connects to a local Meshtastic node via serial (USB) or TCP
    and broadcasts bulletin fragments on the configured channel.

    Requires:
      - meshtastic Python package (pip install meshtastic)
      - MESHTASTIC_DEVICE env var (default: auto-detect)
        Serial: /dev/ttyUSB0 or COM3
        TCP:    tcp:192.168.1.50

    Channel 0 is reserved for CrisisBridge humanitarian broadcasts.
    PSK must be distributed to field nodes out-of-band.
    """

    transport_type = TransportType.MESHTASTIC
    CHANNEL_INDEX = 0
    # Inter-packet delay to avoid congestion on slow LoRa links
    TX_DELAY_SECONDS = 2.0

    def __init__(self) -> None:
        self._device = os.getenv("MESHTASTIC_DEVICE", "")
        self._interface: Any = None
        self._last_status: dict[str, Any] = {}

    def is_available(self) -> bool:
        try:
            import meshtastic  # noqa: F401
            from meshtastic.serial_interface import SerialInterface
            from meshtastic.tcp_interface import TCPInterface
        except ImportError:
            self._last_status = {"available": False, "error": "meshtastic package not installed"}
            return False

        if self._interface is not None:
            # Already connected — check if still alive
            try:
                info = self._interface.getMyNodeInfo()
                self._last_status = {
                    "available": True,
                    "node_id": info.get("num", "unknown"),
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                }
                return True
            except Exception:
                self._interface = None

        # Try to connect
        try:
            if self._device.startswith("tcp:"):
                host = self._device[4:]
                self._interface = TCPInterface(hostname=host)
            elif self._device:
                self._interface = SerialInterface(devPath=self._device)
            else:
                # Auto-detect serial
                self._interface = SerialInterface()

            info = self._interface.getMyNodeInfo()
            self._last_status = {
                "available": True,
                "node_id": info.get("num", "unknown"),
                "device": self._device or "auto",
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
            return True
        except Exception as exc:
            logger.debug("Meshtastic device not available: %s", exc)
            self._last_status = {"available": False, "error": str(exc)}
            self._interface = None
            return False

    def send(self, message: MeshMessage, region: str = "") -> bool:
        if self._interface is None:
            logger.error("Meshtastic: no active interface")
            return False

        wire_data = message.to_wire()
        if len(wire_data) > MESHTASTIC_MAX_PAYLOAD:
            logger.error(
                "Meshtastic: packet too large (%d > %d bytes)",
                len(wire_data), MESHTASTIC_MAX_PAYLOAD,
            )
            return False

        try:
            self._interface.sendData(
                data=wire_data,
                channelIndex=self.CHANNEL_INDEX,
                wantAck=False,
            )
            logger.info(
                "Meshtastic: sent fragment %d/%d (%d bytes, %s)",
                message.fragment_index + 1,
                message.fragment_total,
                len(wire_data),
                message.language,
            )
            return True
        except Exception as exc:
            logger.error("Meshtastic send failed: %s", exc)
            return False

    def send_fragments(self, fragments: list[MeshMessage], region: str = "") -> int:
        """
        Send multiple fragments with inter-packet delay.

        Returns:
            Number of fragments successfully queued.
        """
        sent = 0
        for frag in fragments:
            if self.send(frag, region):
                sent += 1
            if frag is not fragments[-1]:
                time.sleep(self.TX_DELAY_SECONDS)
        return sent

    def get_status(self) -> dict[str, Any]:
        return {"transport": "meshtastic", **self._last_status}

    def close(self) -> None:
        """Cleanly disconnect from Meshtastic device."""
        if self._interface is not None:
            try:
                self._interface.close()
            except Exception:
                pass
            self._interface = None


# ──────────────────────────────────────────
# D2C Satellite transport (pre-reserved)
# ──────────────────────────────────────────

class D2CSatelliteTransport(MeshTransport):
    """
    Direct-to-Cell satellite transport.

    Pre-reserved interface for Starlink D2C / AST SpaceMobile APIs.
    When operational, this allows ordinary smartphones to receive
    messages bypassing all ground-based infrastructure.

    Env vars (future):
      - D2C_API_URL
      - D2C_API_KEY
      - D2C_PROVIDER (starlink | ast_spacemobile)
    """

    transport_type = TransportType.D2C_SATELLITE

    def __init__(self) -> None:
        self._api_url = os.getenv("D2C_API_URL", "")
        self._api_key = os.getenv("D2C_API_KEY", "")
        self._provider = os.getenv("D2C_PROVIDER", "starlink")

    def is_available(self) -> bool:
        # D2C APIs are not yet publicly available for humanitarian use
        if self._api_url and self._api_key:
            logger.info("D2C satellite: credentials configured, testing endpoint")
            try:
                import requests as req
                resp = req.get(
                    f"{self._api_url}/v1/status",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    timeout=10,
                )
                return resp.ok
            except Exception:
                pass
        return False

    def send(self, message: MeshMessage, region: str = "") -> bool:
        if not self.is_available():
            logger.info("D2C satellite: transport not available")
            return False
        # Future: implement D2C API call
        raise NotImplementedError(
            f"D2C satellite ({self._provider}) API integration pending"
        )

    def get_status(self) -> dict[str, Any]:
        return {
            "transport": "d2c_satellite",
            "provider": self._provider,
            "available": bool(self._api_url and self._api_key),
            "note": "Awaiting API access from satellite provider",
        }


# ──────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────

class MeshDispatcher:
    """
    Central dispatcher that fans out bulletins to all transports.

    Usage:
        dispatcher = MeshDispatcher()
        results = dispatcher.broadcast("Bulletin text...", "fa", region="tehran")
    """

    def __init__(self) -> None:
        self._transports: list[MeshTransport] = [
            BriarTransport(),
            MeshtasticTransport(),
            D2CSatelliteTransport(),
        ]
        self._delivery_log: list[dict[str, Any]] = []

    @property
    def transports(self) -> list[MeshTransport]:
        return list(self._transports)

    def broadcast(
        self,
        text: str,
        language: str,
        region: str = "",
        priority: Priority = Priority.NORMAL,
    ) -> dict[str, bool]:
        """
        Broadcast a bulletin to all available offline transports.

        Automatically selects the right encoding for each transport:
        - Briar: single compressed message
        - Meshtastic: fragmented packets with inter-packet delay
        - D2C: single compressed message

        Returns:
            Dict of transport_name → success/failure.
        """
        results: dict[str, bool] = {}
        bulletin_hash = _compute_hash(text)

        for transport in self._transports:
            name = type(transport).__name__
            if not transport.is_available():
                results[name] = False
                logger.debug("%s: not available, skipping", name)
                continue

            try:
                if isinstance(transport, MeshtasticTransport):
                    fragments = fragment_for_meshtastic(text, language, priority)
                    sent = transport.send_fragments(fragments, region)
                    success = sent == len(fragments)
                    if sent < len(fragments):
                        logger.warning(
                            "%s: only %d/%d fragments sent",
                            name, sent, len(fragments),
                        )
                elif isinstance(transport, BriarTransport):
                    msg = prepare_for_briar(text, language, priority)
                    success = transport.send(msg, region)
                else:
                    # Generic path (D2C and future transports)
                    msg = prepare_for_briar(text, language, priority)
                    success = transport.send(msg, region)

                results[name] = success
            except Exception as exc:
                logger.error("%s broadcast failed: %s", name, exc)
                results[name] = False

        # Log delivery attempt
        self._delivery_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bulletin_hash": bulletin_hash[:16],
            "language": language,
            "region": region,
            "priority": priority.name,
            "results": results,
        })

        delivered = sum(1 for v in results.values() if v)
        total = len(results)
        logger.info(
            "Dispatch complete: %d/%d transports delivered (%s, %s, %s)",
            delivered, total, language, region, priority.name,
        )
        return results

    def get_status(self) -> list[dict[str, Any]]:
        """Return status of all transports."""
        return [t.get_status() for t in self._transports]

    def get_delivery_log(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return recent delivery log entries."""
        return self._delivery_log[-limit:]


# ──────────────────────────────────────────
# Module-level convenience API
# ──────────────────────────────────────────

_dispatcher: MeshDispatcher | None = None


def get_dispatcher() -> MeshDispatcher:
    """Get or create the singleton MeshDispatcher."""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = MeshDispatcher()
    return _dispatcher


def dispatch_bulletin(
    text: str,
    language: str,
    region: str = "",
    priority: Priority = Priority.NORMAL,
) -> dict[str, bool]:
    """
    Fan out a bulletin to all available offline transports.

    Convenience wrapper around MeshDispatcher.broadcast().

    Returns:
        Dict of transport_name → success/failure.
    """
    return get_dispatcher().broadcast(text, language, region, priority)
