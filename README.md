[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Languages](https://img.shields.io/badge/languages-12-orange.svg)](#what-we-do)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram)](https://t.me/openclaw_aid_bot)

<!-- Demo recording: see docs/demo-recording.md for instructions -->
<!-- ![Demo](docs/demo.svg) -->

# CrisisBridge

> **600,000–1 million households displaced. 28+ days of internet blackout. Most humanitarian reports available only in English. CrisisBridge is building a multilingual bridge.**

An open-source platform ensuring life-saving humanitarian information reaches every civilian, in their language, online or offline. Currently serving the 2026 Middle East crisis in 12 languages: Arabic, Lebanese Arabic, Persian, Dari, Pashto, Kurdish (Kurmanji), French, Spanish, Russian, English, Chinese, and Turkish.

**Read in your language:** &nbsp; [فارسی](README.fa.md) &nbsp;|&nbsp; [العربية](README.ar.md) &nbsp;|&nbsp; [中文](README.zh.md) &nbsp;|&nbsp; [Français](README.fr.md) &nbsp;|&nbsp; [Español](README.es.md) &nbsp;|&nbsp; [Русский](README.ru.md) &nbsp;|&nbsp; [English](README.md)

---

## The Problem

| Stat | Reality | Source |
|------|---------|--------|
| 🏚️ **600K–1M households** | Displaced in Iran alone in the current escalation | *UNHCR Flash Refugee Response Plan, March 2026* |
| 📵 **28+ days** | Iran internet blackout affecting ~90 million people | *NetBlocks, March 2026* |
| 👥 **33,000** | Afghan refugees in Iran receiving WFP food assistance | *WFP Situation Report #4, March 26, 2026* |
| 📄 **~90%** | Humanitarian situation reports published in English only | *OCHA, ReliefWeb language analysis* |

Humanitarian organizations produce critical situation reports daily — predominantly in English. Affected populations in Iran, Afghanistan, Lebanon, and Syria, who primarily speak Arabic, Persian, and Dari, lack access to this information.

CrisisBridge addresses this gap.

---

## ⚠️ Current Limitations

We believe in being upfront about where this project stands:

- **Telegram is unreachable in Iran.** With 28+ days of near-total internet blackout and connectivity at ~1% of normal levels, our primary distribution channel does not reach the population that needs it most. The offline mesh layer (Briar + Meshtastic + D2C satellite) is now a P0 MVP deliverable.
- **Persian, Dari, Pashto, Kurdish, and Lebanese Arabic glossary terms are unverified.** These are our most critical target languages, but zero terms have been validated by native speakers yet. Translations may contain errors that matter in life-or-death contexts. We urgently need native speaker reviewers.
- **Offline mesh transport is implemented but untested in the field.** `src/offline/mesh.py` provides Briar Mailbox and Meshtastic serial integration with compression, fragmentation, and dedup — but no field deployment has occurred yet.
- **No persistent storage.** Reports and user preferences are not persisted. Restarting the system loses all state.
- **ACLED API integration pending.** The airstrike alert module polls OCHA Flash Updates but the ACLED real-time feed requires an API key not yet configured.

If you can help with any of these, please [open an issue](https://github.com/CuiweiG/openclaw-humanitarian/issues) or reach out at aid@agentmail.to.

---

## Quick Start

```bash
git clone https://github.com/CuiweiG/openclaw-humanitarian.git
cd openclaw-humanitarian
pip install -r requirements.txt
python src/demo.py  # See it work in 30 seconds
```

The demo fetches a real report from the ReliefWeb API and demonstrates the translation pipeline with glossary-based terminology enforcement.

---

## Live Demo

📱 **Telegram Bot:** [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)

Send `/start` → choose your language → explore available crisis bulletins in your language.

---

## What We Do

| Product | Status | Description |
|---------|--------|-------------|
| 📡 **Crisis Scraper** | ✅ Live | Auto-scrapes situation reports from ReliefWeb and OCHA APIs |
| 🌐 **Multilingual Translator** | ✅ Live | AI-powered translation with humanitarian-specific glossary (40 terms, 12 languages, verification tracked) |
| 🤖 **Telegram Bot** | ✅ Live | Delivers bulletins in 12 languages on demand and via push alerts |
| 🔍 **Source Verification** | ✅ Live | Credibility scoring for all information sources |
| 🚨 **Airstrike Alert System** | 🔨 In Dev | Minute-level civilian safety alerts from ACLED, OCHA Flash Updates |
| 📶 **Offline Mesh Layer** | 🔨 In Dev | Briar + Meshtastic + D2C satellite for internet-denied environments |
| 📱 **SMS Gateway** | 🔨 In Dev | SMS delivery with HMAC verification; Iran region paused for safety |
| 📦 **Supply Chain Tracker** | 🔨 In Dev | WFP/OCHA logistics status for humanitarian coordinators |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   DATA SOURCES                       │
│  ReliefWeb API  ·  OCHA HDX  ·  UN Agencies RSS     │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                SCRAPER PIPELINE                      │
│  src/scraper/reliefweb.py  ·  src/scraper/ocha.py   │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              TRANSLATION ENGINE                      │
│  AI model + glossary.json · 40 terms · 12 languages     │
│  Quality checks · Source verification                    │
└────────────────────────┬────────────────────────────┘
                         │
                    ┌────┴────┬──────────┐
                    ▼         ▼          ▼
            ┌──────────┐ ┌────────┐ ┌──────────┐
            │ Telegram │ │ Alert  │ │ Offline  │
            │   Bot    │ │ System │ │SMS/Mesh/ │
            │          │ │(ACLED) │ │Satellite │
            └──────────┘ └────────┘ └──────────┘
```

Full architecture details: [docs/architecture.md](docs/architecture.md)

---

## Daily Output Example

Here's an illustrative example of a translated bulletin (data shown is for demonstration):

```
🚨 گزارش بحران — ۲۷ مارس ۲۰۲۶

📍 موقعیت: سوریه شمالی
👥 آوارگان: ۴۲۰٬۰۰۰ نفر
🏥 وضعیت پزشکی: بحرانی — ۳ بیمارستان فعال
🍞 توزیع غذا: روزهای دوشنبه و چهارشنبه، ساعت ۸–۱۲
🚪 گذرگاه‌های باز: باب الهوا (شمال)

منبع: OCHA، ۲۶ مارس ۲۰۲۶
@openclaw_aid_bot
```

---

## Glossary

The project maintains a 40-term humanitarian glossary (with per-term verification tracking) to ensure translation accuracy across all languages:

| English | العربية | فارسی | 中文 |
|---------|---------|-------|------|
| Displaced person | نازح | آواره | 流离失所者 |
| Evacuation route | طريق الإخلاء | مسیر تخلیه | 疏散路线 |
| Emergency shelter | مأوى طارئ | پناهگاه اضطراری | 紧急避难所 |
| Food distribution | توزيع الغذاء | توزیع غذا | 食品分发 |

📖 Full glossary: [data/glossary.json](data/glossary.json)

> ⚠️ **Persian (fa) and Dari (dar) translations are machine-generated and unverified.** Native speaker review is our top priority. See [Contributing](#contributing) if you can help.

---

## Roadmap

**✅ Live** — deployed and functional &nbsp;|&nbsp; **🔨 In Dev** — code exists, not production-ready &nbsp;|&nbsp; **📋 Planned** — documented, no code yet

### P0 — Critical (MVP Core)
- 🔨 Briar + Meshtastic + D2C satellite offline layer — **promoted to MVP core**
- 🔨 Airstrike civilian alert module (ACLED / OCHA Flash Updates / Airstrikes.live)
- 🔨 GPS-free routing via Cell Tower ID and governorate lookup tables

### P1 — High Priority
- 🔨 SMS gateway with HMAC verification + Iran region pause protocol
- ✅ Source credibility scoring engine (T1–T4 trust tiers)
- 🔨 D2C satellite API interface (Starlink / AST SpaceMobile pre-reserved)
- 🔨 Pashto and Kurdish (Kurmanji) glossary terms — **40 terms added, unverified**
- 🔨 Lebanese Arabic (Levantine) dialect support for 800K+ displaced in Lebanon

### Delivered
- ✅ Multilingual crisis bulletins (AR/APC/FA/DAR/PS/KU/EN/ZH/TR/FR/ES/RU)
- ✅ ReliefWeb/OCHA auto-scraping pipeline
- ✅ 40-term humanitarian glossary (12 languages, per-term verification tracking)
- ✅ Telegram bot with 9-language support
- ✅ Simplified language + emoji markers for low-literacy users
- 🔨 Family links tracing system (privacy-by-design)
- 🔨 Mental health & psychosocial support (MHPSS)
- 🔨 UXO/mine safety education module
- 🔨 Document protection guide
- 🔨 Security canary system for bot scraping detection
- 🔨 Supply chain status tracker for humanitarian coordinators

### P2 — Planned
- 📋 Audio bulletin generation (pluggable TTS backend)
- 📋 Emergency contact database (IR/LB/AF/SY)
- 📋 Real-time shelter tracker for Lebanon
- 📋 Browser extension for inline report translation

---

## Research Foundation

This project builds on peer-reviewed research in humanitarian NLP, crisis informatics, and offline communication systems. We maintain an active [research bibliography](docs/references.md) with 40+ references from IEEE, Frontiers, ICWSM, and leading humanitarian organizations.

**Key research areas:**

- **Humanitarian NLP** — Automated extraction of crisis-relevant information from unstructured reports ([Rocca et al. 2023](https://doi.org/10.3389/fdata.2023.1082787), IBM/WFP 2020)
- **Low-resource language MT** — Machine translation for languages with limited training data ([CLEAR Global Gamayun](https://clearglobal.org/gamayun/))
- **Offline mesh networks** — LoRa-based decentralized communication for internet-denied environments (IJARCCE 2025, Meshtastic)
- **Community feedback loops** — Two-way humanitarian information exchange via chatbots (TWB Uji, IRC Signpost)
- **Crisis data standards** — HumSet-compatible output format for interoperability with UN systems ([OCHA HumSet](https://www.thedeep.io/))

We actively seek collaboration with researchers. If your work intersects with ours, please [open an issue](https://github.com/CuiweiG/openclaw-humanitarian/issues) or email aid@agentmail.to.

---

## Featured In

> *No media coverage yet. If you write about this project, please open a PR to add your link here.*

---

## Limitations & Ethical Considerations

We believe in transparency about what this system can and cannot do:

- **AI translation is imperfect.** Especially for low-resource languages like Dari, translation quality varies. We maintain a [verified glossary](data/glossary.json) and welcome native speaker corrections.
- **We are not a replacement for professional humanitarian agencies.** Our role is information bridging, not aid delivery.
- **LLMs can hallucinate.** All AI-generated content goes through our [source verification system](src/verification/). Every claim links to its original source.
- **Offline mesh networks are experimental.** The Briar + Meshtastic layer is a research initiative, not a deployed solution yet.
- **User safety is paramount.** In countries with internet shutdowns, using communication tools can carry personal risk. We do not collect or store any user data.

See our [humanitarian compliance framework](docs/humanitarian-compliance.md) for detailed privacy and ethics policies.

---

## Contributing

We welcome translators, developers, humanitarian professionals, and volunteers of all backgrounds.

- 🐛 [Report a bug](.github/ISSUE_TEMPLATE/bug_report.md)
- ✨ [Request a feature](.github/ISSUE_TEMPLATE/feature_request.md)
- 🌐 [Contribute a translation](.github/ISSUE_TEMPLATE/translation_request.md)
- 📖 Read the full guide: [CONTRIBUTING.md](CONTRIBUTING.md) · [بالعربية](CONTRIBUTING-ar.md) · [به فارسی](CONTRIBUTING-fa.md)

All skill levels welcome. **Native speakers of Persian, Dari, Turkish, Pashto, and Kurdish who can verify translations are especially valued.**

---

## We Don't Accept Donations

This project does not accept financial contributions. To support humanitarian operations directly, please consider donating to established organizations:

- 🔴 **ICRC** — [icrc.org/en/donate](https://www.icrc.org/en/donate)
- 🔵 **UNHCR** — [donate.unhcr.org](https://donate.unhcr.org)
- ⚕️ **MSF / Doctors Without Borders** — [msf.org/donate](https://www.msf.org/donate)

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CuiweiG/openclaw-humanitarian&type=Date)](https://star-history.com/#CuiweiG/openclaw-humanitarian&Date)

---

## License

Released under the [MIT License](LICENSE). Free to use, modify, and distribute.

---

## Contact

- 📧 Email: [aid@agentmail.to](mailto:aid@agentmail.to)
- 🤖 Telegram: [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)
- 🐛 Issues: [GitHub Issues](https://github.com/CuiweiG/openclaw-humanitarian/issues)

---

*Developed to bridge the humanitarian information gap. Contributions and visibility help this project reach affected communities.*
