# System Architecture — OpenClaw Humanitarian Network

> Version: 1.0 | Last updated: 2026-03-27

---

## Overview

OpenClaw Humanitarian Network is a multi-layer information distribution system designed to deliver accurate, multilingual humanitarian bulletins to civilians in conflict zones — even under degraded or disconnected network conditions.

---

## ASCII Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════╗
║                    DATA SOURCES (Layer 0)                        ║
║  ┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ ║
║  │  ReliefWeb  │  │   OCHA   │  │   WFP    │  │   UNHCR     │ ║
║  │  API v2     │  │ Reports  │  │ SitReps  │  │  Updates    │ ║
║  └──────┬──────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘ ║
╚═════════╪══════════════╪═════════════╪════════════════╪═════════╝
          │              │             │                │
          ▼              ▼             ▼                ▼
╔══════════════════════════════════════════════════════════════════╗
║                    SCRAPING (Layer 1)                            ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  src/scraper/reliefweb.py  ─────────┐                   │    ║
║  │  src/scraper/ocha.py       ─────────┤→  parser.py       │    ║
║  │  (retry logic, error handling)      │   (HTML clean,    │    ║
║  │                                     │    key_points)    │    ║
║  └─────────────────────────────────────┴───────────────────┘    ║
╚══════════════════════════════════════════════════════════════════╝
          │
          ▼
╔══════════════════════════════════════════════════════════════════╗
║                  TRANSLATION (Layer 2)                           ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  src/translator/translate.py                             │    ║
║  │  ┌──────────────┐     ┌──────────────────────────────┐  │    ║
║  │  │ glossary.json│────►│  Pluggable Backend:           │  │    ║
║  │  │ (40 terms,   │     │  - ClaudeBackend (API)        │  │    ║
║  │  │  5 languages)│     │  - LocalModelBackend (future) │  │    ║
║  │  └──────────────┘     └──────────────────────────────┘  │    ║
║  │                                                           │    ║
║  │  src/translator/quality_check.py                         │    ║
║  │  (word count, terminology, number format, attribution)   │    ║
║  └─────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════╝
          │
          ▼
╔══════════════════════════════════════════════════════════════════╗
║                   DISTRIBUTION (Layer 3)                         ║
║                                                                  ║
║  ONLINE LAYER                   OFFLINE LAYER                    ║
║  ┌─────────────────────┐       ┌──────────────────────────────┐  ║
║  │  Telegram Bot       │       │  Mesh / Offline Network       │  ║
║  │  @openclaw_aid_bot  │       │                               │  ║
║  │                     │       │  ┌─────────────────────────┐ │  ║
║  │  /start             │       │  │  Briar (Android app)    │ │  ║
║  │  /latest            │       │  │  - P2P encrypted msgs   │ │  ║
║  │  /shelter [loc]     │       │  │  - BLE/WiFi Direct      │ │  ║
║  │  /language [code]   │       │  │  - No internet needed   │ │  ║
║  │  /help              │       │  └────────────┬────────────┘ │  ║
║  │                     │       │               │              │  ║
║  │  Languages:         │       │  ┌────────────▼────────────┐ │  ║
║  │  FA/DAR/AR/ZH/TR/EN │       │  │  Meshtastic + LoRa      │ │  ║
║  └─────────────────────┘       │  │  - 2-15 km range        │ │  ║
║                                │  │  - 915/868 MHz bands    │ │  ║
║                                │  │  - Text broadcasts      │ │  ║
║                                │  └─────────────────────────┘ │  ║
║                                └──────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Component Descriptions

### Layer 0 — Data Sources

| Source | Type | Coverage |
|--------|------|----------|
| ReliefWeb API v2 | REST API | Global humanitarian reports |
| OCHA | Via ReliefWeb (source filter) | UN coordination reports |
| WFP | Via ReliefWeb | Food security situation reports |
| UNHCR | Via ReliefWeb | Refugee & displacement reports |

All sources are publicly accessible, no authentication required.

### Layer 1 — Scraping

- **`src/scraper/reliefweb.py`**: Primary scraper. Queries ReliefWeb API with country filters (Iran, Lebanon) and a 24-hour window. Implements exponential-backoff retry logic.
- **`src/scraper/ocha.py`**: OCHA-specific scraper. Reuses `reliefweb.py` core with `source=OCHA` filter.
- **`src/scraper/parser.py`**: Extracts structured data from raw reports. Handles HTML stripping, key-point extraction, word count.

### Layer 2 — Translation

- **`src/translator/translate.py`**: Multilingual translation pipeline. Pluggable backend design supports Claude API or local models. Validates terminology against `glossary.json`.
- **`src/translator/quality_check.py`**: Automated quality gate. Checks word count (≤200), source attribution, terminology consistency, and numeric format (Persian ۱۲۳ vs Arabic ١٢٣).
- **`data/glossary.json`**: 40 humanitarian terms in 5 languages (EN/FA/DAR/AR/ZH).

### Layer 3a — Online Distribution (Telegram Bot)

The Telegram bot is the primary distribution channel for users with internet access.

- **Framework**: python-telegram-bot v20+ (async)
- **Commands**: `/start`, `/latest`, `/shelter`, `/language`, `/help`
- **Languages**: Persian, Dari, Arabic, Chinese, Turkish, English
- **Architecture**: Stateless handlers; user language preferences stored in-memory (Redis in production)

### Layer 3b — Offline Distribution (Research Phase)

For scenarios where governments restrict internet access:

**Briar** (recommended for high-censorship environments):
- Android-native encrypted P2P messaging
- Works over Bluetooth, WiFi Direct, or Tor
- No central server; fully decentralised
- Research status: API integration via Briar Mailbox being evaluated

**Meshtastic + LoRa**:
- LoRa radio mesh for text message relay
- Range: 2–15 km per node (up to 60 km with relay chain)
- Frequency bands: 868 MHz (EU/Lebanon), 915 MHz (Iran/US)
- Devices: ~$30–60 per node (LILYGO T-Beam, Heltec LoRa32)
- Research status: Configuration guide complete; field testing pending

---

## Deployment

### Minimum Requirements

| Component | Specification |
|-----------|--------------|
| OS | Linux (Ubuntu 22.04+ recommended) |
| Python | 3.11+ |
| RAM | 512 MB minimum |
| Storage | 1 GB minimum |
| Network | Outbound HTTPS (port 443) |

### Quick Deploy

```bash
git clone https://github.com/openclaw-humanitarian/openclaw-humanitarian.git
cd openclaw-humanitarian
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set TELEGRAM_BOT_TOKEN and ANTHROPIC_API_KEY
python -m src.bot.telegram_bot
```

### Environment Variables

```dotenv
TELEGRAM_BOT_TOKEN=your_token_here      # From @BotFather
ANTHROPIC_API_KEY=your_key_here         # Optional: Claude API for translation
```

### Production Deployment

For production, run as a systemd service or Docker container:

```bash
# systemd service example
[Unit]
Description=OpenClaw Humanitarian Bot
After=network.target

[Service]
WorkingDirectory=/opt/openclaw-humanitarian
EnvironmentFile=/opt/openclaw-humanitarian/.env
ExecStart=/opt/openclaw-humanitarian/venv/bin/python -m src.bot.telegram_bot
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Security Considerations

### Secrets Management
- **Never** commit `.env` files or API keys to the repository
- Use environment variables exclusively for secrets
- Rotate Telegram bot token immediately if compromised

### Data Privacy
- No personally identifiable information (PII) is collected or stored
- User language preferences stored in-memory only (lost on restart)
- All API calls are outbound HTTPS; no inbound ports required

### Content Integrity
- All bulletins sourced from verified UN/OCHA publications
- Source URLs included in every bulletin for verification
- Quality check pipeline validates accuracy before publication

### Network Security
- Bot operates in polling mode (no inbound webhook required)
- No database exposed to internet
- Offline layer (Briar/Meshtastic) uses end-to-end encryption by default

### Humanitarian Neutrality
- No political content; strictly factual humanitarian information
- No affiliation with any government or military
- Code of conduct enforced for all contributors (see CONTRIBUTING.md)

---

## Agent Architecture (Internal)

The system uses three named AI agent roles:

| Agent | Role | Implementation |
|-------|------|----------------|
| **Scout** | Research & data retrieval | `src/scraper/` |
| **Babel** | Translation & terminology | `src/translator/` |
| **Quill** | Publishing & formatting | `src/bot/` |
