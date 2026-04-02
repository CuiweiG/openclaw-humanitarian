# Glossary Review Workflow

> CrisisBridge — Language Quality Assurance Process
> Version: 1.0 | Date: 2026-04-03

---

## Purpose

CrisisBridge delivers humanitarian information in 12 languages. Machine-generated
translations of humanitarian terminology can contain errors that matter in
life-or-death contexts. This workflow ensures native speakers validate every
glossary term before it is treated as verified.

---

## Current Verification Status

| Language | Code | Terms | Verified | Reviewer | Status |
|----------|------|-------|----------|----------|--------|
| Arabic (MSA) | ar | 40 | 40 | ✅ Complete | Production |
| Chinese | zh | 40 | 40 | ✅ Complete | Production |
| French | fr | 40 | 40 | ✅ Complete | Production |
| Spanish | es | 40 | 40 | ✅ Complete | Production |
| Russian | ru | 40 | 40 | ✅ Complete | Production |
| Persian | fa | 40 | **0** | ❌ Needed | **Unverified** |
| Dari | dar | 40 | **0** | ❌ Needed | **Unverified** |
| Turkish | tr | 40 | **0** | ❌ Needed | **Unverified** |
| Pashto | ps | 40 | **0** | ❌ Needed | **Unverified** |
| Kurdish (Kurmanji) | ku | 40 | **0** | ❌ Needed | **Unverified** |
| Lebanese Arabic | apc | 40 | **0** | ❌ Needed | **Unverified** |

**Critical gap:** The 5 most important target languages (fa, dar, ps, ku, apc)
have zero verified terms.

---

## Reviewer Requirements

### Minimum Qualifications

1. **Native or near-native** fluency in the target language
2. **Reading knowledge** of English humanitarian terminology
3. **Familiarity** with the humanitarian context (displacement, aid distribution,
   medical terminology) — field experience preferred but not required
4. **No conflict of interest** — not affiliated with any party to the conflict

### Ideal Profile

- Humanitarian translator, interpreter, or information management officer
- Experience with OCHA/UNHCR/WFP terminology
- Member of CLEAR Global / Translators Without Borders community

---

## Review Process

### Step 1: Claim a Language

1. Open a GitHub issue using the `translation-review` label
2. Title: `[Glossary Review] {Language Name} ({code})`
3. Body: Confirm your language qualifications
4. A maintainer will assign you and provide the review spreadsheet

### Step 2: Review Terms

For each of the 40 glossary terms in `data/glossary.json`:

| Field | Action |
|-------|--------|
| English term | Read and understand the humanitarian context |
| Current translation | Evaluate: is this term correct, natural, and unambiguous? |
| Verdict | ✅ Correct / ⚠️ Needs correction / ❌ Wrong |
| Correction | If needed, provide the correct term |
| Notes | Context, regional variation, or alternative terms |

### Review Criteria

Each term must satisfy ALL of the following:

1. **Accuracy** — Does it convey the same meaning as the English term?
2. **Naturalness** — Would a native speaker use this term in conversation?
3. **Unambiguity** — Could it be confused with a different concept?
4. **Cultural appropriateness** — Is it safe and respectful in the target culture?
5. **Dialect fit** — Is it appropriate for the specific dialect (e.g., Levantine
   vs. MSA for Arabic)?

### Step 3: Submit Review

1. Fork the repository
2. Edit `data/glossary.json`:
   - Update any corrected terms
   - Set `"verified": { "{lang}": true }` for each reviewed term
3. Submit a PR with title: `[Glossary] Verify {Language} — {N} terms reviewed`
4. Include your reviewer qualifications in the PR description

### Step 4: Merge

- A second reviewer (if available) or maintainer reviews the corrections
- PR is merged and the term is marked as verified
- README verification status updates automatically

---

## Error Correction After Verification

If a verified term is later found to be incorrect:

1. Open an issue with `translation-error` label
2. Explain the error and provide the correction
3. Tag the original reviewer if possible
4. Fast-track merge — translation errors in humanitarian context are P0

---

## Outreach Channels

We actively seek reviewers through:

- CLEAR Global / Translators Without Borders volunteer network
- University Middle Eastern / Central Asian studies departments
- Diaspora community organizations
- OCHA/UNHCR information management staff
- GitHub issue with `help-wanted` + `translation` labels

---

## Quality Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Languages with ≥90% verified terms | 12/12 | 5/12 |
| Average time from claim to completion | ≤2 weeks | N/A |
| Terms corrected post-verification | <5% | N/A |

---

*This workflow is referenced in CONTRIBUTING.md and the Technical Readiness
Matrix. Native speaker verification of life-safety terminology is a
prerequisite for Phase 2 partner engagement.*
