# Contributing to CrisisBridge

Thank you for considering contributing. This project exists because people showed up. Here's how you can help.

---

## 🌐 Contributing Translations

### Add a new language
1. Fork the repository
2. Create a new bulletin file in `translations/[date]/` following the existing format
3. Use the [glossary](glossary.md) for terminology consistency
4. Submit a pull request with the language clearly labeled

### Review existing translations
- Check bulletins in `translations/` for accuracy
- Compare against the original English source (linked in each file)
- Pay special attention to:
  - Humanitarian terminology (use `glossary.md` as reference)
  - Number formats (Persian ۱۲۳ vs Arabic ١٢٣)
  - Dari vs Farsi distinctions (see `guides/translation-qa.md`)
- Open an issue or PR with corrections

### Priority languages
- 🔴 **Urgent:** Dari, Pashto, Kurdish (Sorani)
- 🟡 **Needed:** Turkish, Urdu
- 🟢 **Welcome:** Any language spoken in affected regions

No minimum commitment. Even reviewing one bulletin helps.

---

## 💻 Contributing Code

### Areas where we need help
- **Telegram Bot** — New features, command handling, multilingual UX
- **Data pipeline** — Scraping/parsing ReliefWeb, OCHA, WFP feeds
- **Shelter tracker** — Our Product 2 (see `research/shelter-tracker-concept.md`)
- **LoRa/mesh research** — Offline communication prototyping
- **Website** — Improvements to the landing page

### Getting started
1. Fork and clone the repository
2. Read `README.md` for project overview
3. Check open issues labeled `good-first-issue`
4. For larger changes, open an issue first to discuss

### Code style
- Keep it simple and readable
- Comment anything non-obvious
- Test before submitting

---

## 🏥 Contributing Humanitarian Expertise

We need people who understand the humanitarian system:

- **Content review** — Are our bulletins accurate? Are we using terms correctly?
- **Source validation** — Are we citing the right reports? Missing any key sources?
- **Cultural sensitivity** — Does the tone work for the target audience?
- **Field connections** — Can you connect us with organizations on the ground?

If you have field experience in Lebanon, Iran, Afghanistan, or Syria, your input is especially valuable. You don't need to write code.

---

## Issue Labels

| Label | Description |
|-------|-------------|
| `good-first-issue` | Good for newcomers, limited scope |
| `translation` | Translation work needed |
| `translation-review` | Existing translation needs review |
| `research` | Research task (data gathering, analysis) |
| `urgent` | Time-sensitive, related to active crisis |
| `shelter-tracker` | Product 2 development |
| `lora-mesh` | Offline communication research |
| `bug` | Something isn't working |
| `enhancement` | New feature or improvement |

---

## Code of Conduct

### Core principles

**1. Neutrality**
This project provides humanitarian information. We do not take sides in any conflict. All content must be factual, sourced, and neutral.

**2. No political discussion**
Issues, PRs, and discussions are for project work only. Political opinions, blame attribution, and conflict commentary do not belong here. This is not a debate forum — it's an aid tool.

**3. Respect**
Treat all contributors with respect regardless of background, nationality, language, or skill level. Many contributors may be personally affected by the crises we cover.

**4. Accuracy over speed**
When in doubt, verify. Wrong information in a crisis can be dangerous. If you're unsure about a translation or data point, flag it rather than guessing.

**5. Privacy**
Never share personal information about affected populations. Do not include identifying details in issues or PRs. See our data privacy guidelines.

### Enforcement
Violations of this code of conduct will result in comment removal and, for repeat offenses, contributor ban. The maintainers' decision is final.

---

## 🔒 Security Threat Model

CrisisBridge operates in adversarial environments where state actors actively monitor, disrupt, and exploit communication tools. Contributors should understand these threats.

### Identified Threats

**T1 — Bot Infiltration via Privileged Network Access**
Governments may use unfiltered network connections (e.g. Iran's "white SIM cards") to interact with the Telegram bot, scrape user patterns, or inject disinformation. Mitigation: canary token system (`src/security/canary.py`), rate-based anomaly detection, honeypot commands.

**T2 — SMS Spoofing & Intimidation Confusion**
In Iran, government agencies send mass SMS warnings against using foreign services. Unverified SMS from CrisisBridge could be mistaken for — or used as cover for — state intimidation. Mitigation: HMAC-SHA256 message signing (`src/sms/gateway.py`), Iran region delivery paused until secure verification is established.

**T3 — GPS Jamming Affecting Geolocation**
Large-scale GPS signal interference (documented in Iran) degrades satellite connectivity and renders GPS-dependent features unreliable. Mitigation: GPS-free routing using Cell Tower ID and manual governorate selection (`src/geo/routing.py`).

**T4 — User Deanonymization**
State actors may attempt to correlate Telegram user IDs with geographic locations to identify and target users. Mitigation: no PII storage, no geolocation collection, hashed user IDs only in analytics, governorate-level granularity (never precise coordinates).

**T5 — Content Poisoning**
Compromised or state-affiliated sources may inject misleading information into the bulletin pipeline. Mitigation: trust scoring engine (`src/verification/trust_scorer.py`) with T1–T4 source classification, state media explicitly labelled rather than blocked.

### Security Review for PRs

All pull requests that touch `src/security/`, `src/sms/`, `src/bot/`, or `src/geo/` must include a brief threat assessment: which threats from the list above does the change interact with, and how are they addressed?

### Responsible Disclosure

If you discover a vulnerability that could endanger users in conflict zones, **do not open a public issue**. Email aid@agentmail.to with subject line `[SECURITY]` and we will respond within 48 hours.

---

## Questions?

- 📧 Email: aid@agentmail.to
- 🤖 Telegram: [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)
- Open an issue with the `question` label

---

*Every contribution matters. A reviewed translation might help a family find shelter tonight.*
