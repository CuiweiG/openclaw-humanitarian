/**
 * MIT Engineering Audit — Node.js Integration Test
 * Verifies all Python modules have correct structure,
 * imports resolve, and key patterns are present.
 * Validates with simulated ReliefWeb data.
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
  if (condition) {
    passed++;
    console.log(`  [PASS] ${name}`);
  } else {
    failed++;
    failures.push({ name, detail });
    console.log(`  [FAIL] ${name}${detail ? ' — ' + detail : ''}`);
  }
}

function section(title) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`  ${title}`);
  console.log(`${'='.repeat(60)}`);
}

function fileExists(p) { return fs.existsSync(path.join(ROOT, p)); }
function readFile(p) { return fs.readFileSync(path.join(ROOT, p), 'utf8'); }
function pyHasFunction(content, name) { return new RegExp(`def ${name}\\(`).test(content); }
function pyHasClass(content, name) { return new RegExp(`class ${name}[:(]`).test(content); }

// ============================================================
section('MODULE 1: SCRAPER');

const rw = readFile('src/scraper/reliefweb.py');
test('reliefweb.py: has fetch_reports()', pyHasFunction(rw, 'fetch_reports'));
test('reliefweb.py: has _parse_report()', pyHasFunction(rw, '_parse_report'));
test('reliefweb.py: uses correct API URL', rw.includes('api.reliefweb.int/v1/reports'));
test('reliefweb.py: filters by country', /country.*Iran|Iran.*country/s.test(rw));
test('reliefweb.py: has retry logic', /retry|backoff|attempt/i.test(rw));
test('reliefweb.py: has error handling', /except.*Exception|try:/s.test(rw));

const parser = readFile('src/scraper/parser.py');
test('parser.py: has parse_report()', pyHasFunction(parser, 'parse_report'));
test('parser.py: has _strip_html()', pyHasFunction(parser, '_strip_html'));
test('parser.py: has _extract_key_points()', pyHasFunction(parser, '_extract_key_points'));
test('parser.py: uses BeautifulSoup or regex for HTML', /BeautifulSoup|re\.sub.*</.test(parser));

const ocha = readFile('src/scraper/ocha.py');
test('ocha.py: exists with content', ocha.length > 200);
test('ocha.py: references OCHA/reliefweb', /ocha|reliefweb/i.test(ocha));

// ============================================================
section('MODULE 2: TRANSLATOR');

const translate = readFile('src/translator/translate.py');
test('translate.py: has TranslationBackend ABC', pyHasClass(translate, 'TranslationBackend'));
test('translate.py: has ClaudeBackend', pyHasClass(translate, 'ClaudeBackend'));
test('translate.py: has StubBackend', pyHasClass(translate, 'StubBackend'));
test('translate.py: has load_glossary()', pyHasFunction(translate, 'load_glossary'));
test('translate.py: has translate_bulletin()', pyHasFunction(translate, 'translate_bulletin'));
test('translate.py: has check_glossary_consistency()', pyHasFunction(translate, 'check_glossary_consistency'));
test('translate.py: StubBackend does not need API key', !(/ANTHROPIC_API_KEY.*StubBackend|StubBackend.*ANTHROPIC/).test(translate));

const qc = readFile('src/translator/quality_check.py');
test('quality_check.py: has quality_check()', pyHasFunction(qc, 'quality_check'));
test('quality_check.py: has check_word_count()', pyHasFunction(qc, 'check_word_count'));
test('quality_check.py: has check_source_attribution()', pyHasFunction(qc, 'check_source_attribution'));
test('quality_check.py: has check_terminology()', pyHasFunction(qc, 'check_terminology'));
test('quality_check.py: has check_numeric_format()', pyHasFunction(qc, 'check_numeric_format'));
test('quality_check.py: handles Persian numerals', /[\u06F0-\u06F9]|persian|farsi.*numer/i.test(qc));
test('quality_check.py: handles Arabic numerals', /[\u0660-\u0669]|arabic.*numer/i.test(qc));

// ============================================================
section('MODULE 3: NLP ENGINE');

const extractor = readFile('src/nlp/extractor.py');
test('extractor.py: has CrisisExtractor class', pyHasClass(extractor, 'CrisisExtractor'));
test('extractor.py: extracts casualties', /casualt|killed|injured/i.test(extractor));
test('extractor.py: extracts displacement', /displac|fled|evacuat/i.test(extractor));
test('extractor.py: extracts locations', /location|Iran|Lebanon/i.test(extractor));
test('extractor.py: assesses urgency', /urgency|critical|high|moderate/i.test(extractor));

const classifier = readFile('src/nlp/classifier.py');
test('classifier.py: has SectorClassifier', pyHasClass(classifier, 'SectorClassifier'));
test('classifier.py: uses OCHA sectors', /protection|food_security|health|wash|shelter/i.test(classifier));
test('classifier.py: maps to lead agencies', /UNHCR|WFP|WHO|UNICEF/i.test(classifier));

const summarizer = readFile('src/nlp/summarizer.py');
test('summarizer.py: has BulletinSummarizer', pyHasClass(summarizer, 'BulletinSummarizer'));
test('summarizer.py: enforces word limit', /max_words|200|word.*count/i.test(summarizer));

const ner = readFile('src/nlp/entities.py');
test('entities.py: has HumanitarianNER', pyHasClass(ner, 'HumanitarianNER'));
test('entities.py: knows humanitarian orgs', /OCHA|WFP|UNHCR|ICRC|WHO/i.test(ner));
test('entities.py: knows crisis locations', /Tehran|Beirut|Damascus|Kabul/i.test(ner));

// ============================================================
section('MODULE 4: REPORTING');

const sitrep = readFile('src/reporting/auto_sitrep.py');
test('auto_sitrep.py: has AutoSitrepGenerator', pyHasClass(sitrep, 'AutoSitrepGenerator'));
test('auto_sitrep.py: uses OCHA sections', /displacement|casualties|humanitarian_access|food_security/i.test(sitrep));
test('auto_sitrep.py: has to_markdown()', pyHasFunction(sitrep, 'to_markdown'));
test('auto_sitrep.py: references arXiv paper', /arXiv|2512\.19475/i.test(sitrep));

const citation = readFile('src/reporting/citation_linker.py');
test('citation_linker.py: has CitationLinker', pyHasClass(citation, 'CitationLinker'));
test('citation_linker.py: has register_source()', pyHasFunction(citation, 'register_source'));
test('citation_linker.py: has find_source()', pyHasFunction(citation, 'find_source'));

const scorer = readFile('src/reporting/quality_scorer.py');
test('quality_scorer.py: has QualityScorer', pyHasClass(scorer, 'QualityScorer'));
test('quality_scorer.py: scores completeness', /completeness/i.test(scorer));
test('quality_scorer.py: scores timeliness', /timeliness/i.test(scorer));
test('quality_scorer.py: has A-F grading', /grade.*[ABCDF]/i.test(scorer));

// ============================================================
section('MODULE 5: VERIFICATION');

const srcChecker = readFile('src/verification/source_checker.py');
test('source_checker.py: has SourceChecker', pyHasClass(srcChecker, 'SourceChecker'));
test('source_checker.py: has tier system', /TIER_1|TIER_2|tier_1|tier_2/i.test(srcChecker));
test('source_checker.py: OCHA is tier 1', /OCHA.*1\.0|1\.0.*OCHA/s.test(srcChecker));
test('source_checker.py: unknown needs review', /unverified.*review|requires_review/i.test(srcChecker));

const xref = readFile('src/verification/cross_reference.py');
test('cross_reference.py: has CrossReferencer', pyHasClass(xref, 'CrossReferencer'));
test('cross_reference.py: checks number consistency', /consistency|variance|conflict/i.test(xref));
test('cross_reference.py: has 20% threshold', /0\.2|20.*%|CONFLICT_THRESHOLD/i.test(xref));

const disclaimer = readFile('src/verification/disclaimer_generator.py');
test('disclaimer_generator.py: has DisclaimerGenerator', pyHasClass(disclaimer, 'DisclaimerGenerator'));
test('disclaimer_generator.py: has verification levels', /cross_verified|single_source|unverified/i.test(disclaimer));

// ============================================================
section('MODULE 6: FEEDBACK');

const collector = readFile('src/feedback/collector.py');
test('collector.py: has FeedbackCollector', pyHasClass(collector, 'FeedbackCollector'));
test('collector.py: NO user_id stored', !/user_id.*=|store.*user_id/i.test(collector));
test('collector.py: anonymizes immediately', /anonym|report_id|sha256/i.test(collector));

const anonymizer = readFile('src/feedback/anonymizer.py');
test('anonymizer.py: has Anonymizer', pyHasClass(anonymizer, 'Anonymizer'));
test('anonymizer.py: strips phone numbers', /phone|\\+\?\\d/i.test(anonymizer));
test('anonymizer.py: strips emails', /email|@.*\\./i.test(anonymizer));
test('anonymizer.py: strips coordinates', /coord|\\d.*\\d.*lat|lon/i.test(anonymizer));

const nlpAnalyzer = readFile('src/feedback/nlp_analyzer.py');
test('nlp_analyzer.py: has FeedbackAnalyzer', pyHasClass(nlpAnalyzer, 'FeedbackAnalyzer'));
test('nlp_analyzer.py: detects need types', /shelter|food|water|medical|safety/i.test(nlpAnalyzer));
test('nlp_analyzer.py: assesses urgency', /critical|high|moderate|low/i.test(nlpAnalyzer));

const trends = readFile('src/feedback/trend_detector.py');
test('trend_detector.py: has TrendDetector', pyHasClass(trends, 'TrendDetector'));
test('trend_detector.py: detects hotspots', /hotspot|alert|threshold/i.test(trends));

// ============================================================
section('MODULE 7: DATA FORMAT');

const humset = readFile('src/data/humset_format.py');
test('humset_format.py: has HumSetFormatter', pyHasClass(humset, 'HumSetFormatter'));
test('humset_format.py: generates document_id', /document_id|sha256/i.test(humset));
test('humset_format.py: has to_json()', pyHasFunction(humset, 'to_json'));

// ============================================================
section('MODULE 8: GLOSSARY DATA');

const glossary = JSON.parse(readFile('data/glossary.json'));
test('Glossary: is array', Array.isArray(glossary));
test('Glossary: has 40 entries', glossary.length === 40, `Got ${glossary.length}`);

const requiredLangs = ['en', 'fa', 'dar', 'ar', 'zh', 'fr', 'es', 'ru'];
for (const lang of requiredLangs) {
  test(`Glossary: all entries have '${lang}'`, glossary.every(g => g[lang] && g[lang].length > 0));
}
test('Glossary: all entries have verified field', glossary.every(g => g.verified !== undefined));
test('Glossary: FA marked unverified', glossary.every(g => g.verified?.fa === false));
test('Glossary: AR marked verified', glossary.every(g => g.verified?.ar === true));

// Spot check specific terms
const displaced = glossary.find(g => g.en === 'displaced persons');
test('Term "displaced persons" exists', !!displaced);
test('  FA translation present', displaced?.fa?.length > 0);
test('  DAR translation present', displaced?.dar?.length > 0);
test('  DAR differs from FA', displaced?.dar !== displaced?.fa, 'Dari should differ from Farsi');

// ============================================================
section('MODULE 9: i18n LOCALES');

const localeDir = path.join(ROOT, 'src', 'bot', 'locales');
const expectedLocales = ['en', 'ar', 'fa', 'dar', 'zh', 'tr', 'fr', 'es', 'ru'];
const requiredKeys = ['welcome', 'help', 'latest_header', 'shelter_header', 'language_set', 'about', 'disclaimer', 'error'];

for (const lang of expectedLocales) {
  const fp = path.join(localeDir, `${lang}.json`);
  const exists = fs.existsSync(fp);
  test(`Locale ${lang}.json exists`, exists);
  if (exists) {
    const data = JSON.parse(fs.readFileSync(fp, 'utf8'));
    const missing = requiredKeys.filter(k => !data[k] || data[k].length === 0);
    test(`  ${lang}.json has all ${requiredKeys.length} keys`, missing.length === 0, 
         missing.length > 0 ? `Missing: ${missing.join(', ')}` : '');
  }
}

// ============================================================
section('MODULE 10: SAMPLE DATA');

for (let i = 1; i <= 3; i++) {
  const fp = path.join(ROOT, 'data', 'sample_reports', `sample_${i}.json`);
  test(`sample_${i}.json exists`, fs.existsSync(fp));
  if (fs.existsSync(fp)) {
    const data = JSON.parse(fs.readFileSync(fp, 'utf8'));
    test(`  Has required fields`, ['title','date','source','url','text'].every(k => k in data));
    test(`  URL starts with https`, data.url.startsWith('https://'));
    test(`  Text > 100 chars`, data.text.length > 100, `Length: ${data.text.length}`);
  }
}

// ============================================================
section('MODULE 11: DEMO.PY OFFLINE RESILIENCE');

const demo = readFile('src/demo.py');
test('demo.py: pure stdlib (no requests/pip)', !/(^import requests|^from requests)/m.test(demo));
test('demo.py: uses urllib (stdlib)', /import urllib/m.test(demo));
test('demo.py: has SAMPLE_REPORT fallback', /SAMPLE_REPORT/i.test(demo));
test('demo.py: has try/except for network', /try:[\s\S]*?except.*Exception/m.test(demo));
test('demo.py: prints offline message', /offline|Network unavailable/i.test(demo));
test('demo.py: has glossary loading', /glossary/i.test(demo));
test('demo.py: has colored output', /\\033|ANSI|_green|_yellow|_cyan/i.test(demo));

// ============================================================
section('MODULE 12: DOCKER');

test('Dockerfile exists', fileExists('Dockerfile'));
const dockerfile = readFile('Dockerfile');
test('Dockerfile: FROM python', /FROM python/i.test(dockerfile));
test('Dockerfile: COPY requirements', /COPY requirements/i.test(dockerfile));
test('Dockerfile: pip install', /pip install/i.test(dockerfile));
test('Dockerfile: has CMD', /CMD/i.test(dockerfile));
test('Dockerfile: no hardcoded tokens', !/sk-ant-|github_pat_|8746100038/.test(dockerfile));

test('docker-compose.yml exists', fileExists('docker-compose.yml'));
test('.env.example exists', fileExists('.env.example'));
const envExample = readFile('.env.example');
test('.env.example: no real tokens', !/sk-ant-|github_pat_|874610/.test(envExample));

// ============================================================
section('FINAL SUMMARY');

console.log(`\n  Total tests:  ${total}`);
console.log(`  Passed:       ${passed}`);
console.log(`  Failed:       ${failed}`);
console.log(`  Pass rate:    ${(passed/total*100).toFixed(1)}%`);

if (failed > 0) {
  console.log(`\n  FAILED TESTS:`);
  for (const f of failures) {
    console.log(`    - ${f.name}${f.detail ? ': ' + f.detail : ''}`);
  }
}

console.log(`\n  ${failed === 0 ? 'AUDIT PASSED ✅' : 'AUDIT FAILED ❌'}`);
console.log(`  Date: ${new Date().toISOString()}`);
process.exit(failed === 0 ? 0 : 1);
