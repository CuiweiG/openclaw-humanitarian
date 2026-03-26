# Automated Situation Report Generation — Methodology

## Why Automated SitRep Generation Matters

In humanitarian emergencies, situation reports (SitReps) are the operational backbone of the response. They coordinate hundreds of organizations, inform funding decisions, and shape policy. But they take time — often hours of analyst work — which means information can be 24–48 hours stale by the time it reaches decision-makers.

Automated SitRep generation addresses this gap by:
- **Compressing the information cycle** from hours to minutes
- **Ensuring consistent structure** across all reports (OCHA standard sections)
- **Aggregating across dozens of sources** simultaneously, something no human analyst can do at scale
- **Freeing analysts** to do higher-level synthesis rather than extraction

## Research Foundation

This module is inspired by the methodology in:

> **arXiv:2512.19475** (December 2025)  
> *"A Large-Language-Model Framework for Automated Humanitarian Situation Reporting"*

The paper proposes a multi-stage pipeline:
1. **Document ingestion** — gather reports from ReliefWeb, OCHA, UN agencies
2. **Semantic clustering** — group documents by theme using embeddings
3. **Question generation** — auto-generate standard questions per OCHA section
4. **RAG-based extraction** — retrieve answers from the document corpus using retrieval-augmented generation
5. **Structured synthesis** — compile extracted answers into a standard report format

## Our Implementation

We implement a **simplified version** of this pipeline, optimized for offline-capable deployment:

### What we do:
| Stage | Paper approach | Our approach |
|-------|---------------|--------------|
| Clustering | Sentence embeddings (SBERT) | Keyword-based thematic clustering |
| Question answering | RAG with vector search | Sentence-level keyword overlap scoring |
| Synthesis | LLM summarization | Template-based extraction + ordering |
| Output | JSON + narrative | Structured dict + Markdown renderer |

### Why simplified?
- **No GPU required** — runs on field laptops and Raspberry Pi
- **No API dependency** — works fully offline once documents are loaded
- **Auditable** — every finding traces back to a specific source sentence
- **Fast** — generates a full SitRep in under 1 second on minimal hardware

## Current Limitations

These limitations are known and documented for transparency:

1. **Keyword matching vs. semantic search**  
   Our `_extract_answer()` uses word overlap, not semantic similarity. It can miss paraphrases ("people fleeing" vs. "population displacement") and return false positives for documents that share common words without relevance.

2. **No coreference resolution**  
   If a document says "they" instead of "refugees", the system may not connect it to the displacement section.

3. **Section coverage gaps**  
   Some OCHA sections (WASH, funding, outlook) often have no findings because source documents rarely contain explicit answers to our generated questions. This is a data problem, not a code problem.

4. **Language limitation**  
   The current extraction pipeline is English-only. Arabic and Dari sources must be translated first.

## Planned Upgrades (v0.5.0)

- [ ] **Semantic search** using lightweight embedding models (e.g., `all-MiniLM-L6-v2`)
- [ ] **LLM-assisted synthesis** for the overview section (optional, requires API key)
- [ ] **Multi-language extraction** — run extraction on translated + original simultaneously
- [ ] **Confidence calibration** — better scoring that correlates with human-judged quality

## Verification Framework

Every finding in a generated SitRep goes through our three-layer verification:

```
Finding extracted
     ↓
[1] Source credibility check (SourceChecker)
     — Is the source a verified UN/ICRC/Tier-2 organization?
     ↓
[2] Cross-reference check (CrossReferencer)
     — Do 2+ independent sources confirm this?
     ↓
[3] Disclaimer generation (DisclaimerGenerator)
     — Append appropriate caveat based on verification result
```

Findings that do not pass Level 2 are clearly marked as single-source or unverified, and are **never published without human review**.

## OCHA Standard Sections

All generated reports follow the OCHA standard SitRep structure:

| Section | Key Questions |
|---------|--------------|
| Overview | General situation summary |
| Displacement | How many displaced? Where? Trend? |
| Casualties | Deaths, injuries, civilian impact |
| Humanitarian Access | Constraints, hard-to-reach areas |
| Food Security | Food insecurity numbers, distribution |
| Health | Facility status, disease outbreaks |
| WASH | Water access, sanitation |
| Shelter | Availability, occupancy |
| Protection | Violations, vulnerable groups |
| Response | What humanitarian actors are doing |
| Funding | Requirements vs. contributions |
| Outlook | Forward-looking assessment |

## References

- arXiv:2512.19475 — Primary methodology reference
- OCHA SitRep Guidelines: https://www.unocha.org/resources/situation-reports
- ReliefWeb API: https://reliefweb.int/help/api
- Kreutzer et al. 2020 — "Improving Humanitarian Needs Assessments through NLP" (IBM/WFP)
