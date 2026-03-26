[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Languages](https://img.shields.io/badge/languages-9-orange.svg)](#what-we-do)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram)](https://t.me/openclaw_aid_bot)

<!-- Demo recording: see docs/demo-recording.md for instructions -->
<!-- ![Demo](docs/demo.svg) -->

# CrisisBridge

> **600,000–1 million households displaced. 28+ days of internet blackout. Most aid reports locked in English. We're breaking the language barrier.**

An open-source platform ensuring life-saving humanitarian information reaches every civilian, in their language, online or offline. Currently serving the 2026 Middle East crisis in 9 languages: Arabic, Persian, Dari, French, Spanish, Russian, English, Chinese, and Turkish.

**Read in your language:** &nbsp; [فارسی](README.fa.md) &nbsp;|&nbsp; [العربية](README.ar.md) &nbsp;|&nbsp; [中文](README.zh.md) &nbsp;|&nbsp; [Français](README.fr.md) &nbsp;|&nbsp; [Español](README.es.md) &nbsp;|&nbsp; [Русский](README.ru.md) &nbsp;|&nbsp; [English](README.md)

---

## The Problem

| Stat | Reality | Source |
|------|---------|--------|
| 🏚️ **600K–1M households** | Displaced in Iran alone in the current escalation | *UNHCR Flash Refugee Response Plan, March 2026* |
| 📵 **28+ days** | Iran internet blackout affecting ~90 million people | *NetBlocks, March 2026* |
| 👥 **33,000** | Afghan refugees in Iran receiving WFP food assistance | *WFP Situation Report #4, March 26, 2026* |
| 📄 **~90%** | Humanitarian situation reports published in English only | *OCHA, ReliefWeb language analysis* |

Humanitarian organizations produce life-saving information every day. It's locked in English PDFs. The people who need it most — displaced civilians in Iran, Afghanistan, Lebanon, Syria — can't read it.

We fix that.

---

## Quick Start

```bash
git clone https://github.com/CuiweiG/openclaw-humanitarian.git
cd openclaw-humanitarian
pip install -r requirements.txt
python src/demo.py  # See it work in 30 seconds
```

That's it. In 30 seconds you'll see a humanitarian bulletin scraped from ReliefWeb and translated using our glossary engine.

---

## Live Demo

📱 **Telegram Bot:** [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)

Send `/start` → choose your language → explore available crisis bulletins in your language.

---

## What We Do

| Product | Description |
|---------|-------------|
| 📡 **Crisis Scraper** | Auto-scrapes situation reports from ReliefWeb and OCHA APIs |
| 🌐 **Multilingual Translator** | AI-powered translation with humanitarian-specific glossary (40 terms, verification tracked) |
| 🤖 **Telegram Bot** | Delivers bulletins in 9 languages (AR/FA/DAR/ZH/TR/EN/FR/ES/RU) on demand and via push alerts |

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
│  AI model + glossary.json · 40 terms · 9 languages      │
│  Quality checks · Source verification                    │
└────────────────────────┬────────────────────────────┘
                         │
                    ┌────┴────┐
                    ▼         ▼
            ┌──────────┐ ┌──────────┐
            │ Telegram │ │  Future  │
            │   Bot    │ │ SMS/Mesh │
            └──────────┘ └──────────┘
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

---

## Roadmap

- [x] Multilingual crisis bulletins (AR/FA/DAR/EN/ZH/TR/FR/ES/RU)
- [x] ReliefWeb/OCHA auto-scraping pipeline
- [x] 40-term humanitarian glossary (8 languages)
- [x] Telegram bot with 9-language support
- [ ] Real-time shelter tracker for Lebanon
- [ ] Briar + Meshtastic offline communication layer
- [ ] SMS gateway for partial connectivity zones
- [ ] Pashto and Kurdish language support
- [ ] Browser extension for inline report translation

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

> *Coming soon. Help us get there by starring ⭐*

If you've written about this project, open a PR to add your link here.

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

We welcome translators, developers, humanitarian workers, and anyone who gives a damn.

- 🐛 [Report a bug](.github/ISSUE_TEMPLATE/bug_report.md)
- ✨ [Request a feature](.github/ISSUE_TEMPLATE/feature_request.md)
- 🌐 [Contribute a translation](.github/ISSUE_TEMPLATE/translation_request.md)
- 📖 Read the full guide: [CONTRIBUTING.md](CONTRIBUTING.md) · [بالعربية](CONTRIBUTING-ar.md) · [به فارسی](CONTRIBUTING-fa.md)

All skill levels welcome. If you speak a crisis-affected language and can verify translations, that's more valuable than code.

---

## We Don't Accept Donations

This project will always be free and open. If you want to help financially, please give directly to the people doing life-saving work on the ground:

- 🔴 **ICRC** — [icrc.org/en/donate](https://www.icrc.org/en/donate)
- 🔵 **UNHCR** — [donate.unhcr.org](https://donate.unhcr.org)
- ⚕️ **MSF / Doctors Without Borders** — [msf.org/donate](https://www.msf.org/donate)

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CuiweiG/openclaw-humanitarian&type=Date)](https://star-history.com/#CuiweiG/openclaw-humanitarian&Date)

---

## License

MIT — use it, fork it, build on it. See [LICENSE](LICENSE).

---

## Contact

- 📧 Email: [aid@agentmail.to](mailto:aid@agentmail.to)
- 🤖 Telegram: [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)
- 🐛 Issues: [GitHub Issues](https://github.com/CuiweiG/openclaw-humanitarian/issues)

---

*Built with urgency. Every star helps this project reach someone who needs it.*
