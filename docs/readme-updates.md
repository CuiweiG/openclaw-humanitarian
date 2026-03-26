# README Updates

This file contains text fragments to be merged into `README.md`.

---

## New Top Description (replace existing tagline/description)

```
An open-source platform ensuring life-saving humanitarian information reaches every civilian, in their language, online or offline. Currently serving the 2026 Middle East crisis in 9 languages.
```

---

## New Roadmap (replace existing roadmap section)

```markdown
- [x] Multilingual crisis bulletins (AR/FA/DAR/EN/ZH/TR/FR/ES/RU)
- [x] ReliefWeb/OCHA automated scraping pipeline
- [x] 40-term humanitarian glossary (8 languages, verification status tracked)
- [x] Telegram bot with 9-language i18n support
- [x] Docker deployment support
- [x] Comprehensive test suite with CI/CD
- [ ] Real-time shelter capacity tracker for Lebanon
- [ ] Briar + Meshtastic offline communication layer
- [ ] Community translation verification system
- [ ] SMS gateway for partial connectivity zones
- [ ] Pashto and Kurdish language support
- [ ] Integration with OCHA HDX API
- [ ] Browser extension for inline report translation
```

---

## New "Transparency & Limitations" Section (add after Features / before Contributing)

```markdown
## Transparency & Limitations

- **AI translations have limitations.** Our bulletins are AI-generated from official UN sources. While we enforce terminology consistency via our glossary, translations may contain errors. We're building a community verification system.
- **Glossary verification status:** Each term in our glossary is marked as `verified` (confirmed by UN official terminology or native speakers) or `unverified` (AI-generated, pending review). [See glossary →](data/glossary.json)
- **We are not a replacement for official sources.** Always refer to OCHA, WFP, UNHCR, and ICRC directly for critical decisions.
- **Persian vs Dari:** We maintain separate translations for Iranian Persian and Afghan Dari, recognizing vocabulary and usage differences. [See our approach →](docs/translation-pipeline.md)
```

---

## Use Cases Section (add after Transparency / before Roadmap)

See [`docs/use-cases.md`](use-cases.md) — paste full contents inline, or include via reference:

```markdown
## Real-World Use Cases

<!-- paste contents of docs/use-cases.md here -->
```
