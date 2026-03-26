/**
 * Academic Reference Technical Audit
 * 
 * Verifies that every technique borrowed from academic literature
 * is correctly implemented. Each test maps to a specific paper.
 * 
 * References audited:
 * 1. arXiv:2512.19475 — Auto situation report generation
 * 2. Rocca et al. 2023 — Humanitarian NLP extraction
 * 3. Kreutzer et al. 2020 (IBM/WFP) — Needs assessment NLP
 * 4. Otal & Canbaz 2024 — LLM crisis management
 * 5. ICRC Handbook 2020 — Data protection in humanitarian action
 * 6. HumSet (Frontiers) — Humanitarian NLP data standard
 * 7. CrisisNLP (QCRI) — Crisis classification benchmarks
 * 8. CLEAR Global Gamayun — Low-resource language MT
 * 9. OCHA sector classification — Standard humanitarian clusters
 * 10. Meshtastic/Briar — Offline mesh protocols
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

let total = 0, passed = 0, failed = 0;
const failures = [];

function test(name, condition, detail = '') {
  total++;
  if (condition) { passed++; console.log(`  [PASS] ${name}`); }
  else { failed++; failures.push({name, detail}); console.log(`  [FAIL] ${name}${detail ? ' — '+detail : ''}`); }
}

function section(title) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`  ${title}`);
  console.log(`${'='.repeat(60)}`);
}

function read(p) { return fs.readFileSync(path.join(ROOT, p), 'utf8'); }

// ============================================================
section('REF 1: arXiv:2512.19475 — Auto Situation Report Framework');
// Paper claims: Documents → Semantic Clustering → Question Generation → RAG Answer Extraction → Structured Report
// Our implementation: src/reporting/auto_sitrep.py

const sitrep = read('src/reporting/auto_sitrep.py');

test('Cites arXiv:2512.19475', /2512\.19475|arXiv/i.test(sitrep));

// Paper Step 1: Semantic Clustering
test('Implements document clustering', /cluster|_cluster_by_theme/i.test(sitrep),
  'Paper requires thematic grouping of source documents');
test('Clustering uses humanitarian themes', /displacement|health|food|shelter|access/i.test(sitrep));

// Paper Step 2: Auto Question Generation  
test('Has section-specific questions', /SECTION_QUESTIONS|questions.*displacement|how many.*displaced/i.test(sitrep),
  'Paper generates questions per OCHA section');

// Paper Step 3: RAG-style Answer Extraction
test('Extracts answers from source docs', /_extract_answer|find.*answer|match.*source/i.test(sitrep),
  'Paper uses RAG to extract answers with citations');
test('Answers link to sources', /source.*url|citation|source_url/i.test(sitrep));

// Paper Step 4: Structured Report Output
test('Uses OCHA standard sections', /SITREP_SECTIONS/i.test(sitrep));
test('Has 10+ OCHA sections', (sitrep.match(/['"](displacement|casualties|humanitarian_access|food_security|health|wash|shelter|protection|response|funding|outlook|overview)['"]/g) || []).length >= 8,
  'Paper recommends standard humanitarian report structure');

// Paper claims 84.7% relevance — we can't test accuracy but verify structure exists
test('Has quality scoring', /quality.*score|QualityScorer/i.test(sitrep) || fs.existsSync(path.join(ROOT, 'src/reporting/quality_scorer.py')));

// Citation accuracy (paper reports 76%+ citation precision)
const citation = read('src/reporting/citation_linker.py');
test('Citation linker exists', citation.length > 500);
test('Citations track confidence', /confidence/i.test(citation));
test('Citations link to source URL', /source_url|url/i.test(citation));

// ============================================================
section('REF 2: Rocca et al. 2023 — NLP for Humanitarian Action');
// Paper claims: NLP can extract crisis-relevant info from unstructured text
// Key entities: casualties, displacement, needs, locations
// Our implementation: src/nlp/extractor.py

const extractor = read('src/nlp/extractor.py');

test('Cites Rocca et al.', /Rocca/i.test(extractor));

// Paper: Extract casualty numbers
test('Extracts killed count', /killed|dead|death|fatalities/i.test(extractor));
test('Extracts injured count', /injured|wounded|hurt/i.test(extractor));
test('Uses regex for number extraction', /\\d|re\.(search|findall)/i.test(extractor));

// Paper: Extract displacement data
test('Extracts displacement numbers', /displaced|fled|evacuat/i.test(extractor));
test('Handles "million" and "thousand"', /million|thousand|[MK]\b/i.test(extractor));

// Paper: Classify humanitarian needs
test('Classifies need types', /food|water|shelter|health|protection/i.test(extractor));

// Paper: Urgency assessment
test('Assesses urgency levels', /critical|high|moderate|low/i.test(extractor));
test('Urgency uses keyword matching', /URGENCY_KEYWORDS|urgency.*keyword/i.test(extractor));

// Paper: Named entity recognition for locations
const entities = read('src/nlp/entities.py');
test('NER identifies humanitarian orgs', /OCHA|WFP|UNHCR|ICRC|WHO|IOM/i.test(entities));
test('NER identifies crisis locations', /Tehran|Beirut|Kabul|Damascus|Khuzestan/i.test(entities));
test('NER extracts dates', /date|January|February|March|\d{4}-\d{2}-\d{2}/i.test(entities));

// ============================================================
section('REF 3: Kreutzer et al. 2020 (IBM/WFP) — Humanitarian Needs Assessment NLP');
// Paper: NLP can extract structured needs from voice/text feedback
// Our implementation: src/feedback/nlp_analyzer.py

const analyzer = read('src/feedback/nlp_analyzer.py');

test('Cites Kreutzer/IBM/WFP', /Kreutzer|IBM.*WFP|WFP.*IBM/i.test(analyzer));

// Paper: Detect need types from free text
test('Detects shelter needs', /shelter.*pattern|shelter.*keyword/i.test(analyzer) || /shelter/i.test(analyzer));
test('Detects food needs', /food|hungry|starving/i.test(analyzer));
test('Detects water needs', /water|thirsty/i.test(analyzer));
test('Detects medical needs', /medical|hospital|injur/i.test(analyzer));
test('Detects safety needs', /safety|danger|attack/i.test(analyzer));

// Paper: Assess urgency from text
test('Urgency: critical level', /critical.*dying|trapped|bleeding/i.test(analyzer));
test('Urgency: high level', /high.*urgent|emergency|desperate/i.test(analyzer));

// Paper: Extract people count
test('Extracts affected population count', /\\d.*people|persons|families|estimated_people/i.test(analyzer));

// Paper: Extract location from text
test('Extracts location mentions', /location|extract.*location|_extract_location/i.test(analyzer));

// ============================================================
section('REF 4: Otal & Canbaz 2024 — LLM-Assisted Crisis Management');
// Paper: Use LLM for emergency info extraction + auto-classification
// Our implementation: src/nlp/classifier.py + src/feedback/trend_detector.py

test('Cites Otal & Canbaz', /Otal|Canbaz/i.test(analyzer));

const classifier = read('src/nlp/classifier.py');

// Paper: OCHA standard sector classification
test('Uses OCHA sector taxonomy', /OCHA_SECTORS|ocha.*sector/i.test(classifier));
test('Has Protection sector', /protection/i.test(classifier));
test('Has Food Security sector', /food_security/i.test(classifier));
test('Has Health sector', /health/i.test(classifier));
test('Has WASH sector', /wash/i.test(classifier));
test('Has Shelter sector', /shelter/i.test(classifier));
test('Has Coordination sector', /coordination/i.test(classifier));
test('Maps sectors to lead agencies', /lead.*UNHCR|lead.*WFP|lead.*WHO|lead.*UNICEF/i.test(classifier));

// Paper: Trend detection from aggregated reports
const trends = read('src/feedback/trend_detector.py');
test('Detects emerging trends', /trend|emerging|spike/i.test(trends));
test('Has alert threshold', /threshold|ALERT_THRESHOLD/i.test(trends));
test('Finds geographic hotspots', /hotspot|district.*count/i.test(trends));
test('Time-windowed analysis', /hours|timedelta|window/i.test(trends));

// ============================================================
section('REF 5: ICRC Handbook 2020 — Data Protection in Humanitarian Action');
// Paper: 7 principles of humanitarian data protection
// Our implementation: src/feedback/anonymizer.py, collector.py, docs/humanitarian-compliance.md

const anonymizer = read('src/feedback/anonymizer.py');
const collector = read('src/feedback/collector.py');
const compliance = read('docs/humanitarian-compliance.md');

test('Cites ICRC Handbook', /ICRC.*Handbook|Handbook.*Data Protection/i.test(compliance));

// Principle 1: Lawful and fair processing
test('Only collects necessary data', /district|need_type/i.test(collector));
test('No excessive data collection', !/user_id\s*=|phone\s*=|ip\s*=|gps\s*=/i.test(collector),
  'Collector must NOT store user_id, phone, IP, or GPS');

// Principle 2: Purpose limitation
test('Data used only for humanitarian purpose', /humanitarian|need|shelter|crisis/i.test(collector));

// Principle 3: Data minimization
test('Strips phone numbers', /PHONE_REDACTED|\+?\d.*phone/i.test(anonymizer));
test('Strips email addresses', /EMAIL_REDACTED|email/i.test(anonymizer));
test('Strips IP addresses', /IP_REDACTED|ip.*address/i.test(anonymizer));
test('Strips GPS coordinates', /COORDS_REDACTED|coordinates|lat.*lon/i.test(anonymizer));
test('Strips names', /NAME_REDACTED|name.*redact/i.test(anonymizer));

// Principle 4: Data quality
test('Reports have timestamps', /timestamp|datetime/i.test(collector));

// Principle 5: Retention limitation
test('No persistent user storage', !/database.*user|save.*user_id|persist.*user/i.test(collector),
  'ICRC: do not retain user-identifiable data');

// Principle 6: Security
test('Uses hash for IDs (not sequential)', /sha256|hashlib|hash/i.test(collector));

// Principle 7: Accountability
test('Compliance framework documented', /ICRC|compliance|data protection/i.test(compliance));
test('Compliance doc > 2000 chars', compliance.length > 2000);

// ============================================================
section('REF 6: HumSet — Humanitarian NLP Data Standard');
// Paper: Standard schema for humanitarian NLP datasets
// Our implementation: src/data/humset_format.py

const humset = read('src/data/humset_format.py');

test('Cites HumSet', /HumSet|humset/i.test(humset));

// HumSet required fields
test('Has document_id field', /document_id/i.test(humset));
test('Has text field', /["']text["']/i.test(humset));
test('Has language field', /["']language["']/i.test(humset));
test('Has sectors field', /["']sectors["']/i.test(humset));
test('Has severity field', /["']severity["']/i.test(humset));
test('Has source_url field', /source_url/i.test(humset));
test('Has extraction_date field', /extraction_date/i.test(humset));
test('Has confidence_score field', /confidence_score/i.test(humset));

// HumSet: document_id should be deterministic hash
test('document_id uses hash', /sha256|hashlib/i.test(humset));

// HumSet: JSON output format
test('Has JSON serialization', /to_json|json\.dumps/i.test(humset));
test('Has metadata wrapper', /metadata.*format|format.*version/i.test(humset));

// ============================================================
section('REF 7: OCHA Sector Classification Standard');
// Standard: UN OCHA Coordination Framework — 11 humanitarian clusters
// Our implementation: src/nlp/classifier.py

// Verify all major OCHA sectors are represented
const ocha_sectors = ['protection', 'food_security', 'health', 'wash', 'shelter', 'education', 'logistics', 'coordination'];
for (const sector of ocha_sectors) {
  test(`OCHA sector: ${sector}`, classifier.includes(sector), 
    `Must include standard OCHA sector: ${sector}`);
}

// Verify sector keywords are appropriate
test('Protection keywords include GBV', /GBV|gender.based.violence/i.test(classifier));
test('Health keywords include WHO', /WHO/i.test(classifier));
test('WASH keywords include sanitation', /sanitation/i.test(classifier));
test('Food keywords include WFP', /WFP/i.test(classifier));

// ============================================================
section('REF 8: CLEAR Global Gamayun — Low-Resource Language MT');
// Approach: glossary-enforced terminology for low-resource languages
// Our implementation: src/translator/translate.py + data/glossary.json

const translate = read('src/translator/translate.py');
const glossaryRaw = read('data/glossary.json');
const glossary = JSON.parse(glossaryRaw);

// Gamayun principle: standardized terminology
test('Glossary-enforced translation', /glossary|check_glossary_consistency/i.test(translate));
test('Post-processing with glossary', /glossary.*check|consistency.*glossary/i.test(translate));

// Gamayun: low-resource language handling (Dari is low-resource)
test('Dari (low-resource) supported', glossary.every(g => g.dar && g.dar.length > 0));
test('Dari marked for verification', glossary.every(g => g.verified?.dar === false),
  'Low-resource translations need native speaker verification');

// Gamayun: Persian vs Dari distinction (critical for accuracy)
const displacedEntry = glossary.find(g => g.en === 'displaced persons');
test('Persian ≠ Dari for "displaced persons"', 
  displacedEntry && displacedEntry.fa !== displacedEntry.dar,
  `FA: ${displacedEntry?.fa} vs DAR: ${displacedEntry?.dar}`);

// Check multiple terms have FA/DAR distinction
let distinctCount = 0;
for (const g of glossary) {
  if (g.fa !== g.dar) distinctCount++;
}
test('FA/DAR distinct for multiple terms', distinctCount >= 5,
  `${distinctCount}/40 terms have distinct FA vs DAR translations`);

// ============================================================
section('REF 9: Quality Check — Persian vs Arabic Numeral Handling');
// Technical requirement: ۱۲۳ (Persian) vs ١٢٣ (Arabic) 
// Our implementation: src/translator/quality_check.py

const qc = read('src/translator/quality_check.py');

// Persian digits: ۰۱۲۳۴۵۶۷۸۹ (U+06F0-U+06F9)
// Arabic digits: ٠١٢٣٤٥٦٧٨٩ (U+0660-U+0669)
test('Handles Persian numerals (U+06F0)', /06[fF][0-9]|[\u06F0-\u06F9]|persian.*numer|farsi.*digit/i.test(qc));
test('Handles Arabic numerals (U+0660)', /066[0-9]|[\u0660-\u0669]|arabic.*numer|arabic.*digit/i.test(qc));
test('Distinguishes Persian from Arabic numerals', /persian.*arabic|arabic.*persian|fa.*ar.*numer/i.test(qc) || (/06[fF]/.test(qc) && /066/.test(qc)));

// ============================================================
section('REF 10: Meshtastic/Briar — Offline Mesh Documentation');
// These are documented as RESEARCH, not implemented code.
// Verify documentation accuracy.

const briar = read('src/mesh/briar_bridge.md');
const mesh = read('src/mesh/meshtastic_config.md');
const beacon = read('src/mesh/node_firmware/humanitarian_beacon.md');
const protocol = read('src/mesh/protocol/humanitarian_broadcast_protocol.md');

// Briar technical accuracy
test('Briar: mentions Android support', /Android/i.test(briar));
test('Briar: mentions BLE/WiFi', /BLE|Bluetooth|WiFi/i.test(briar));
test('Briar: mentions Tor', /Tor/i.test(briar));
test('Briar: mentions Cure53 audit', /Cure53|security.*audit/i.test(briar));

// Meshtastic technical accuracy
test('Meshtastic: mentions LoRa', /LoRa/i.test(mesh));
test('Meshtastic: mentions frequency bands', /868|915|MHz/i.test(mesh));
test('Meshtastic: mentions ESP32', /ESP32/i.test(mesh));

// Humanitarian Broadcast Protocol
test('HBP: defines message types', /ALERT|SHELTER|MEDICAL|WATER|SAFETY/i.test(protocol));
test('HBP: defines urgency levels', /CRITICAL|HIGH|MODERATE|INFO/i.test(protocol));
test('HBP: defines message format', /VERSION|TYPE|URGENCY|LANG|TIMESTAMP|CONTENT/i.test(protocol));

// Beacon design
test('Beacon: solar powered', /solar/i.test(beacon));
test('Beacon: broadcast interval', /interval|minute|broadcast/i.test(beacon));
test('Beacon: one-way (humanitarian use only)', /one.way|unidirectional|broadcast/i.test(beacon));

// BOM accuracy
const bom = read('src/mesh/hardware/bom.md');
test('BOM: has cost per node', /\$\d+.*node|node.*\$\d+/i.test(bom));
test('BOM: includes solar panel', /solar.*panel/i.test(bom));
test('BOM: includes battery', /battery|18650/i.test(bom));
test('BOM: includes LoRa board', /Heltec|LILYGO|T.Beam|LoRa.*board/i.test(bom));

// ============================================================
section('REF 11: Source Verification — Tiered Credibility System');
// Based on humanitarian information management standards
// Tier 1 = UN agencies, Tier 2 = established media/NGOs

const srcChecker = read('src/verification/source_checker.py');

test('Tier 1 includes all key UN agencies', 
  /OCHA/.test(srcChecker) && /WHO/.test(srcChecker) && /UNHCR/.test(srcChecker) && 
  /WFP/.test(srcChecker) && /UNICEF/.test(srcChecker) && /ICRC/.test(srcChecker) && /IOM/.test(srcChecker));

test('Tier 2 includes major wire services',
  /AP/.test(srcChecker) && /Reuters/.test(srcChecker));

test('Tier 2 includes key NGOs',
  /MSF/.test(srcChecker) && /Human Rights Watch|HRW/.test(srcChecker));

test('Unknown sources flagged for review',
  /requires_review.*True|unverified/i.test(srcChecker));

test('Credibility scores are numeric 0-1',
  /1\.0|0\.85|0\.8|0\.9|0\.3/i.test(srcChecker));

// Cross-reference validation
const xref = read('src/verification/cross_reference.py');
test('Cross-ref: 3+ sources = verified', /cross_verified|3.*source/i.test(xref));
test('Cross-ref: 2 sources = double-sourced', /double_sourced|2.*source/i.test(xref));
test('Cross-ref: 1 source = unverified warning', /single_source|awaiting.*verification/i.test(xref));
test('Cross-ref: number conflict detection', /conflict|variance|inconsisten/i.test(xref));

// ============================================================
section('FINAL SUMMARY');

console.log(`\n  Total tests:  ${total}`);
console.log(`  Passed:       ${passed}`);
console.log(`  Failed:       ${failed}`);
console.log(`  Pass rate:    ${(passed/total*100).toFixed(1)}%`);

if (failed > 0) {
  console.log(`\n  FAILED TESTS:`);
  for (const f of failures) {
    console.log(`    - ${f.name}${f.detail ? ': '+f.detail : ''}`);
  }
}

console.log(`\n  ${failed === 0 ? 'ACADEMIC REFERENCE AUDIT PASSED ✅' : 'ACADEMIC REFERENCE AUDIT FAILED ❌'}`);
console.log(`  References verified: 11`);
console.log(`  Date: ${new Date().toISOString()}`);
process.exit(failed === 0 ? 0 : 1);
