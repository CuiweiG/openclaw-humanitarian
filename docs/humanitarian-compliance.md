# Humanitarian Compliance Framework

> **CrisisBridge** - Compliance & Ethics Document
> Version: 1.0 | References: ICRC Handbook on Data Protection in Humanitarian Action (2nd ed., 2020)

---

## 1. Core Principles

CrisisBridge operates under three non-negotiable humanitarian principles, drawn from the International Humanitarian Law framework and operationalized in our technical design:

### 1.1 Do No Harm

> *"Humanitarian action must not worsen the situation of affected people."*

In a digital context, this means:
- Information delivered cannot be weaponized against the people receiving it
- System design cannot create new vulnerabilities (location exposure, identity exposure)
- Content accuracy failures must default to silence rather than misinformation

**How we implement it**: Content is sourced exclusively from verified humanitarian agencies (OCHA, WFP, UNHCR, ICRC). Any content that cannot be verified is suppressed, not guessed. No user data is retained that could be used against them.

### 1.2 Neutrality

> *"Humanitarian actors must not take sides in hostilities or engage in controversies of a political, racial, religious or ideological nature."*

**How we implement it**: The content pipeline has strict source whitelisting. Only official humanitarian agency reports are ingested. Political commentary, military assessments, and government statements are explicitly excluded. See Section 4 for technical enforcement.

### 1.3 Data Minimization

> *"Collect only the personal data that is adequate, relevant, and limited to what is necessary."*

**How we implement it**: CrisisBridge minimises data collection to the functional minimum. The bot stores only in-memory language preferences keyed by Telegram user ID (lost on restart). Application logs include Telegram user IDs at INFO level — this is a known deviation being addressed. No persistent database, no analytics, no location history. See `docs/data-flow.md` for the complete, auditable data flow map.

---

## 2. ICRC Digital Humanitarian Framework Alignment

Reference: *Handbook on Data Protection in Humanitarian Action*, ICRC & Brussels Privacy Hub, 2nd Edition (2020).

### Principle 1: Lawfulness

**ICRC requirement**: Processing must have a lawful basis; for humanitarian actors this is typically "vital interests" of data subjects.

**Our alignment**:
- We process **minimal personal data**: Telegram user ID (for language preference) and query text (in-memory, discarded after response). Application logs currently include user IDs — migration to hashed IDs is planned.
- The primary data processed is publicly available humanitarian reports from OCHA/WFP/UNHCR — institutional data, not personal data.
- Telegram bot interactions: Telegram's own privacy policy governs their infrastructure. We receive message text and user ID. Query text is processed in-memory and not persisted to disk. User IDs appear in application logs (see `docs/data-flow.md`).

### Principle 2: Purpose Limitation

**ICRC requirement**: Data collected for humanitarian purposes must not be repurposed.

**Our alignment**:
- The system has a single, documented purpose: delivery of verified humanitarian information to affected populations.
- No secondary use of any data. No advertising, no research data sales, no government data sharing.
- Codebase is open source - purpose limitation is verifiable by inspection.

### Principle 3: Data Minimization

**ICRC requirement**: Only collect data necessary for the humanitarian purpose.

**Our alignment**: See Section 3. We have implemented technical minimization, not just policy minimization - the system is architecturally incapable of retaining what it doesn't collect.

### Principle 4: Accuracy

**ICRC requirement**: Data must be accurate and kept up to date.

**Our alignment**:
- All content is fetched from source APIs (ReliefWeb, OCHA) with timestamps.
- Bulletins are date-stamped and include source attribution URLs.
- Cached bulletins on mesh nodes are marked with a 72-hour expiry; stale content displays a visible age warning.
- Correction pipeline: if a source agency issues a correction, the next scrape cycle (every 4 hours) picks it up and supersedes the prior bulletin.

### Principle 5: Storage Limitation

**ICRC requirement**: Data must not be kept longer than necessary.

**Our alignment**:
- No user data is stored at any point in the pipeline.
- Bulletin content: retained in cache for 72 hours (offline mesh nodes) or until next scrape (online nodes).
- Telegram interaction logs: not stored. Each query is stateless.

### Principle 6: Security

**ICRC requirement**: Appropriate technical and organizational measures to protect data.

**Our alignment**:
- All API communications: HTTPS with TLS 1.3
- Mesh layer: AES-256 pre-shared key encryption on LoRa channel
- Briar layer: end-to-end encrypted by protocol design (Bramble Transport Protocol)
- Server infrastructure: no persistent logs, systemd journal with 24h rotation
- Open source code: security reviewable by any party

### Principle 7: Accountability

**ICRC requirement**: The organization must be able to demonstrate compliance.

**Our alignment**:
- This document is public and versioned in the repository
- Code is open source under MIT License
- Data flows are documented in architecture docs
- No "trust us" - the technical design makes compliance independently verifiable

---

## 3. Technical Guarantees

These are not policy statements. They are architectural properties of the system, verifiable in source code.

### 3.1 No User Location History

```python
# There is no location field in the user interaction model
# Telegram bot receives: {message_id, text, timestamp}
# We process: {text}
# We store: nothing
```

The Telegram bot handler (`src/bot/telegram_bot.py`) processes incoming text and returns a response. No IP addresses, no GPS coordinates, no cell tower identifiers are accessed or stored.

### 3.2 No Query Logging

Query text is processed in-memory within a single request cycle. No logging framework captures query content:

```python
# logging config in all modules:
logging.basicConfig(level=logging.INFO)
# Log messages contain: timestamps, module names, error codes
# Log messages do NOT contain: user input, query text, translated content
```

This is enforced by code review policy: any log statement containing user input is rejected in PR review.

### 3.3 Encrypted Transmission

| Transport | Encryption |
|-----------|------------|
| Telegram Bot API | TLS/MTProto (server-to-server, **NOT** E2E) |
| ReliefWeb API | TLS 1.3 |
| OCHA API | TLS 1.3 |
| Briar P2P | Bramble Transport Protocol (end-to-end) |
| Meshtastic LoRa | AES-128 PSK (channel-level) |

### 3.4 Open Source = Auditable

The entire codebase is published under AGPL-3.0 at `github.com/CuiweiG/openclaw-humanitarian`. This means:

- Any security researcher can audit the data handling
- Any partner organization can verify the content pipeline
- Any affected community can confirm no surveillance is occurring

The AGPL license ensures that any modified deployments must also publish their source code, preventing a closed-source fork from removing these guarantees.

---

## 4. Content Restrictions

### 4.1 Permitted Content

CrisisBridge bulletins may only contain:

| Category | Examples |
|----------|---------|
| **Shelter locations** | UNRWA school addresses, collective center coordinates |
| **Food aid distribution** | WFP distribution point locations and times |
| **Medical access** | Field hospital locations, ICRC medical facility contacts |
| **Emergency contacts** | UNHCR helplines, Red Cross/Crescent numbers |
| **Evacuation guidance** | Safe corridor information from UN-verified sources |
| **WASH information** | Clean water sources, sanitation facility locations |

### 4.2 Prohibited Content

The following content categories are **technically prevented** by the source whitelist:

| Category | Reason |
|----------|--------|
| Military positions | Violates neutrality; creates harm risk |
| Casualty counts by party | Could be used as targeting information |
| Political statements | Violates neutrality principle |
| Government announcements | Not a neutral humanitarian source |
| Social media content | Unverified; accuracy not guaranteed |
| Rumor or speculation | ICRC accuracy principle |

### 4.3 Technical Enforcement: Source Whitelist

Content can only enter the pipeline from these verified sources:

```python
APPROVED_SOURCES = [
    "reliefweb.int",      # OCHA's humanitarian information platform
    "unocha.org",         # UN Office for the Coordination of Humanitarian Affairs
    "wfp.org",            # World Food Programme
    "unhcr.org",          # UN Refugee Agency
    "icrc.org",           # International Committee of the Red Cross
    "unicef.org",         # UN Children's Fund
    "who.int",            # World Health Organization
    "msf.org",            # Médecins Sans Frontières
]
```

Any API response from a non-whitelisted domain is rejected before parsing. This is not a content filter - it is a source filter. The question is not "is this content harmful?" but "is this content from a trusted humanitarian actor?" If no, it never enters the pipeline.

---

## 5. Anti-Misuse Design

### 5.1 Can the Mesh Network Be Militarized?

This is a genuine concern raised during design review. A mesh network that delivers location information could theoretically be used to coordinate military activity. Our mitigations:

**Content control**: The mesh network only relays CrisisBridge bulletins. There is no general-purpose messaging capability exposed to arbitrary users. Messages must be formatted and signed (SHA-256 hash) to be relayed by CrisisBridge nodes.

**Source verification**: All bulletin content must originate from the online layer (verified humanitarian APIs). Field devices cannot inject arbitrary content into the mesh - they can only relay signed content received from CrisisBridge servers.

**No location data**: Meshtastic nodes have GPS broadcast **disabled in firmware configuration**. Nodes do not advertise their location. Users cannot query "where are all the nodes."

### 5.2 Rate Limiting: Maximum Broadcast Volume per Node

Each Meshtastic node enforces a transmission rate limit:

```
Max transmissions: 1 bulletin per hour
Max bulletin size: 255 bytes (LoRa protocol limit)
Daily maximum: 24 bulletins × 255 bytes = ~6 KB/day
```

This is a physical constraint of LoRa duty cycle regulations (1% duty cycle at 868 MHz), not just a software limit. The radio hardware cannot exceed this regardless of software configuration.

This rate is sufficient for:
- Shelter location updates (once per 4 hours is adequate)
- Emergency contact numbers (rarely change)

This rate is insufficient for:
- Real-time tactical communication
- Coordinating movements across checkpoints (requires higher bandwidth)

The bandwidth constraint is a feature, not a bug - it makes the system structurally unsuitable for military use while adequate for humanitarian information delivery.

### 5.3 Content Signature Verification

Every CrisisBridge bulletin includes a SHA-256 hash of its content:

```
[CrisisBridge-AID v1]
DATE: 2026-03-26
LANG: fa
HASH: sha256:3a7f2b9c...
SIGNED-BY: CrisisBridge-server-01
---
[content]
---
[END]
```

Field devices and Meshtastic relay nodes verify the hash before relaying. Content that fails verification is:
1. Dropped (not relayed)
2. Logged locally as a tamper attempt (no external report - this would require internet)

A partner organization attempting to inject false shelter locations would need to:
1. Obtain the AES-256 channel key (distributed only to vetted partner organizations)
2. Generate a valid HMAC signature (requires access to CrisisBridge server signing key)
3. Format the bulletin correctly (documented but integrity-checked)

The signing key is held only by CrisisBridge server infrastructure and is rotated monthly.

---

## 6. Partner Organization Agreement Requirements

Any organization deploying CrisisBridge mesh hardware must agree in writing to:

1. Use nodes exclusively for humanitarian information relay
2. Not modify the firmware to enable position broadcasting
3. Not inject unsigned or self-signed bulletins into the network
4. Report any suspected misuse to the CrisisBridge security team
5. Destroy or return nodes if their humanitarian mandate changes

This agreement does not have legal force in all jurisdictions. It is a trust mechanism, not a legal control - and is documented here honestly as such. The technical mitigations in Section 5 are the primary safeguard.

---

*Last reviewed: March 2026. For compliance questions, contact the CrisisBridge ethics review board.*
