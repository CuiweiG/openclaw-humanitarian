# Data Flow Map — CrisisBridge

> Version: 1.0 | Last updated: 2026-04-03
> Required reading for all contributors and partner organizations.

---

## Purpose

This document provides an honest, auditable map of all data that enters,
moves through, and exits the CrisisBridge system. It replaces prior
statements of "zero personal data collection" with accurate descriptions
of actual system behaviour.

---

## 1. Data Ingested

| Source | Data Type | Personal Data? | Frequency |
|--------|-----------|---------------|-----------|
| ReliefWeb API | Humanitarian reports (title, body, date, source, URL) | No | Every 4 hours |
| OCHA API | Flash updates, situation reports | No | Every 4 hours |
| Telegram Bot API | User message text, Telegram user ID, chat ID | **Yes — user ID is personal data** | On user interaction |

## 2. Data Processed (In-Memory Only)

| Data | Processing | Stored? | Retention |
|------|-----------|---------|-----------|
| Report text | Translation, quality check, summarization | Cached in-memory | Until next scrape cycle (~4h) |
| User language preference | Keyed by Telegram user ID in `dict[int, str]` | In-memory only | **Lost on restart** |
| /shelter location param | Passed to shelter lookup (not yet implemented) | **Not persisted** | Discarded after response |
| /latest query | Triggers scraper → translator → response | **Not persisted** | Discarded after response |

## 3. Data Logged

The following data appears in application logs (stdout/journald):

| Log Entry | Contains PII? | Example |
|-----------|--------------|---------|
| `/start from user {id}` | **Yes — Telegram user ID** | `/start from user 123456789 (lang=fa)` |
| `/latest from user {id}` | **Yes — Telegram user ID** | `/latest from user 123456789` |
| `/shelter from user {id}, location={loc}` | **Yes — user ID + search text** | `/shelter from user 123456789, location=beirut` |
| ReliefWeb fetch results | No | `Fetched 5 reports.` |
| Translation errors | No | `Translation to 'fa' failed: timeout` |

### ⚠️ Known Issue: User ID in Logs

The current logging in `src/bot/commands.py` includes raw Telegram user IDs
at INFO level. This is a **known deviation** from the "no personal data"
claim in earlier documentation.

**Mitigation planned:** Replace raw user IDs with hashed identifiers in
log statements. Track in issue #XX.

## 4. Data Transmitted

| Destination | Data Sent | Encryption |
|-------------|-----------|------------|
| Telegram API | Translated bulletin text | TLS/MTProto (**not** E2E) |
| Briar Mailbox | Compressed bulletin (no user data) | E2E (Bramble protocol) |
| Meshtastic LoRa | Compressed bulletin fragments (no user data) | AES-128 PSK |
| SMS Gateway | Bulletin text + HMAC tag (no user data) | Carrier-dependent |

## 5. Data NOT Collected

The following data is **architecturally unavailable** to CrisisBridge:

- IP addresses of Telegram users (not exposed by Bot API)
- GPS coordinates of users
- Device identifiers
- Phone numbers (unless user voluntarily provides via family links — module restricted)
- Browsing history
- Message history (queries are stateless)

## 6. Restricted Modules — Additional Data Flows

The following modules handle sensitive data and are **disabled by default**.
They must not be activated without a Data Protection Impact Assessment (DPIA)
and a signed partner SOP.

### Family Links (`src/family_links/`)

| Data | Sensitivity | Current Status |
|------|------------|----------------|
| seeking_name | **High** — personally identifiable | Module exists, NOT production-deployed |
| last_known_location | **Critical** — could endanger individuals | Module exists, NOT production-deployed |
| contact_method | **High** — personally identifiable | Module exists, NOT production-deployed |

**Required before activation:**
- [ ] DPIA completed with partner organization
- [ ] Data retention policy (max 30 days, then purge)
- [ ] Encrypted-at-rest storage (not in-memory dict)
- [ ] Access control (only authorized case workers)
- [ ] Incident response plan for data breach
- [ ] ICRC Restoring Family Links coordination

### MHPSS (`src/mhpss/`)

Currently provides only:
- Static self-help content (breathing exercises, grounding techniques)
- Helpline numbers (publicly available)
- **No clinical assessment, no triage, no case management**

### Airstrike Alerts (`src/alert/`)

| Risk | Description |
|------|-------------|
| False positive | Could cause unnecessary panic and dangerous movement |
| False negative | Could create false sense of safety |
| Stale alert | Expired alert treated as current — lethal risk |
| Precision risk | Overly precise location data could be weaponized |

**Required before activation:**
- [ ] Multi-source cross-verification (minimum 2 independent sources)
- [ ] Geographic confidence interval (governorate-level only, never precise coordinates)
- [ ] TTL expiry with automatic retraction
- [ ] Human review gate before broadcast
- [ ] Kill switch accessible to operations team
- [ ] Correction/supersedence mechanism

---

*This document is versioned in the repository and must be updated whenever
data handling changes. Any PR that modifies data flows must update this
document or be rejected.*
