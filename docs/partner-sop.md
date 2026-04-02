# Partner Standard Operating Procedure — Red-Tier Module Activation

> CrisisBridge — Operational Governance Document
> Version: 1.0 | Date: 2026-04-03
> Classification: Partner-facing

---

## Purpose

CrisisBridge classifies modules into three risk tiers (see `SECURITY.md`).
**Red-tier modules** handle sensitive data or produce safety-critical outputs
that could cause harm if misused, misconfigured, or deployed without adequate
safeguards.

This SOP defines the **mandatory prerequisites** for activating any red-tier
module. No red-tier module may be enabled in any deployment — including
development and staging — without completing the applicable checklist.

---

## Red-Tier Modules

| Module | Risk Category | Primary Concern |
|--------|--------------|-----------------|
| Airstrike Alert System | Life safety | False/stale alerts cause harm; precision data weaponizable |
| Family Links | Data protection | PII of vulnerable individuals; RFL standards |
| MHPSS Referral | Clinical safety | Risk of inappropriate triage without qualified oversight |

---

## General Prerequisites (All Red-Tier Modules)

Before activating **any** red-tier module, the deploying partner must:

- [ ] **1. Identify a Responsible Officer** — Named individual accountable for
      the module's operation, with authority to invoke the kill switch.
- [ ] **2. Complete a Data Protection Impact Assessment (DPIA)** — Using the
      template in `docs/dpia-template.md`. The DPIA must be reviewed by the
      partner's data protection officer or equivalent.
- [ ] **3. Sign a Partner Agreement** — Covering permitted use, data handling,
      incident reporting obligations, and decommissioning procedures.
- [ ] **4. Establish an Incident Response Plan** — Covering data breach,
      false alert, system compromise, and partner withdrawal scenarios
      (see `docs/incident-response.md`).
- [ ] **5. Document a Kill Switch Procedure** — The Responsible Officer must
      be able to disable the module within 5 minutes via any of the three
      kill switch mechanisms (env var, file, runtime call).
- [ ] **6. Confirm Human Review Chain** — No red-tier output reaches end users
      without at least one human reviewer in the loop.

---

## Module-Specific Checklists

### Airstrike Alert System

In addition to the general prerequisites:

- [ ] **Multi-source verification** — Minimum 2 independent data sources must
      confirm an event before alert broadcast. Single-source alerts are
      suppressed with a log entry.
- [ ] **Geographic confidence interval** — Alerts specify governorate-level
      regions only. No precise coordinates, street addresses, or grid
      references in alert content.
- [ ] **TTL expiry** — Every alert has a `ttl_minutes` field (default: 60).
      Expired alerts are automatically retracted and must not be relayed
      by mesh nodes.
- [ ] **Correction/supersedence** — A mechanism exists to broadcast a
      correction that overrides a prior alert. Corrections propagate
      through the same channels as the original alert.
- [ ] **Kill switch tested** — The kill switch has been tested in the
      deployment environment within the last 7 days.
- [ ] **Escalation path** — A documented escalation path exists from
      automated alert → human reviewer → broadcast approval → distribution.
- [ ] **False positive protocol** — Documented procedure for handling a
      false alert that has already been broadcast, including retraction
      message template.

### Family Links

In addition to the general prerequisites:

- [ ] **ICRC coordination** — The deploying partner has notified or
      coordinated with ICRC Restoring Family Links (RFL) focal point
      for the relevant country.
- [ ] **Encryption at rest** — All family links data (names, locations,
      contact methods) is encrypted at rest using AES-256 or equivalent.
      The current in-memory dict implementation is NOT acceptable for
      production.
- [ ] **Access control** — Only authorized case workers can access family
      links records. Access is logged and auditable.
- [ ] **Retention policy** — Maximum 30-day retention for unmatched
      records. Matched records purged within 7 days of confirmation.
- [ ] **Consent mechanism** — Documented informed consent process for
      individuals submitting their data. Consent must be revocable.
- [ ] **Data breach protocol** — Specific plan for family links data
      breach, including notification of affected individuals and ICRC.

### MHPSS Referral

In addition to the general prerequisites:

- [ ] **Clinical partner identified** — A qualified mental health
      organization (e.g., WHO-trained provider, MSF mental health
      program, local MHPSS working group member) oversees referral
      pathways.
- [ ] **No self-triage** — The module MUST NOT present itself as a
      diagnostic or triage tool. Permitted outputs: self-help content,
      publicly available helpline numbers, referral to qualified services.
- [ ] **Do-no-harm review** — A qualified MHPSS professional has
      reviewed all self-help content for appropriateness in the target
      cultural context.
- [ ] **Escalation for acute risk** — If user input suggests acute
      suicide risk or self-harm, the system must immediately display
      emergency contact numbers and must NOT attempt automated
      assessment or counselling.

---

## Activation Process

1. Partner completes all applicable checklists above
2. Partner submits completed checklists to CrisisBridge maintainers
3. Maintainers review and confirm readiness
4. Module is enabled in the partner's deployment configuration
5. 7-day monitoring period with daily status reports
6. Formal go/no-go decision at end of monitoring period

---

## Deactivation

A red-tier module must be immediately deactivated if:

- The Responsible Officer is no longer available and no successor is named
- A data breach or false alert incident occurs (pending investigation)
- The partner organization's mandate or operating conditions change
- The kill switch is invoked for any reason (investigate before re-enabling)
- CrisisBridge maintainers issue a security advisory affecting the module

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-04-03 | Initial release |

---

*This SOP is referenced in the Technical Readiness Matrix and SECURITY.md.
It must be provided to all partner organizations evaluating CrisisBridge
for deployment.*
