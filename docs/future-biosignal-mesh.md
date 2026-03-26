# Future Research: Biosignal Transmission via LoRa Mesh

> Status: Conceptual / Future Work  
> Reference: Hackster.io 2025 "Transmission of biosignals via LoRa using Meshtastic"

## Concept

In internet-denied conflict zones, injured civilians often cannot reach 
medical facilities. If basic vital signs could be transmitted via our 
existing LoRa mesh network, remote medical triage becomes possible.

## What Could Be Transmitted

| Signal | Sensor | Cost | Data Rate |
|--------|--------|------|-----------|
| Heart rate | MAX30102 | $3 | ~4 bytes/reading |
| Blood oxygen (SpO2) | MAX30102 | (same) | ~4 bytes/reading |
| Body temperature | DS18B20 | $1 | ~2 bytes/reading |

**Total per reading: ~10 bytes** — well within LoRa payload limits (≤256 bytes).

## Architecture

```
[Patient] → [Wearable Sensor] → [LoRa Node] → ~~mesh~~ → [Medical Point]
                                                            ↓
                                                     [Triage Display]
```

## Privacy Considerations

- Vital signs are extremely sensitive personal data
- Must be encrypted end-to-end (AES-256)
- Only authorized medical personnel can decrypt
- No persistent storage — display only
- Requires explicit patient consent mechanism

## Technical Feasibility

- LoRa can transmit 10-byte readings every 30 seconds
- Battery impact: minimal (sensor + transmission < 50mA)
- Range: same as existing mesh (2-10km per hop)
- Challenge: ensuring data integrity over mesh hops

## Ethical Framework

This capability must only be deployed:
1. Under medical supervision
2. With patient or guardian consent
3. In partnership with established medical organizations (WHO, MSF)
4. With full ICRC data protection compliance

## Next Steps

1. Prototype with MAX30102 + ESP32 + Meshtastic firmware
2. Lab testing for data integrity over multi-hop mesh
3. Ethics review with medical humanitarian partners
4. Field pilot only with MSF or ICRC partnership

---

*This is a research direction, not a current capability. 
We include it here for transparency about our technical roadmap.*
