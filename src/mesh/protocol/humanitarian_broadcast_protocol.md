# Humanitarian Broadcast Protocol (HBP) v1.0

## Overview

HBP defines a standardized, open, one-way broadcast protocol for transmitting humanitarian information over LoRa mesh networks in internet-denied environments. It is designed to be:

- **Simple:** Implementable on any LoRa device in <500 lines of code
- **Compact:** Fits in a single LoRa packet (≤255 bytes)
- **Multilingual:** Supports any UTF-8 language
- **Verifiable:** Checksum prevents corrupted messages from being displayed

---

## Message Format

```
[VERSION:1B][TYPE:1B][URGENCY:1B][LANG:2B][TIMESTAMP:4B][CONTENT:≤200B][SOURCE_HASH:4B][CHECKSUM:2B]
```

**Total minimum size:** 15 bytes  
**Total maximum size:** 215 bytes  

### Field Definitions

| Field | Size | Description |
|-------|------|-------------|
| VERSION | 1 byte | Protocol version. Current: `0x01` |
| TYPE | 1 byte | Message type code (see below) |
| URGENCY | 1 byte | Priority level (see below) |
| LANG | 2 bytes | ISO 639-1 language code (e.g., `ar`, `fa`, `en`) |
| TIMESTAMP | 4 bytes | Unix epoch timestamp, little-endian |
| CONTENT | ≤200 bytes | UTF-8 encoded bulletin text |
| SOURCE_HASH | 4 bytes | First 4 bytes of SHA256(node_id) — non-reversible |
| CHECKSUM | 2 bytes | CRC-16/CCITT of all preceding bytes |

---

## Message Types

| Code | Name | Description |
|------|------|-------------|
| `0x01` | ALERT | Evacuation order or immediate safety warning |
| `0x02` | SHELTER | Shelter location and availability update |
| `0x03` | MEDICAL | Medical facility status, supply info, first aid |
| `0x04` | WATER | Safe water point locations and status |
| `0x05` | SAFETY | Area safety status (passable/dangerous/unknown) |
| `0x06` | GENERAL | General humanitarian bulletin |
| `0xFF` | TEST | Test message — receivers should ignore or log only |

---

## Urgency Levels

| Code | Name | Meaning | Display |
|------|------|---------|---------|
| `0x01` | CRITICAL | Immediate life threat — act now | 🔴 RED |
| `0x02` | HIGH | Urgent — act within hours | 🟠 ORANGE |
| `0x03` | MODERATE | Important — act within days | 🟡 YELLOW |
| `0x04` | INFO | General information, no immediate action | 🟢 GREEN |

---

## Broadcast Schedule

Nodes broadcast on the following schedule (configurable):

| Urgency | Interval |
|---------|----------|
| CRITICAL | Every 5 minutes |
| HIGH | Every 15 minutes |
| MODERATE | Every 30 minutes |
| INFO | Every 60 minutes |

If multiple messages are queued, CRITICAL messages preempt lower-priority broadcasts.

---

## Example Packet (hex)

```
01          # VERSION = 0x01
01          # TYPE = ALERT
01          # URGENCY = CRITICAL
61 72       # LANG = "ar" (Arabic)
A0 4E 2C 68 # TIMESTAMP = Unix epoch
[200 bytes of UTF-8 Arabic text]
AB CD EF 01 # SOURCE_HASH
F2 3A       # CRC-16 CHECKSUM
```

---

## Receiver Behavior

1. **Validate checksum** — discard if invalid
2. **Check VERSION** — discard if unsupported version
3. **Deduplicate** — track SOURCE_HASH + TIMESTAMP; ignore exact duplicates
4. **Display** — show to user based on TYPE and URGENCY
5. **Relay** (optional) — re-broadcast after random delay (100–500ms) to extend range

---

## Security Model

- **No encryption on broadcast channel** — by design; humanitarian info is public
- **No authentication** — receiver cannot verify sender identity (acceptable tradeoff for simplicity)
- **Tamper detection** — CRC-16 catches accidental corruption
- **Anti-spam** — receivers can rate-limit by SOURCE_HASH (>10 messages/hour = suspect)

**Threat model:** This protocol is not suitable for operational security. It is for civilian information dissemination only.
