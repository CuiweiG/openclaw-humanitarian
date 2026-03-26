[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Languages](https://img.shields.io/badge/languages-6-orange.svg)](#what-we-do)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram)](https://t.me/openclaw_aid_bot)

# OpenClaw Humanitarian Network

> **3.2 million displaced. 4 weeks of internet blackout. Zero multilingual civilian warning systems. We're building one.**

An open-source AI pipeline that scrapes humanitarian reports from OCHA, ReliefWeb, and UN agencies — then translates them into Arabic, Farsi, Dari, Chinese, Turkish, and English — and delivers them to civilians in crisis zones via Telegram, SMS, and offline mesh networks.

**Read in your language:** &nbsp; [فارسی](README.fa.md) &nbsp;|&nbsp; [العربية](README.ar.md) &nbsp;|&nbsp; [中文](README.zh.md) &nbsp;|&nbsp; [English](README.md)

---

## The Problem

| Stat | Reality |
|------|---------|
| 🏚️ **3.2 million** | People displaced in active conflict zones with no local-language information |
| 📵 **28 days** | Average internet blackout duration during major crisis events |
| ☠️ **2,698** | Civilian deaths directly linked to missed evacuation warnings (2023–2024) |
| 📄 **94%** | Humanitarian situation reports published in English only |

Humanitarian organizations produce life-saving information every day. It's locked in English PDFs. The people who need it most — displaced civilians in Sudan, Gaza, Lebanon, Afghanistan — can't read it.

We fix that.

---

## Quick Start

```bash
git clone https://github.com/openclaw-humanitarian/openclaw-humanitarian.git
cd openclaw-humanitarian
pip install -r requirements.txt
python src/demo.py  # See it work in 30 seconds
```

That's it. In 30 seconds you'll see a live humanitarian bulletin scraped and translated into 6 languages.

---

## Live Demo

📱 **Telegram Bot:** [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)

Send `/start` → choose your language → receive today's crisis bulletins in your language.

---

## What We Do

| Product | Description |
|---------|-------------|
| 📡 **Crisis Scraper** | Auto-pulls situation reports from ReliefWeb, OCHA, and UN agencies every 6 hours |
| 🌐 **Multilingual Translator** | AI-powered translation with humanitarian-specific glossary (40+ verified terms) |
| 🤖 **Telegram Bot** | Delivers bulletins in AR / FA / DAR / ZH / TR / EN on demand and via push alerts |

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
│  AI model + glossary.json (40 verified terms)        │
│  → AR  → FA  → DAR  → ZH  → TR  → EN               │
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

Here's what a civilian in Iran or Afghanistan receives every morning:

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

The project maintains a verified 40-term humanitarian glossary to ensure translation accuracy across all languages:

| English | العربية | فارسی | 中文 |
|---------|---------|-------|------|
| Displaced person | نازح | آواره | 流离失所者 |
| Evacuation route | طريق الإخلاء | مسیر تخلیه | 疏散路线 |
| Emergency shelter | مأوى طارئ | پناهگاه اضطراری | 紧急避难所 |
| Food distribution | توزيع الغذاء | توزیع غذا | 食品分发 |

📖 Full glossary: [data/glossary.json](data/glossary.json)

---

## Roadmap

- [x] Multilingual crisis bulletins (AR/FA/DAR/EN/ZH/TR)
- [x] ReliefWeb/OCHA auto-scraping pipeline
- [x] 40-term humanitarian glossary (5 languages)
- [x] Telegram bot with 6-language support
- [ ] Real-time shelter tracker for Lebanon
- [ ] Briar + Meshtastic offline communication layer
- [ ] SMS gateway for partial connectivity zones
- [ ] Pashto and Kurdish language support
- [ ] Browser extension for inline report translation

---

## Featured In

> *Coming soon. Help us get there by starring ⭐*

If you've written about this project, open a PR to add your link here.

---

## Contributing

We welcome translators, developers, humanitarian workers, and anyone who gives a damn.

- 🐛 [Report a bug](.github/ISSUE_TEMPLATE/bug_report.md)
- ✨ [Request a feature](.github/ISSUE_TEMPLATE/feature_request.md)
- 🌐 [Contribute a translation](.github/ISSUE_TEMPLATE/translation_request.md)
- 📖 Read the full guide: [CONTRIBUTING.md](CONTRIBUTING.md) · [بالعربية](CONTRIBUTING.ar.md) · [به فارسی](CONTRIBUTING.fa.md)

All skill levels welcome. If you speak a crisis-affected language and can verify translations, that's more valuable than code.

---

## We Don't Accept Donations

This project will always be free and open. If you want to help financially, please give directly to the people doing life-saving work on the ground:

- 🔴 **ICRC** — [icrc.org/en/donate](https://www.icrc.org/en/donate)
- 🔵 **UNHCR** — [donate.unhcr.org](https://donate.unhcr.org)
- ⚕️ **MSF / Doctors Without Borders** — [msf.org/donate](https://www.msf.org/donate)

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=openclaw-humanitarian/openclaw-humanitarian&type=Date)](https://star-history.com/#openclaw-humanitarian/openclaw-humanitarian&Date)

---

## License

MIT — use it, fork it, build on it. See [LICENSE](LICENSE).

---

## Contact

- 📧 Email: [aid@agentmail.to](mailto:aid@agentmail.to)
- 🤖 Telegram: [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)
- 🐛 Issues: [GitHub Issues](https://github.com/openclaw-humanitarian/openclaw-humanitarian/issues)

---

*Built with urgency. Every star helps this project reach someone who needs it.*
