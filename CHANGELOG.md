# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] — "Human First" (2026-03-27)

### Added
- **Family Links** — Tracing system with fuzzy name matching, GDPR-compliant privacy, auto-expiry
- **MHPSS Module** — Crisis helplines (IR/LB/AF/SY), guided breathing (9 languages), 5-4-3-2-1 grounding (9 languages), urgency-based referral engine
- **UXO Safety** — Mine/UXO safety rules in 9 languages, demining organization contacts
- **Document Protection** — Backup guide (EN/FA/AR), embassy/UNHCR contacts
- **Emergency Contacts** — Verified emergency numbers for Iran, Lebanon, Afghanistan, Syria
- **Accessibility** — Simplified language generator, emoji markers for low-literacy, audio bulletin generation (pluggable TTS)
- **15 new Bot commands** — /findFamily, /searchFamily, /mentalhealth, /breathe, /helpline, /safety, /documents, /embassy, /emergency, /audio, /simple, and more
- **4 new test files** — test_family_links.py, test_mhpss.py, test_safety.py, test_accessibility.py

## [0.1.0] — "First Light" (2026-03-27)

### Added
- 🌐 Multilingual crisis bulletin pipeline (Arabic, Persian, Dari, English, Chinese, Turkish)
- 📡 ReliefWeb/OCHA automated report scraper
- 🤖 Telegram bot with /start, /latest, /shelter, /language, /help commands
- 📖 40-term humanitarian glossary in 8 languages (EN/FA/DAR/AR/ZH/FR/ES/RU)
- 📻 Briar + Meshtastic offline architecture design documents
- 🌍 Multi-language README (English, Persian, Arabic, Chinese)
- 🌍 Multi-language CONTRIBUTING guide (English, Persian, Arabic)
- 🧪 Complete test suite (pytest)
- 🔧 GitHub Actions CI pipeline
- 📋 Translation quality checking system
- 🏥 ICRC-aligned humanitarian compliance framework
- ⚡ Demo script — works without API key, 30-second experience

### Technical
- Pluggable translation backend (Claude API / local model / stub)
- ReliefWeb API v2 integration with retry logic
- 9-language i18n system (JSON locale files)
- Glossary-enforced terminology consistency
- Persian vs Dari automatic distinction handling

[0.1.0]: https://github.com/CuiweiG/openclaw-humanitarian/releases/tag/v0.1.0
