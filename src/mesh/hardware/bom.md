# Bill of Materials (BOM) — Humanitarian LoRa Mesh Node

## Per-Node Components

| Component | Model | Unit Cost (USD) | Notes |
|-----------|-------|----------------|-------|
| LoRa Board | Heltec WiFi LoRa 32 V3 | $18.00 | ESP32-S3 + SX1262, USB-C, OLED |
| Solar Panel | SUNYIMA 5V 3W Mono | $6.00 | 138×110mm, weatherproof leads |
| Battery | Samsung INR18650-30Q ×2 | $4.00 | 2× 3000mAh in parallel |
| Charge Controller | CN3791 MPPT module | $2.50 | With protection circuit |
| Enclosure | IP65 ABS 150×100×70mm | $4.00 | UV-resistant, with cable glands |
| Antenna | 868MHz 5dBi Fiberglass | $8.00 | N-connector, 30cm |
| N-SMA Pigtail | 20cm RG316 | $1.50 | Waterproof |
| Mounting Bracket | Steel pole-mount | $2.00 | 40mm tube compatible |
| Cable Glands | PG7 ×2 | $0.50 | IP68 rated |
| Misc (screws, wire) | — | $0.50 | Heat shrink, silicone |
| **Total per node** | | **~$47.00** | Volume discounts available |

*Volume pricing (100+ units): approximately $38–42/node via AliExpress/LCSC*

---

## Regional Deployment Estimates

### Beirut (Urban — 80 nodes)

| Item | Qty | Unit | Total |
|------|-----|------|-------|
| Nodes (assembled) | 80 | $47 | $3,760 |
| Spare parts (10%) | 8 | $47 | $376 |
| Tools & consumables | — | — | $200 |
| Transport/logistics | — | — | $300 |
| **Subtotal** | | | **$4,636** |

### South Lebanon Rural (40 nodes)

| Item | Qty | Unit | Total |
|------|-----|------|-------|
| Nodes (assembled) | 40 | $47 | $1,880 |
| Spare parts (10%) | 4 | $47 | $188 |
| Vehicle rental | — | — | $500 |
| Tools & consumables | — | — | $150 |
| **Subtotal** | | | **$2,718** |

### Tehran Pilot (150 nodes)

| Item | Qty | Unit | Total |
|------|-----|------|-------|
| Nodes (assembled) | 150 | $47 | $7,050 |
| Spare parts (15%) | 22 | $47 | $1,034 |
| Local partner costs | — | — | $1,000 |
| Shipping/customs | — | — | $500 |
| **Subtotal** | | | **$9,584** |

### Syria-Lebanon Border (25 nodes)

| Item | Qty | Unit | Total |
|------|-----|------|-------|
| Nodes (assembled) | 25 | $47 | $1,175 |
| Ruggedized cases (extra) | 25 | $3 | $75 |
| Border logistics | — | — | $400 |
| **Subtotal** | | | **$1,650** |

---

## Phase 1 Total Budget

| Region | Nodes | Cost |
|--------|-------|------|
| Beirut | 80 | $4,636 |
| South Lebanon | 40 | $2,718 |
| Tehran pilot | 150 | $9,584 |
| Syria-Lebanon border | 25 | $1,650 |
| **Gateway nodes (×4)** | 4 | $800 |
| **Total Phase 1** | **299** | **$19,388** |

---

## Gateway Node (per coordination hub)

| Component | Model | Cost |
|-----------|-------|------|
| Raspberry Pi 4 (2GB) | RPi4B-2GB | $45 |
| LoRa HAT | RAK2287 (SX1302) | $89 |
| 4G/LTE modem | Quectel EC25 | $35 |
| UPS HAT | Waveshare UPS | $25 |
| Case + power | Industrial | $20 |
| **Gateway total** | | **~$214** |

4 gateways (Beirut ×2, Tyre, coordination center) = **$856**

---

## Procurement Notes

- **Primary supplier:** AliExpress (bulk), LCSC (components), Mouser (certified parts)
- **Lead time:** 2–3 weeks for bulk order from China; 1 week local if available
- **Local sourcing:** Heltec boards and solar panels sometimes available in Beirut/Istanbul electronics markets
- **Quality check:** Test each board before deployment; ~3–5% DOA rate from bulk orders
- **Customs:** Lebanon has no tariff on electronic components <$1,000/shipment; Iran requires NGO import permit

## Assembly Time

- **Per node (trained technician):** ~20 minutes
- **Per node (volunteer with guide):** ~45 minutes
- **Batch of 50 nodes:** 1 day (2 technicians)
