# Interoperability with Meshtastic, Briar, and Reticulum

## Overview

The Humanitarian Broadcast Protocol (HBP) is designed for one-way broadcasts. However, affected communities may already be using other mesh/resilient communication tools. This document describes how HBP can interoperate with three major platforms.

---

## 1. Meshtastic

**Compatibility: Native (Recommended)**

Meshtastic uses SX1262/SX1276 LoRa hardware — the same chipset as our nodes. HBP messages can be transmitted on a **secondary Meshtastic channel** without interfering with existing Meshtastic traffic.

### Integration Approach

**Option A: Dedicated HBP channel**
- Configure Meshtastic channel 2 (secondary) with HBP PSK = 0 (no encryption)
- HBP broadcasts on this channel; users see messages in Meshtastic app
- Requires: Custom Meshtastic channel config pushed to community devices

**Option B: Admin message type**
- Use Meshtastic's `ADMIN_APP` portnum (67) with HBP-formatted payload
- Devices with custom firmware can parse and display HBP content
- Standard Meshtastic devices will ignore unknown portnums gracefully

**Option C: Text message overlay**
- Format HBP content as plain text, broadcast on Meshtastic channel 0
- Works with unmodified Meshtastic apps — no custom firmware needed
- Trade-off: No structured metadata (type, urgency codes)

### Recommended for Phase 1: Option C
Fastest deployment; no firmware changes needed on civilian devices.

---

## 2. Briar

**Compatibility: Bridged (via gateway node)**

Briar is a peer-to-peer messaging app using Tor + Bluetooth + WiFi. It does not support LoRa natively. However, a **gateway node** with both LoRa and WiFi/BT can bridge HBP broadcasts into the local Briar mesh.

### Integration Architecture

```
[HBP LoRa Node] → [LoRa RX] → [Gateway (Raspberry Pi / ESP32 + WiFi)]
                                         |
                                    [Briar API]
                                         |
                              [Briar Mailbox / Forum]
                                         |
                              [Briar App Users via BT/WiFi]
```

### Implementation Notes
- Briar has no official external API; integration requires Briar's Android intent system or unofficial REST wrapper
- Gateway must run Android (for Briar) — Raspberry Pi not directly supported
- **Practical approach:** Gateway node posts to a Briar forum; community members subscribe to the forum
- Latency: ~30-60 seconds from HBP broadcast to Briar delivery

### Limitations
- Briar forum posts cannot be pushed; users must actively sync
- Requires at least one device with Briar within WiFi/BT range of gateway
- Not recommended as primary integration; use as fallback

---

## 3. Reticulum Network Stack (RNS)

**Compatibility: Native protocol bridge (Advanced)**

Reticulum is a cryptographic network stack designed for LoRa and other low-bandwidth links. It natively supports LoRa via RNode firmware, making it architecturally similar to our stack.

### Integration Approach

**Reticulum LXMF (Lightweight Extensible Message Format)** can carry HBP payloads as application data:

```python
# Pseudocode: HBP → Reticulum bridge
import RNS
import LXMF

def bridge_hbp_to_rns(hbp_packet):
    destination = RNS.Destination(
        identity=None,
        direction=RNS.Destination.OUT,
        type=RNS.Destination.PLAIN,
        app_name="humanitarian",
        aspects=["broadcast"]
    )
    message = LXMF.LXMessage(
        destination=destination,
        source=our_identity,
        content=hbp_packet.content,
        title=f"[{hbp_packet.type}] Humanitarian Update"
    )
    message_router.handle_outbound(message)
```

### Advantages of Reticulum Integration
- End-to-end encryption (for feedback channel, not broadcast)
- Automatic multi-hop routing
- Works on LoRa, packet radio, TCP/IP — future-proof
- Nomad Network (RNS app) already used by some humanitarian orgs

### Recommended Use Case
Use Reticulum for the **feedback channel** (community reports back to coordinators), while keeping HBP for one-way broadcasts. This gives us:
- HBP → open broadcast → civilian devices
- RNS/LXMF → encrypted feedback → coordination center

---

## Interoperability Matrix

| Platform | One-way broadcast | Two-way feedback | Encryption | Complexity |
|----------|-------------------|------------------|------------|------------|
| Meshtastic (Option A) | ✅ Native | ❌ | Optional | Low |
| Meshtastic (Option C) | ✅ Text overlay | ❌ | No | Very Low |
| Briar (bridged) | ✅ Via gateway | ✅ Limited | Yes (Briar) | High |
| Reticulum | ✅ Via bridge | ✅ Full | Yes (RNS) | Medium |

---

## Phase 1 Recommendation

1. **Broadcast:** HBP → Meshtastic Option C (plain text, channel 0)
2. **Feedback:** Reticulum LXMF on dedicated gateway nodes
3. **Gateway:** Raspberry Pi 4 at coordination hubs (Beirut, Tyre) with both LoRa and internet uplink

This provides maximum reach to civilians (Meshtastic is widely deployed) while maintaining a secure feedback channel for coordinators.
