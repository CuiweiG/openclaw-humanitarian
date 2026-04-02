# Incident Response Plan

> CrisisBridge — Security & Operational Incident Handling
> Version: 1.0 | Date: 2026-04-03

---

## Scope

This plan covers all incidents that could harm CrisisBridge users,
partner organizations, or affected populations. It applies to all
deployment environments (production, staging, partner-hosted).

---

## Incident Categories

| Category | Severity | Example | Response Time |
|----------|----------|---------|---------------|
| **S1 — Critical** | Life safety risk | False airstrike alert broadcast; family links data breach | **Immediate** (< 15 min) |
| **S2 — High** | Data exposure or system compromise | Bot credentials leaked; unauthorized access to partner data | **< 1 hour** |
| **S3 — Medium** | Service disruption or content error | Translation error in safety-critical term; scraper returning stale data | **< 4 hours** |
| **S4 — Low** | Minor issue, no harm | Formatting bug; non-critical dependency CVE | **< 24 hours** |

---

## Response Procedures

### Phase 1: Detection & Triage (0–15 minutes)

1. **Detect** — Incident identified by:
   - Automated monitoring (canary alerts, error rates)
   - Partner report
   - User report
   - Maintainer observation

2. **Triage** — Assign severity (S1–S4) based on:
   - Is anyone in physical danger? → S1
   - Is personal data exposed? → S2
   - Is content incorrect in a safety-critical way? → S3
   - Everything else → S4

3. **Notify** — Alert the response chain:
   - S1/S2: All maintainers + affected partners immediately
   - S3/S4: Primary maintainer within response time

### Phase 2: Containment (15 min – 1 hour)

**For S1 — False Alert:**
1. Invoke kill switch: `kill_alerts()` or set `ALERT_KILL_SWITCH=1`
2. Broadcast retraction message through all channels
3. Notify all partner organizations
4. Document timeline

**For S2 — Data Breach:**
1. Revoke compromised credentials (bot token, API keys)
2. Assess what data was exposed and to whom
3. Notify affected partners
4. If family links data: notify affected individuals and ICRC RFL

**For S3 — Content Error:**
1. Identify the incorrect content
2. Issue corrected bulletin (supersedes original)
3. Notify partners who may have relayed the error

**For S1/S2 — General:**
1. Disable affected module/service
2. Preserve evidence (logs, state)
3. Do NOT attempt to "fix" in production — contain first

### Phase 3: Investigation (1 hour – 48 hours)

1. **Root cause analysis** — What happened and why?
2. **Impact assessment** — Who was affected and how?
3. **Evidence collection** — Logs, screenshots, timeline
4. **External notification** — If required by partner agreements or regulations

### Phase 4: Recovery (48 hours – 1 week)

1. **Fix** — Implement and test the fix in staging
2. **Verify** — Confirm the fix addresses the root cause
3. **Deploy** — Roll out to production with monitoring
4. **Communicate** — Notify partners and users of resolution

### Phase 5: Post-Incident Review (1–2 weeks)

1. **Incident report** — Written document covering:
   - Timeline of events
   - Root cause
   - Impact (who, what, how severe)
   - Response effectiveness
   - Lessons learned
   - Preventive measures

2. **Process update** — Update this plan if gaps were identified

3. **Affected party debrief** — Share relevant findings with partners

---

## Bulletin Retraction & Correction

### When to Retract

A bulletin must be retracted if it contains:
- Incorrect shelter locations (could endanger people)
- Wrong emergency contact numbers
- Outdated evacuation routes
- Any information that could cause harm if acted upon

### Retraction Process

1. Generate a **supersedence bulletin** with:
   - Same region and language targeting
   - `[CORRECTION]` prefix in title
   - Clear statement of what was wrong
   - Corrected information
   - Higher priority flag to ensure propagation

2. Push through ALL channels (Telegram, mesh, SMS)

3. For mesh networks: supersedence bulletins carry a
   `supersedes_hash` field that tells relay nodes to
   discard the original

4. Log the retraction in the delivery log

### Correction Template

```
[CORRECTION] CrisisBridge — {date}
⚠️ A previous bulletin contained incorrect information.

WRONG: {incorrect information}
CORRECT: {corrected information}

We apologize for the error. Source: {source_url}
```

---

## Contact Chain

| Role | Contact | Availability |
|------|---------|-------------|
| Primary maintainer | aid@agentmail.to | Best effort |
| Security reports | aid@agentmail.to (subject: [SECURITY]) | 48h response |
| Partner escalation | Via signed partner agreement channel | Per agreement |

---

## Review Schedule

This plan must be reviewed:
- Every 3 months
- After every S1 or S2 incident
- When new red-tier modules are activated
- When new partner organizations are onboarded

---

*This plan is referenced in partner-sop.md and SECURITY.md.*
