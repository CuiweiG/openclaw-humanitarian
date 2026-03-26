# Solar-Powered Autonomous Node Configuration

> Reference: IJARCCE 2025 — "Solar-Powered LoRa Mesh Networks for Disaster Communication"

## Design Goal

Deploy once, run for 6+ months with zero maintenance. Nodes must survive Middle East summers (55°C ambient), winter rains, and occasional dust storms.

## Hardware Stack

| Component | Model | Specs | Notes |
|-----------|-------|-------|-------|
| MCU + LoRa | Heltec WiFi LoRa 32 V3 | ESP32-S3 + SX1262 | Built-in OLED, USB-C |
| Solar Panel | SUNYIMA 5V 3W | 138×110mm, monocrystalline | Rated 600mA @ 5V |
| Battery | Samsung INR18650-30Q | 3000 mAh, 15A discharge | x2 in parallel = 6000 mAh |
| Charge Controller | CN3791 MPPT | 4.2V cutoff, 1A max charge | MPPT for panel efficiency |
| Protection | DW01A + FS8205 | Overcurrent + overdischarge | Critical in heat |
| Enclosure | IP65 ABS 150×100×70mm | UV-resistant | With cable glands |
| Antenna | 868MHz 5dBi fiberglass | N-connector | External, on enclosure lid |

## Circuit Overview

```
[Solar Panel 5V/3W]
        |
   [MPPT Controller CN3791]
        |            |
   [18650 x2]    [5V Rail]
   (6000 mAh)        |
        |        [Heltec V3]
        |------------|
                     |
              [SX1262 LoRa]
                     |
              [5dBi Antenna]
```

**Key design decisions:**
- MPPT controller (not simple linear) → ~30% more harvest from partial shade
- Two batteries in parallel → doubles capacity, improves temperature handling
- Separate 5V rail from solar → stable power even during cloud transitions

## Power Budget

| Mode | Current | Time/Day | Energy |
|------|---------|----------|--------|
| Deep sleep | 0.01 mA | 23.5h | 0.235 mAh |
| Active (TX) | 120 mA | 0.02h (15min TX) | 2.4 mAh |
| Active (CPU) | 80 mA | 0.1h | 8 mAh |
| **Total consumption** | | **24h** | **~11 mAh/day** |

**Solar harvest (conservative, 3h effective sun):**  
600 mA × 3h × 0.85 (MPPT efficiency) = **~1,530 mAh/day**

**Net daily balance:** +1,519 mAh → batteries never drain under normal conditions.

**Worst case (3 overcast days):** 3 × 11 mAh consumed vs. 6,000 mAh reserve = 36h autonomy at full power, or **>100 days** in deep-sleep-dominant mode.

## Charge Management

```c
// Pseudocode: CN3791 MPPT thresholds
#define SOLAR_FULL_V    4.20   // Stop charging
#define SOLAR_LOW_V     3.50   // Reduce TX power
#define SOLAR_CUTOFF_V  3.20   // Enter emergency sleep
#define SOLAR_RESUME_V  3.60   // Wake from emergency sleep
```

Node firmware checks battery voltage every 5 minutes. At low voltage:
1. Extend broadcast interval (15min → 60min)
2. Reduce TX power (20dBm → 14dBm)
3. Emergency sleep if below cutoff (wake every 6h to check)

## Thermal Management

Middle East summers regularly exceed 50°C ambient. Inside sealed enclosure: +10–15°C above ambient.

**Mitigations:**
- White or silver enclosure paint (reduces solar absorption by ~40%)
- Ventilation slots with mesh (prevents insects/dust, allows convection)
- ESP32 thermal throttle at 85°C (built-in)
- MPPT controller rated to 85°C operating
- 18650 cells: rated 60°C, derate charge above 45°C (firmware enforced)

**Cold weather (Lebanon winters, -5°C):**
- LiPo charging inhibited below 0°C (firmware + hardware protection)
- Minimum discharge: -20°C (well within range)
- No additional heating required

## Enclosure Mounting

- **IP65 rating:** Protected against dust ingress and water jets
- **Mounting:** Pole-mount bracket on 40mm tube, or wall-mount with 4×M6 bolts
- **Antenna:** External N-connector, antenna mounted vertically above enclosure
- **Cable entry:** 2× PG7 cable glands (solar panel + optional USB for maintenance)
- **Orientation:** Panel facing south (northern hemisphere), 30° tilt optimal

## Firmware OTA Update Strategy

Nodes can receive firmware updates via:
1. **USB-C direct** (during quarterly field visits)
2. **LoRa mesh OTA** (Meshtastic native, for small config changes)
3. **Manual flash** (ESP32 bootloader, for major updates)

Update schedule: Quarterly field visit recommended for cleaning panels and checking connections.
