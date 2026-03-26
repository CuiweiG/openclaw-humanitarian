# Mesh Network Deployment Guide

## Scenario 1: Urban Deployment — Beirut

**Coverage target:** Greater Beirut metropolitan area (~20 km²)  
**Node spacing:** Every 2 km (urban obstacles reduce effective range)  
**Topology:** Grid with redundant paths

### Node Placement
- Rooftops of hospitals, schools, mosques, community centers
- Priority: Southern suburbs (Dahieh), Palestinian camps (Shatila, Burj al-Barajneh), port area
- Avoid: Military installations, contested areas

### Specifications
| Parameter | Value |
|-----------|-------|
| Node count | ~80 nodes |
| Spacing | 1.5–2 km |
| TX power | 14 dBm (urban, reduce interference) |
| Spreading Factor | SF9 |
| Estimated cost | 80 × $43 = **$3,440** |
| Deployment time | 5–7 days (team of 4) |

### Hop Analysis
- Diameter of network: ~8 hops across city
- Each hop: ~2 km, latency ~2s
- End-to-end bulletin delivery: ~16 seconds

---

## Scenario 2: Rural Deployment — South Lebanon

**Coverage target:** Southern Lebanon (Tyre, Sidon, villages to Syrian border, ~1,500 km²)  
**Node spacing:** 5–10 km (open terrain, good LoRa propagation)  
**Topology:** Linear corridors along major roads, with branch nodes

### Node Placement
- Church/mosque rooftops in villages
- Water towers (excellent height, community access)
- UNIFIL positions (with permission)
- Key road intersections (N23, coastal highway)

### Specifications
| Parameter | Value |
|-----------|-------|
| Node count | ~40 nodes |
| Spacing | 5–10 km |
| TX power | 20 dBm |
| Spreading Factor | SF12 (maximum range) |
| Estimated cost | 40 × $43 = **$1,720** |
| Deployment time | 7–10 days (team of 3, vehicle required) |

### Coverage Map
```
[Beirut] ←10km→ [Sidon] ←8km→ [Tyre] ←12km→ [Naqoura/UNIFIL]
                    |                |
               [inland v.]      [border v.]
```

---

## Scenario 3: Cross-Border — Syria-Lebanon Border

**Coverage target:** Arsal region to Qalamoun (Syria), ~200 km border zone  
**Purpose:** Enable information flow for Syrian returnees crossing checkpoints  
**Topology:** Linear relay chain across border mountains

### Node Placement
- **Lebanese side:** Arsal outskirts, UNHCR registration points
- **Border crossing:** Masnaa/Al-Masnaa crossing area
- **Syrian side (if accessible):** Qusayr, Yabroud — in coordination with Syrian Arab Red Crescent

### Specifications
| Parameter | Value |
|-----------|-------|
| Node count | ~25 nodes |
| Spacing | 8–15 km (mountain terrain) |
| TX power | 20 dBm |
| Spreading Factor | SF12 |
| Estimated cost | 25 × $43 = **$1,075** |
| Deployment time | 10–14 days (requires border coordination) |

### Special Considerations
- **Jurisdiction:** Nodes on Lebanese side only without explicit Syrian authority permission
- **Content:** Multilingual (Arabic primary, Farsi secondary)
- **Security:** Nodes carry no user data, no logs — safe if seized

---

## Summary: Full Regional Deployment

| Region | Nodes | Cost | Timeline |
|--------|-------|------|----------|
| Beirut (urban) | 80 | $3,440 | Week 1–2 |
| South Lebanon (rural) | 40 | $1,720 | Week 2–3 |
| Tehran pilot | 150 | $6,600 | Week 3–5 |
| Syria-Lebanon border | 25 | $1,075 | Week 4–6 |
| **Total Phase 1** | **295 nodes** | **$12,835** | **6 weeks** |

*Note: Tehran deployment requires separate team and local humanitarian partnership.*

## Team Requirements

- **Field team per region:** 3–4 people
- **Technical lead:** 1 person (firmware, troubleshooting)
- **Local coordinator:** 1 person (community access, permissions)
- **Logistics:** Vehicle with ladder, basic tools, GPS

## Maintenance Schedule

| Activity | Frequency | Duration |
|----------|-----------|----------|
| Visual inspection | Monthly | 30 min/node batch |
| Panel cleaning | Quarterly | 5 min/node |
| Content update | Weekly (remote OTA) | Automated |
| Full inspection | 6 months | 1 day/region |
| Battery replacement | 3–5 years | As needed |
