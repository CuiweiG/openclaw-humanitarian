# Briar Integration Research

> Status: Research / Proof-of-concept
> Based on: Scout research session, 2026-03-27

---

## What is Briar?

[Briar](https://briarproject.org/) is an open-source, end-to-end encrypted messaging app designed specifically for activists, journalists, and people in high-risk environments.

### Key Properties

| Property | Details |
|----------|---------|
| Encryption | End-to-end (BIP32 key derivation) |
| Transport options | Bluetooth LE, WiFi Direct, Tor (when internet available) |
| Architecture | Fully decentralised, no central server |
| Platform | Android (primary), future Linux headless |
| License | GPLv3 |
| Audit | Security audited by Cure53 (2017, 2021) |
| User base | Trusted by journalists in Belarus, Iran, Myanmar |

---

## Integration Strategy

### Option A: Briar Mailbox (Recommended)

Briar Mailbox is an official Briar feature (introduced in Briar 1.4) that allows messages to be stored on a server and retrieved when two parties are online at different times.

**How it works:**
1. A Briar Mailbox server runs on a VPS or Raspberry Pi
2. The bulletin bot uploads new bulletins to the Mailbox
3. Field volunteers sync the Mailbox when they briefly have internet
4. They relay bulletins to nearby users via Bluetooth (no internet needed for the last-mile relay)

**Implementation path:**
```
OpenClaw Bot → Briar Mailbox API → Volunteer Android Device
                                         ↓ Bluetooth LE
                              Displaced persons in camp
```

**Briar Mailbox API:**
- REST API over HTTPS
- Authentication: password-based (set on first run)
- Endpoints: `POST /v1/messages` to upload, `GET /v1/messages` to fetch
- Documentation: https://code.briarproject.org/briar/briar-mailbox

### Option B: Headless Briar Node (Future)

The Briar team is developing a headless Linux version that could run as a daemon:
- Run on a Raspberry Pi at a border crossing or camp
- Automatically push bulletin updates via WiFi Direct
- No human relay needed

**Status:** Headless Briar is in alpha as of Q1 2026. Not production-ready.

---

## Proof-of-Concept Architecture

```
┌─────────────────────────────────────────┐
│  OpenClaw Translation Pipeline          │
│  (translate.py + quality_check.py)      │
└────────────────────┬────────────────────┘
                     │ Compressed bulletin (≤200 words)
                     ▼
┌─────────────────────────────────────────┐
│  Briar Mailbox Server (VPS)             │
│  - Encrypted storage                    │
│  - HTTPS API endpoint                   │
│  - No plaintext logs                    │
└────────────────────┬────────────────────┘
                     │ Sync (when internet available)
                     ▼
┌─────────────────────────────────────────┐
│  Field Volunteer (Android + Briar)      │
│  - Downloads latest bulletins           │
│  - Goes offline to camp/border          │
└────────────────────┬────────────────────┘
                     │ Bluetooth LE / WiFi Direct
                     ▼
┌─────────────────────────────────────────┐
│  Displaced Persons (Android + Briar)    │
│  - Receive bulletins without internet   │
│  - Can reply / report needs             │
└─────────────────────────────────────────┘
```

---

## Message Format for Offline Delivery

Bulletins must be compressed for Briar (max message size: ~65 KB, practical limit ~2 KB for reliable sync):

```
[OPENCLAW] 2026-03-27
🆘 Iran/Lebanon Update

• WFP: 33,000 Afghan refugees receiving food aid in Iran
• Lebanon: Southern access restricted — evacuate if possible
• ICRC hotline: +961 1 333 407

Source: reliefweb.int
```

Target: 150–200 words maximum per bulletin.

---

## Security Considerations

- **No identifying data**: Bulletins contain no PII
- **End-to-end encryption**: Briar encrypts all messages before transmission
- **Deniability**: Briar messages use ephemeral keys where possible
- **Threat model**: Designed to resist surveillance by state actors
- **Contact list privacy**: Briar contact lists are never synced to any server

---

## Implementation Checklist

- [ ] Set up Briar Mailbox instance on VPS
- [ ] Create `briar_uploader.py` module using Mailbox REST API
- [ ] Integrate with `translate.py` post-processing step
- [ ] Test BLE relay in field conditions
- [ ] Document volunteer onboarding process

---

## References

- Briar Project: https://briarproject.org/
- Briar Mailbox source: https://code.briarproject.org/briar/briar-mailbox
- Security audit (Cure53, 2021): https://briarproject.org/news/2021-security-audit/
- EFF guide to Briar: https://ssd.eff.org/
