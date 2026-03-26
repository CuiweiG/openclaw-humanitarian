# Offline Communication Research — src/mesh/

> Research lead: Scout (OpenClaw AI Research Agent)
> Last updated: 2026-03-27
> Status: Active research

---

## Overview

This directory contains research notes and implementation guides for delivering humanitarian information **without internet connectivity**.

When governments cut internet access during conflicts — a documented tactic in Iran (2019, 2022), Lebanon (partial disruptions), and other conflict zones — traditional Telegram delivery fails. The mesh layer is our contingency.

---

## Research Conclusion

After evaluating multiple offline communication protocols, we recommend a **two-tier approach**:

| Tier | Technology | Range | Use Case |
|------|-----------|-------|----------|
| 1 (Short range) | **Briar** | 0–100m (BLE/WiFi) | Urban camp-to-camp messaging |
| 2 (Long range) | **Meshtastic + LoRa** | 2–60 km | Regional broadcast relay |

### Why not Bitchat?

Bitchat (Bluetooth mesh protocol) was evaluated but deprioritised:
- Very short range (10–30m practical)
- Limited Android compatibility
- No official APK distribution (security concern)

Briar provides similar P2P functionality with a larger user base, audited code, and established trust in the human rights community.

---

## Files in This Directory

| File | Contents |
|------|----------|
| `README.md` | This overview |
| `briar_bridge.md` | Briar integration research and implementation plan |
| `meshtastic_config.md` | Meshtastic hardware setup and channel configuration |

---

## Current Status

- [x] Protocol comparison research complete
- [x] Meshtastic configuration documented
- [x] Briar integration pathway identified (Mailbox API)
- [ ] Field testing in low-connectivity environment
- [ ] Integration with translation pipeline
- [ ] Automated bulletin broadcast to mesh nodes

---

## Key Insight

**The offline layer doesn't replace Telegram — it extends the last mile.**

Scenario:
1. A volunteer with internet access receives the latest bulletin via Telegram
2. They relay it to nearby displaced persons via Briar (BLE, no internet)
3. Meshtastic nodes at border crossing relay short bulletins to remote areas

This "store-and-forward" model works even under complete internet blackouts.
