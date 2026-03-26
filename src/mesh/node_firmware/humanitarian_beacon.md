# Humanitarian Broadcast Beacon Design

## Concept

Each LoRa node automatically broadcasts the latest humanitarian bulletin at a configurable interval (default: every 15 minutes). This enables any civilian with a Meshtastic-compatible device to receive life-saving information without internet access.

**Core principle:** One-way push only. These nodes broadcast; they do not receive or relay operational data. This prevents misuse for military coordination.

## Message Format

```
[VERSION:1B][TYPE:1B][URGENCY:1B][LANG:2B][TIMESTAMP:4B][CONTENT:≤200B][SOURCE_HASH:4B][CHECKSUM:2B]
```

- **VERSION:** Protocol version (current: 0x01)
- **TYPE:** Message category (see protocol spec)
- **URGENCY:** Priority level (0x01–0x04)
- **LANG:** ISO 639-1 language code (e.g., `ar`, `fa`, `en`)
- **TIMESTAMP:** Unix epoch, 4 bytes (valid through 2106)
- **CONTENT:** UTF-8 encoded bulletin text, max 200 bytes
- **SOURCE_HASH:** First 4 bytes of SHA256 of the originating node ID
- **CHECKSUM:** CRC-16/CCITT of all preceding bytes

**Total packet size:** ~215 bytes — within LoRa SF7/BW125 single-frame limit.

## Broadcast Settings

| Parameter | Urban | Rural | Border |
|-----------|-------|-------|--------|
| Interval | 15 min | 30 min | 60 min |
| Frequency | 868.1 MHz (EU) / 915 MHz (US) | same | same |
| TX Power | 14 dBm | 20 dBm | 20 dBm |
| Spreading Factor | SF9 | SF12 | SF12 |
| Bandwidth | 125 kHz | 125 kHz | 125 kHz |
| Coding Rate | 4/5 | 4/8 | 4/8 |
| Estimated Range | 2 km | 10 km | 15+ km |

## Receiving Devices

Any device running **Meshtastic** firmware or app can receive these broadcasts:
- Android / iOS Meshtastic app
- Meshtastic Python CLI
- Custom receivers (ESP32 + SX1262 with standard LoRa library)

No pairing or authentication required — the broadcast is open and unencrypted by design, so any civilian device can receive it.

## Battery Life Calculation

Assumptions: 18650 cell (3000 mAh), ESP32 + SX1262, solar supplemented.

| State | Current Draw | Duty Cycle |
|-------|-------------|------------|
| Deep sleep | 10 µA | ~99% |
| Wake + process | 80 mA | ~0.5% |
| TX (20 dBm) | 120 mA | ~0.1% |
| RX listen | 12 mA | ~0.4% |

**Estimated battery life (no solar):** ~45 days  
**With 5V 3W solar panel (4h sun/day):** Indefinite in most Middle East climates

## Content Update Mechanism

Nodes store up to 5 bulletins in flash memory. Updates are pushed via:
1. **Direct USB/UART connection** during field visits
2. **Mesh back-channel** (encrypted, separate channel from broadcast)
3. **Satellite uplink** (Iridium/Starlink gateway nodes, where available)

## Ethical Safeguards

- No two-way communication via broadcast channel
- No location tracking of receivers
- Content reviewed by OCHA/humanitarian coordinator before deployment
- Hardware physically incapable of receiving on military frequencies
