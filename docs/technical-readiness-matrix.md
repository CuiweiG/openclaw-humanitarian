# Technical Readiness & Protection Risk Matrix

> **CrisisBridge** — Partner Review Document
> Version: 1.0 | Date: 2026-04-03
> Audience: International organization technical reviewers, protection officers, information management leads

---

## Executive Summary

CrisisBridge is a **verified multilingual public information distribution system prototype** designed for crisis-affected populations in the Middle East. It is **not** a mature protection platform, real-time early warning system, or case management tool.

**What it does well (ready for pilot):**
- Automated scraping of UN humanitarian reports with glossary-enforced multilingual translation (12 languages, 40 verified terms)
- Source credibility scoring (T1–T4 tiered trust labels)
- Telegram bot delivery with locale-aware UI
- Offline transport layer (Briar Mailbox + Meshtastic LoRa) for internet-denied environments

**What it does not do yet (not ready for pilot):**
- Real-time civilian early warning (airstrike alerts)
- Family reunification / Restoring Family Links case management
- Clinical mental health triage
- Persistent data storage
- Field-validated offline mesh deployment

---

## Module Readiness Assessment

| Module | Readiness | Risk Tier | Field Tested | Partner Required | Notes |
|--------|-----------|-----------|-------------|-----------------|-------|
| ReliefWeb/OCHA scraper | ✅ Production | 🟢 Green | N/A (API) | No | Exponential backoff, retry logic |
| Multilingual translator | ✅ Production | 🟢 Green | No | No | 12 languages; fa/dar/ps/ku/apc unverified by native speakers |
| 40-term glossary | ✅ Production | 🟢 Green | No | Yes (reviewers) | Per-term verification tracking; 5 languages unverified |
| Trust scorer (T1–T4) | ✅ Production | 🟢 Green | No | No | State media labelled, not blocked |
| Telegram bot | ✅ Production | 🟢 Green | Yes (limited) | No | 12 languages, locale file fallback |
| Simplified language | ✅ Production | 🟢 Green | No | No | Emoji markers for low-literacy |
| Quality check pipeline | ✅ Production | 🟢 Green | No | No | Word count, terminology, numeric format |
| SMS gateway (HMAC) | ⚠️ Scaffold | 🟡 Yellow | No | Yes (carrier) | Iran +98 paused; HMAC signing implemented |
| Offline mesh (Briar) | ⚠️ Implemented | 🟡 Yellow | **No** | Yes (field partner) | REST API integration; no field deployment |
| Offline mesh (Meshtastic) | ⚠️ Implemented | 🟡 Yellow | **No** | Yes (field partner) | Serial/TCP; compression + fragmentation; no field deployment |
| GPS-free routing | ⚠️ Implemented | 🟡 Yellow | No | No | 31 IR provinces + AF/SY/LB; Cell Tower ID stub |
| Supply chain tracker | ⚠️ Implemented | 🟡 Yellow | No | Yes (logistics cluster) | 6 routes; ReliefWeb status extraction |
| D2C satellite | 📋 Interface only | 🟡 Yellow | No | Yes (Starlink/AST) | Subject to GPS jamming; experimental |
| Airstrike alerts | ❌ Scaffold | 🔴 **Red** | **No** | **Mandatory** | OCHA flash polling works; ACLED not integrated; NO multi-source verification, NO human review gate, NO kill switch |
| Family links | ❌ Scaffold | 🔴 **Red** | **No** | **Mandatory** | Data model exists; NO encryption-at-rest, NO access control, NO DPIA, NO ICRC coordination |
| MHPSS | ⚠️ Partial | 🔴 **Red** | **No** | **Mandatory** | Self-help content + helpline numbers only; NO clinical triage capability; should not be presented as mental health service |
| Canary/scrape detection | ✅ Implemented | 🟢 Green | No | No | Rate-based + honeypot; alerts only, no auto-ban |

---

## Protection Risk Assessment

### Risks Created by System Operation

| Risk | Likelihood | Severity | Mitigation |
|------|-----------|----------|------------|
| Telegram metadata exposed to state actors | High (Iran, Syria) | High | Documented in SECURITY.md; Briar alternative for high-risk users |
| False/stale airstrike alert causes harm | Medium (if module activated) | **Critical** | Module disabled by default; activation requires checklist |
| Family links data breach exposes vulnerable individuals | Low (module not deployed) | **Critical** | Module restricted; activation requires DPIA |
| Machine translation error in life-safety context | Medium | High | Glossary enforcement; native speaker review pipeline needed |
| Mesh network misused for non-humanitarian messaging | Low | Medium | Content signing; no general messaging capability |
| SMS confused with government intimidation messages | Medium (Iran) | High | HMAC signing; Iran +98 paused; brand prefix |

### Risks Mitigated by System Operation

| Risk | How CrisisBridge Helps |
|------|----------------------|
| Information vacuum during internet blackout | Offline mesh delivery; SMS fallback |
| Language barrier for humanitarian reports | 12-language translation with glossary |
| Misinformation during crisis | Source credibility scoring; state media labelling |
| Aid distribution information inaccessible | Low-literacy formatting; multi-channel delivery |

---

## Governance Gaps (Must Address Before Partner Engagement)

| Gap | Priority | Status |
|-----|----------|--------|
| Native speaker glossary verification (fa/dar/ps/ku/apc) | P0 | Not started |
| User ID hashing in application logs | P1 | Planned |
| Data Protection Impact Assessment template | P1 | Not started |
| Partner SOP for red-tier module activation | P0 | Not started |
| Incident response plan | P1 | Not started |
| AAP complaints/feedback channel | P2 | Not started |
| CI/CD pipeline in .github/workflows | P2 | Not started |
| Language reviewer workflow documentation | P1 | Not started |
| Error correction / bulletin retraction mechanism | P1 | Partially implemented (scrape cycle supersedence) |
| Kill switch for alert module | P0 | Not implemented |

---

## Recommended Pilot Scope

**Phase 1 (Now — safe for pilot):**
- Verified public information distribution only (🟢 Green tier)
- Telegram bot with 12-language bulletins
- Source credibility labels on all content
- Offline mesh distribution to partner organizations (no direct civilian deployment)

**Phase 2 (After governance package complete):**
- SMS gateway pilot (non-Iran regions)
- Offline mesh direct-to-civilian via vetted field partners
- Supply chain digest for humanitarian coordinators

**Phase 3 (After DPIA + partner SOP + field testing):**
- Airstrike alert pilot (with full checklist satisfied)
- MHPSS referral pathways (with clinical partner)
- Family links (with ICRC coordination)

---

## Standards Referenced

- ICRC Handbook on Data Protection in Humanitarian Action (2nd ed., 2020)
- OCHA Data Responsibility Guidelines (2025)
- IASC Guidelines on MHPSS in Emergency Settings (2007)
- CHS Core Humanitarian Standard (2024)
- UNHCR AAP Framework
- CLEAR Global / Translators Without Borders guidance on humanitarian MT

---

*This document is designed to be shared with potential partner organizations
for technical and protection review. It intentionally highlights gaps and
risks alongside capabilities.*
