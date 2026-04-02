# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it
responsibly.

**DO NOT** open a public GitHub issue for security vulnerabilities.

### How to Report

Email: **aid@agentmail.to**

Subject line: `[SECURITY] Brief description`

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix timeline:** Depends on severity

### What Qualifies

- Authentication or authorization bypasses
- Data exposure risks (especially regarding affected populations)
- Injection vulnerabilities
- Dependencies with known CVEs
- Inaccurate security/privacy claims in documentation

### What Does NOT Qualify

- Missing security headers on static documentation pages
- Denial of service via API rate limiting (we're a volunteer project)
- Social engineering approaches

## Security Design Principles

1. **Minimal data collection** — We collect only language preference (keyed by Telegram user ID). No geolocation, no message content, no query logs are persisted. See `docs/data-flow.md` for the complete data flow map.
2. **No authentication required** — The bot works without user accounts.
3. **Source transparency** — All data comes from publicly available UN reports.
4. **Open source** — All code is auditable.
5. **Transport encryption** — All API calls use TLS 1.3. Telegram Bot API uses MTProto (server-to-server encrypted, **not** end-to-end encrypted — see note below). Briar provides end-to-end encryption. Meshtastic uses AES-128 channel encryption.

### ⚠️ Telegram Bot API Encryption Clarification

**The Telegram Bot API does NOT provide end-to-end encryption.** Telegram's end-to-end encryption (Secret Chats) is not available for bot interactions. Messages between users and the CrisisBridge bot are encrypted in transit (TLS/MTProto) but are accessible to Telegram's servers. This is a known limitation of the Telegram Bot API.

**Implication for users in high-risk environments:** Users interacting with the bot in countries with government surveillance should assume that message content (queries, language preferences) could theoretically be accessible via Telegram's infrastructure. The bot does not collect or store this data on our side, but we cannot guarantee Telegram's handling of it.

For users requiring end-to-end encrypted communication, the offline Briar mesh layer provides genuine E2E encryption.

## Data Handling Summary

| Data Type | Collected | Stored | Retention |
|-----------|-----------|--------|-----------|
| Telegram user ID | Yes (runtime) | In-memory only | Lost on restart |
| Language preference | Yes | In-memory only | Lost on restart |
| Query text (/latest, /shelter) | Processed | **Not stored** | Discarded after response |
| /shelter location parameter | Processed | **Not stored** | Discarded after response; logged at INFO level without user ID association |
| Family links data | Module exists | **Not implemented for production** | Module restricted — requires partner SOP |
| IP addresses | Not accessed | Not stored | N/A |
| GPS coordinates | Not accessed | Not stored | N/A |

See `docs/data-flow.md` for the complete data flow diagram.

## Risk-Tiered Module Classification

Modules are classified into three risk tiers. Red-tier modules are **disabled by default** and require explicit partner agreements and operational SOPs before activation.

| Tier | Modules | Activation |
|------|---------|------------|
| 🟢 Green | Scraper, translator, glossary, trust scorer, bot (info delivery), simplified language | Default ON |
| 🟡 Yellow | SMS gateway, supply chain tracker, offline mesh (Briar/Meshtastic) | Requires configuration |
| 🔴 Red | Airstrike alerts, family links, MHPSS referrals | **Disabled by default** — requires partner SOP, data protection assessment, human review chain |

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | ✅        |

## Dependencies

We regularly review dependencies for known vulnerabilities. If you notice an
outdated dependency with a known CVE, please open a regular issue.
