# Threat Model — CrisisBridge

> Last updated: 2026-04-02

## 1. Context

CrisisBridge operates in adversarial environments where state actors
actively monitor, disrupt, and manipulate civilian communications.
This document identifies known threats and the countermeasures
implemented or planned.

## 2. Threat Actors

| Actor | Capability | Motivation |
|-------|-----------|------------|
| State security services | Full network control, GPS jamming, SMS interception, "white SIM" privileged access | Surveillance, narrative control |
| State-affiliated media | Mass SMS campaigns, broadcast dominance during blackouts | Propaganda, public compliance |
| Automated scrapers | Bot enumeration, user list harvesting via Telegram API | Intelligence gathering |
| Criminal actors | Phishing via fake humanitarian messages | Financial fraud |

## 3. Threat Scenarios

### 3.1 Telegram Bot Surveillance

**Threat:** State actors use privileged network access ("white SIM
cards") to interact with the bot and systematically enumerate users.

**Countermeasures:**
- Bot does not store user ID ↔ geolocation associations (see `src/bot/commands.py`)
- Canary token system detects automated enumeration (see `src/security/canary.py`)
- Rate-based anomaly detection for unusual interaction patterns
- Honeypot commands that legitimate users would never discover

### 3.2 SMS Impersonation

**Threat:** Government sends mass SMS warning against foreign services.
CrisisBridge SMS could be confused with intimidation messages, or
state actors could forge CrisisBridge-branded messages.

**Countermeasures:**
- HMAC-SHA256 short codes on every outbound SMS (`src/sms/gateway.py`)
- Brand prefix `[CrisisBridge]` on all messages
- Iran (+98) region SMS delivery paused until secure protocol established
- Daily verification keys published on verified channels

### 3.3 GPS Jamming

**Threat:** Large-scale GPS jamming causes ~30% packet loss on
satellite connections and renders GPS-dependent routing unreliable.

**Countermeasures:**
- Routing uses Cell Tower ID or manual governorate selection, not GPS (`src/geo/routing.py`)
- Governorate-level granularity (never individual location)
- Static lookup tables with no GPS hardware dependency

### 3.4 Information Poisoning

**Threat:** Injection of false humanitarian data through compromised
or state-affiliated sources.

**Countermeasures:**
- Source credibility scoring on all content (`src/verification/trust_scorer.py`)
- State media labelled (not blocked) for transparency
- All claims linked to original source URLs
- Tiered trust display: ★★★★ (UN) → ★ (state media)

### 3.5 Network Enumeration

**Threat:** Automated tools enumerate all bot commands to map
functionality and find exploitable endpoints.

**Countermeasures:**
- Canary commands (`/debug_mode`, `/admin_panel`, etc.) trigger alerts
- Multiple canary hits from one user escalate to CRITICAL log level
- No admin functionality exposed through bot commands

## 4. Data Minimization Principles

1. **No PII storage** — Language preference only, keyed by hashed user ID
2. **No geolocation** — Never collect or store coordinates
3. **No message logs** — User messages are processed and discarded
4. **No interaction history** — Only aggregate anomaly counters retained
5. **Ephemeral by default** — In-memory storage, lost on restart

## 5. Operational Security

- All contributors must review this document before submitting code
  that touches user data or external APIs
- Security-sensitive PRs require explicit review tag `security-review`
- Incident response: security@agentmail.to (PGP key in SECURITY.md)

## 6. References

- Signal Protocol privacy design: https://signal.org/docs/
- OCHA data responsibility guidelines: https://centre.humdata.org/
- Sphere Handbook on humanitarian data protection
