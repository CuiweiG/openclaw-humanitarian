# Meshtastic Configuration Guide

> Target regions: Iran (915 MHz band), Lebanon (868 MHz band)
> Status: Configuration documented, field testing pending

---

## What is Meshtastic?

[Meshtastic](https://meshtastic.org/) is an open-source project that turns inexpensive LoRa radio modules into a long-range mesh network for text messaging — no internet required.

### Key Specs

| Parameter | Value |
|-----------|-------|
| Range | 2–15 km direct; up to 60 km with relay nodes |
| Message size | Up to 256 bytes (UTF-8) per packet |
| Battery | 12–48 hours on 18650 cell |
| Cost per node | $25–60 USD |
| License | GPLv3 |

---

## Recommended Hardware

### Primary: LILYGO T-Beam (ESP32-based)

- ESP32 microcontroller + built-in GPS + LoRa (SX1262) + WiFi + Bluetooth
- 18650 battery support
- ~$35–45 USD
- Available: AliExpress, Amazon

### Budget Alternative: Heltec LoRa32 V3 (ESP32-S3)

- ESP32-S3 chip, no GPS (lighter, cheaper)
- ~$20–30 USD
- Good for relay nodes without GPS need

---

## Frequency Bands

> ⚠️ Always use the legally authorised frequency band for your region.
> Unauthorized radio transmissions may be illegal.

| Region | Band | Notes |
|--------|------|-------|
| Lebanon | 868 MHz (EU/SG) | ISM band, license-free |
| Iran | 915 MHz (US) | Check local regulations |
| Turkey | 868 MHz (EU/SG) | ISM band |
| Afghanistan | 433 MHz (also usable) | Wider hardware availability |

---

## Firmware Setup

### Step 1: Flash Meshtastic Firmware

1. Download latest firmware from https://meshtastic.org/downloads/
2. Use the Meshtastic web flasher: https://flasher.meshtastic.org/
3. Select your device (T-Beam, Heltec, etc.)
4. Click "Flash"

### Step 2: Configure via Meshtastic App (Android/iOS)

Install Meshtastic app → connect via Bluetooth → configure:

#### Required Settings

```yaml
# Channel Configuration
channel:
  name: "CrisisBridge"
  psk: "[shared key - distribute via secure channel]"
  # LoRa modulation settings
  modem_preset: LONG_SLOW      # Best range, slower speed
  # or: MEDIUM_SLOW for balance

# Region
lora:
  region: EU_868               # Lebanon/Turkey
  # or: US_915                 # Iran (if legally permitted)
  tx_power: 20                 # dBm - check local limits

# Device Role
device:
  role: ROUTER_CLIENT          # Relay + receive messages
  # or: CLIENT                 # Endpoint only (lower power)
```

#### Optional: Node Description

```yaml
user:
  long_name: "CrisisBridge Aid Node"
  short_name: "OCLN"
```

---

## Network Topology for Humanitarian Use

```
[Border Crossing Node]
      |  LoRa (10-15 km)
      |
[Relay Node at High Point]
      |  LoRa (10-15 km)
      |
[Camp Node A] ---- [Camp Node B]
      |                  |
[Volunteer A]      [Volunteer B]
```

### Recommended Node Placement

1. **Border crossing nodes**: Powered (solar/mains), GPS enabled, antenna height maximised
2. **Relay nodes**: Hilltops or building rooftops, solar-powered
3. **Camp nodes**: Hand-carried by volunteers, battery-powered

---

## Message Format for Meshtastic

LoRa packets are limited to **256 bytes**. Bulletins must be heavily compressed:

```
OC|2026-03-27|IR/LB
WFP: 33k Afghans+food/Iran
S.Leb: access blocked
ICR: +96113334 07
reliefweb.int
```

**Encoding tips:**
- Use abbreviations: `IR` (Iran), `LB` (Lebanon), `WFP`, `UNHCR`
- Numbers: Use Western digits (0-9) for maximum compatibility
- Date: ISO format `YYYY-MM-DD`
- Prefix `OC|` identifies CrisisBridge bulletins

---

## Integration with CrisisBridge Pipeline

Future implementation plan:

```python
# Pseudocode: meshtastic_broadcast.py (not yet implemented)

from meshtastic import mesh_interface

def broadcast_bulletin(compressed_text: str, interface_port: str = "/dev/ttyUSB0"):
    """
    Broadcast a compressed bulletin over the local Meshtastic node.
    Requires a Meshtastic device connected via USB.
    """
    with mesh_interface.MeshInterface(devPath=interface_port) as iface:
        iface.sendText(
            text=compressed_text,
            channelIndex=0,  # CrisisBridge channel
            wantAck=False,   # Broadcast, no ACK needed
        )
```

Dependencies: `meshtastic` Python package (`pip install meshtastic`)

---

## Power & Deployment

### Solar Node (Border Crossing)

```
[6W Solar Panel] → [TP4056 Charger] → [18650 Battery] → [T-Beam Node]
```

- 6W panel provides sufficient power in Middle East sun
- Estimated cost: ~$60 per solar-powered node
- Estimated range: 24/7 operation

### Field Node (Volunteer)

- T-Beam with 18650 cell: 12–24 hours runtime
- Charge via USB-C (power bank or vehicle USB)
- Weight: ~120g with enclosure

---

## Security Notes

- **Encryption**: Meshtastic supports AES-128 channel encryption
- **PSK distribution**: Distribute Pre-Shared Key via secure channel (Signal, in-person) before deployment
- **No PII in messages**: Bulletins must not contain names, locations of individuals
- **Channel name**: Keep channel name neutral (avoid "aid" or "rescue" in active conflict zones)

---

## References

- Meshtastic docs: https://meshtastic.org/docs/
- LoRa frequency calculator: https://www.loratools.nl/#/airtime
- Python client: https://github.com/meshtastic/python
- ICRC digital security guide: https://www.icrc.org/en/digital-security-humanitarian
