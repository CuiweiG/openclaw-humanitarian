# Accountability to Affected Populations (AAP) — Feedback & Complaints

> CrisisBridge — Community Engagement Framework
> Version: 1.0 | Date: 2026-04-03
> References: CHS Core Humanitarian Standard (2024), UNHCR AAP Framework

---

## Principles

CrisisBridge is accountable to the communities it serves. This means:

1. **Participation** — Affected people should influence what information
   we provide and how we provide it
2. **Transparency** — We are open about what we can and cannot do
3. **Feedback** — People can tell us when something is wrong
4. **Correction** — We act on feedback and fix errors
5. **Complaints** — People can raise concerns without fear of retaliation

---

## Feedback Channels

### Current (Active)

| Channel | How to Use | Response Time |
|---------|-----------|---------------|
| GitHub Issues | Open issue with `feedback` label | 48 hours |
| Email | aid@agentmail.to with subject `[FEEDBACK]` | 48 hours |
| Telegram Bot | `/feedback` command (planned) | Automated ack |

### Planned

| Channel | Target | Status |
|---------|--------|--------|
| Telegram `/feedback` command | Direct user input in-bot | Not yet implemented |
| SMS feedback number | For partial-connectivity users | Requires SMS gateway |
| Voice hotline (partner-operated) | For low-literacy users | Requires field partner |
| Community focal point network | For offline/mesh users | Requires field partner |

---

## What Feedback We Accept

| Category | Examples | Priority |
|----------|---------|----------|
| **Translation errors** | Wrong term, misleading wording, cultural insensitivity | P0 — fast track |
| **Incorrect information** | Wrong shelter address, outdated phone number | P0 — fast track |
| **Missing coverage** | "My region is not covered", "My language is missing" | P1 |
| **Usability issues** | "I can't understand the bot commands" | P1 |
| **Feature requests** | "I need information about X" | P2 |
| **Complaints** | "The system gave me wrong information and I went to the wrong place" | **S1 — incident** |

---

## Complaint Handling

### What Constitutes a Complaint

A complaint is any expression of dissatisfaction about CrisisBridge
that alleges harm, failure to meet expectations, or request for
corrective action. Complaints are distinct from feedback (which is
voluntary improvement input).

### Process

1. **Receive** — Log complaint with timestamp, channel, and category.
   Do NOT log personal identity unless the complainant provides it
   voluntarily for follow-up.

2. **Acknowledge** — Within 24 hours:
   - "Thank you for letting us know. We take this seriously."
   - Provide expected response timeline

3. **Investigate** — Within 72 hours:
   - Verify the claim against system records
   - If content error: trigger correction/retraction process
   - If system error: file bug and prioritize fix

4. **Respond** — Within 1 week:
   - Explain what happened
   - Describe what was done to fix it
   - Describe what will prevent recurrence

5. **Close** — Log resolution. If complainant is reachable, confirm
   they are satisfied.

### Escalation

If a complaint alleges serious harm (physical danger, data exposure):
- Escalate immediately to S1/S2 incident (see `docs/incident-response.md`)
- Notify partner organizations
- Do not wait for investigation to complete before containment

---

## Community Participation

### Current Mechanisms

- **GitHub Discussions** — Open to anyone
- **Translation review** — Native speakers verify glossary terms
  (see `docs/glossary-review-workflow.md`)
- **Issue templates** — Structured input for bugs, features, translations

### Planned Mechanisms

- **Affected population consultation** — Before deploying in new regions,
  consult with community representatives about:
  - Information needs and priorities
  - Preferred languages and dialects
  - Trusted communication channels
  - Concerns about digital safety

- **Content co-design** — Work with local organizations to determine
  what information format works best (text, audio, visual, simplified)

---

## Monitoring

| Metric | Target | Measured |
|--------|--------|---------|
| Feedback response time | < 48 hours | Not yet tracked |
| Complaint resolution time | < 1 week | Not yet tracked |
| Translation corrections per month | Track trend | Not yet tracked |
| User satisfaction (when measurable) | Improve over time | Not yet tracked |

---

*This document is referenced in the Technical Readiness Matrix. AAP is a
core humanitarian standard, not an optional feature.*
