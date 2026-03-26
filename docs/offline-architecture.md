# Offline Architecture: Dual-Layer Mesh Network

> **OpenClaw Humanitarian Network** — Technical Design Document  
> Version: 1.0 | Audience: Engineers, Field Coordinators, Security Reviewers

---

## 1. Overview

### Why We Need an Offline Layer

Internet shutdowns are not hypothetical — they are a documented, recurring tactic used during humanitarian crises:

- **Iran 2022–2025**: The government throttled and blocked internet access during protests and civil unrest. During the Mahsa Amini protests (Sept 2022), mobile internet was cut nationwide for days.
- **Lebanon 2024**: Israeli strikes on infrastructure caused repeated outages in southern regions where displacement was highest.
- **Syria ongoing**: Large swaths of displacement corridors have no cellular or internet coverage.

When the network goes down, Telegram bots stop working. The populations that need life-saving information most urgently — people fleeing conflict — are exactly the ones most likely to lose connectivity.

**OpenClaw's response**: build a degradation-tolerant architecture that continues delivering shelter locations, aid contact numbers, and emergency guidance even when the internet is completely unavailable.

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│              ONLINE LAYER (Normal)              │
│  Telegram Bot ←→ ReliefWeb/OCHA ←→ AI Pipeline  │
│         ↕ (internet available)                   │
├─────────────────────────────────────────────────┤
│           MESH LAYER (Degraded)                 │
│  Briar (BLE/WiFi P2P) + Meshtastic (LoRa)      │
│  Range: 10-30m (Briar) / 2-10km (Meshtastic)   │
│         ↕ (no internet)                          │
├─────────────────────────────────────────────────┤
│          BROADCAST LAYER (Minimal)              │
│  Shortwave Radio (one-way, continental range)   │
│  Partner: Radio Zamaneh                         │
└─────────────────────────────────────────────────┘
```

### Layer Activation Logic

```
INTERNET AVAILABLE?
  ├─ YES → Online Layer (Telegram + live API data)
  └─ NO  → MESH AVAILABLE?
             ├─ YES → Mesh Layer (Briar + Meshtastic)
             └─ NO  → Broadcast Layer (shortwave, listen-only)
```

The system degrades gracefully. Users in areas with partial connectivity may have access to Mesh Layer while their neighbor with a shortwave radio receives broadcast-only updates.

---

## 3. Layer 1: Briar (Short-Range Mesh)

### 3.1 Why Briar — Not Bitchat

| Criteria | Briar | Bitchat |
|----------|-------|---------|
| Platform | Android (native) | iOS exclusive |
| Persian language UI | ✅ Yes | ❌ No |
| Security audit | ✅ Cure53 (2017, 2021) | ⚠️ None published |
| P2P transport | BLE + WiFi Direct | BLE only |
| No internet required | ✅ Full functionality | ✅ Yes |
| Iran market share fit | ✅ ~80% Android users | ❌ ~20% iOS users |
| Open source | ✅ GPLv3 | ✅ MIT |

**Verdict**: Briar is the only production-ready, security-audited, Android-native mesh messaging app with Persian language support. Bitchat is technically interesting but is unavailable to 80% of our target user base.

### 3.2 How Briar Works (No Internet)

```
Device A (Android)
    │
    ├── Bluetooth LE discovery → Device B within ~10m
    │
    └── WiFi Direct → Device C within ~30m
              │
              └── Multi-hop relay → Device D (not in direct range)
```

Messages propagate through the mesh hop-by-hop. A bulletin broadcast from a volunteer's phone in Beirut's Hamra district can reach a displaced family 3–4 hops away (up to ~100m total) without any internet.

### 3.3 Message Format (Standardised Bulletin)

All OpenClaw bulletins transmitted over Briar use a compact plaintext format:

```
[OPENCLAW-AID v1]
DATE: 2026-03-26
LANG: fa
HASH: sha256:a3f2...  ← Content integrity check
---
سرپناه‌های موجود در بیروت:
• مدرسه UNRWA الزیتون — ظرفیت ۲۰۰ نفر
• مرکز جمعی ریفی — ظرفیت ۵۰۰ نفر
• خط کمک WFP: +961-1-XXX-XXX
---
[END]
```

Key properties:
- **HASH field**: SHA-256 of the body content. Receivers verify integrity before relay.
- **Maximum size**: 4 KB per bulletin (Briar message limit)
- **Language field**: Allows receivers to filter bulletins by language preference

### 3.4 Briar Mailbox API Integration

Briar's [Mailbox API](https://code.briarproject.org/briar/briar/-/wikis/Mailbox-API) allows a persistent internet-connected node to act as a relay ("mailbox") for offline devices. OpenClaw deploys one Briar Mailbox node per city cluster:

```
┌─────────────────┐
│  Cloud Server   │  ← Fetches from ReliefWeb every 4h
│  (VPS with      │  ← Formats bulletins
│   internet)     │  ← Publishes to Briar Mailbox API
└────────┬────────┘
         │ HTTPS (when internet works)
         ▼
┌─────────────────┐
│  Briar Mailbox  │  ← Volunteers access this when
│  Node (Android  │    internet briefly restores
│  device on UPS) │  ← Then relay offline via BLE/WiFi
└────────┬────────┘
         │ BLE / WiFi Direct
         ▼
    [Field devices]
```

When internet is cut, the Mailbox node stores the last downloaded bulletin and continues serving it to nearby devices via BLE for up to 72 hours.

---

## 4. Layer 2: Meshtastic (Mid-Range LoRa)

### 4.1 Why LoRa for Humanitarian Use

LoRa (Long Range) radio operates in the sub-GHz ISM band. It can transmit small data packets (up to 255 bytes) across 2–10 km with line-of-sight, consuming milliwatts of power. This makes it ideal for:

- Border crossings with no cellular coverage
- Rural areas where BLE/WiFi range is insufficient
- Battery-constrained deployments (solar + 18650 cell)

### 4.2 Frequency Band Selection

| Region | Band | Notes |
|--------|------|-------|
| Europe / Middle East | **868 MHz** | ISM band, license-free |
| Americas | 915 MHz | FCC part 15 |
| Asia | 433 MHz | Wider support but more interference |

**We use 868 MHz** for deployments in Lebanon, Syria border regions, and coverage of Iranian diaspora networks near Turkey/Armenia. This band is:
- Legal to operate license-free in Lebanon, Turkey, EU
- Standard for LILYGO T-Beam hardware
- Less congested than 433 MHz in urban environments

### 4.3 Meshtastic Configuration (Broadcast Mode)

```yaml
# meshtastic-config.yaml
lora:
  region: EU_868
  modem_preset: LONG_SLOW       # Max range, low data rate (~250bps)
  hop_limit: 3                  # Relay through up to 3 intermediate nodes
  tx_power: 20                  # dBm (100mW, within legal limits)

channel:
  name: "OPENCLAW-AID"
  psk: <pre-shared AES-256 key> # Distributed to partner organizations

position:
  position_broadcast_secs: 0   # DISABLED — do not broadcast GPS coordinates
  smart_broadcast_enabled: false

telemetry:
  device_update_interval: 0    # DISABLED — no telemetry leak
```

**Security note**: Position broadcasting is **explicitly disabled** to prevent tracking of displaced persons or aid workers.

### 4.4 Solar Power Configuration

Field nodes are designed for unattended outdoor deployment:

```
[6W Solar Panel]
      │ 5V DC
      ▼
[TP4056 Charge Controller]
      │
      ▼
[18650 3000mAh Battery] ←→ [LILYGO T-Beam ESP32]
                                    │
                                    └── [LoRa SX1262 Radio]
                                    └── [GPS Module] (disabled in software)
```

**Runtime estimates**:
- Full sun (6h/day): self-sustaining indefinitely
- Overcast 3 days: 48h battery backup
- Transmit duty cycle: ~1% (burst mode, one bulletin per hour)

---

## 5. Why NOT SMS

SMS was evaluated and rejected for three independent reasons:

### 5.1 OFAC Sanctions — Technical Blockade

The US Office of Foreign Assets Control (OFAC) sanctions against Iran mean that US-based telecommunications providers cannot legally offer services terminating in Iran:

- **Twilio**: Explicitly blocks Iran (+98) in its SMS routing. Even NGO accounts.
- **Vonage (Ericsson)**: Same restriction.
- **MessageBird / Sinch**: Same restriction under EU/US dual-use regulations.

No commercially viable SMS gateway supports Iranian numbers without violating sanctions, regardless of humanitarian intent.

### 5.2 Surveillance Risk — Unacceptable for Target Population

SMS transmits:
- **Plaintext content** — readable by the carrier network operator
- **Metadata** — sender number, receiver number, timestamp, tower location
- All of this is **accessible to governments** via lawful intercept systems that Iran, Lebanon, and Syria all have deployed

For a displaced person in Iran asking "where is the nearest UNHCR shelter," having that query intercepted creates real security risk. SMS cannot be end-to-end encrypted at the protocol level.

### 5.3 Cost at Scale

At $0.005–0.03 per message, SMS costs become prohibitive at scale. Mesh radio is a one-time hardware cost.

---

## 6. Why NOT Bitchat

Bitchat is a BLE mesh messaging app from Block (Jack Dorsey's company). It is technically sophisticated but unsuitable for this deployment:

| Issue | Impact |
|-------|--------|
| **iOS exclusive** | Excludes ~80% of Iran/Lebanon users (Android majority) |
| **No Persian (Farsi) UI** | Target users cannot navigate the app |
| **No Dari support** | Afghan refugee population excluded |
| **No security audit** | Cannot vouch for safety of displaced persons |
| **English-only documentation** | Field volunteers cannot configure |

**Conclusion**: Bitchat is technically interesting but geographically and linguistically mismatched to this deployment. Briar solves the same problem with superior fit.

---

## 7. Hardware BOM (Bill of Materials)

Per Meshtastic relay node, outdoor deployment:

| Component | Model | Unit Cost | Notes |
|-----------|-------|-----------|-------|
| LoRa Board | LILYGO T-Beam v1.2 | $25 | ESP32 + SX1262 + GPS header |
| Solar Panel | 6W 5V monocrystalline | $8 | 115×165mm, weatherproof |
| Battery | 18650 Li-ion 3000mAh | $5 | NCR18650B or equivalent |
| Charge Controller | TP4056 with protection | $1 | Built into T-Beam v1.2 |
| Enclosure | IP65 waterproof ABS | $4 | 115×90×55mm |
| Antenna | 868 MHz 3dBi external | $3 | SMA connector |
| Mounting | UV-resistant zip ties + bracket | $1 | Pole/wall mount |
| **Total per node** | | **~$47** | Volume discounts available |

### Volume Pricing (estimate, 50+ units)

| Quantity | Unit Cost | Total |
|----------|-----------|-------|
| 10 nodes | ~$47 | $470 |
| 50 nodes | ~$38 | $1,900 |
| 100 nodes | ~$32 | $3,200 |

A city-scale deployment covering 10 km² requires approximately 20–30 nodes.

---

## 8. Deployment Scenarios

### 8.1 Urban — Beirut

**Context**: High population density, frequent Israeli airstrikes on infrastructure, repeated internet outages.

**Primary technology**: **Briar** (BLE + WiFi Direct)  
**Rationale**: High device density means Briar's 10–30m range creates a functional mesh across dense apartment buildings. A single bulletin can propagate through 20+ hops across a neighborhood.

**Network topology**:
```
[Aid worker: Briar Mailbox Node]
    │ WiFi Direct
    ├── [Family A] → [Family B] → [Family C]
    │                               │
    └── [Family D]              [Family E] → ...
```

**Deployment**: Volunteers pre-loaded with Briar + OpenClaw bulletin channel.

### 8.2 Rural — South Lebanon

**Context**: Low population density, damaged cellular towers, large physical distances between displaced families.

**Primary technology**: **Meshtastic LoRa (868 MHz)**  
**Rationale**: BLE range is insufficient across 1–5 km of open terrain. LoRa reaches farmhouses and hilltop shelters that Briar cannot.

**Node placement**: Nodes mounted on water towers, church rooftops, school buildings — structures likely to survive shelling and visible from surrounding terrain.

**Coverage per node**: ~3 km radius (flat terrain), ~5 km (elevated placement)

### 8.3 Border — Syria–Lebanon Corridor

**Context**: Active displacement flow across Masnaa crossing, no internet, no cellular, mixed Syrian/Lebanese/Afghan population.

**Primary technology**: **Meshtastic LoRa + solar power**  
**Rationale**: Border crossings are remote, crossing times can take days, and power is unavailable. Solar-powered nodes provide continuous coverage.

**Special configuration**:
- Arabic + Farsi + Dari bulletins pre-loaded
- 72-hour bulletin cache on each node
- Nodes sealed to IP65 for dust and rain

**UNHCR/IOM coordination**: Border crossing nodes are pre-registered with UNHCR Lebanon as "informal information infrastructure" — not monitored, not logged, humanitarian designation.

---

## 9. Security Considerations

| Threat | Mitigation |
|--------|------------|
| Node seizure | No user data stored; only pre-signed bulletins |
| Content tampering | SHA-256 hash in bulletin header; receivers reject mismatches |
| Traffic analysis | No GPS broadcast; no user identifiers in LoRa packets |
| Mesh infiltration | Pre-shared AES-256 channel key distributed only to partner orgs |
| Node tracking | Transmit duty cycle <1%; no persistent device ID in packets |

---

*This document is maintained by the OpenClaw technical team. For field deployment support, contact the mesh hardware coordinator via secure channel.*
