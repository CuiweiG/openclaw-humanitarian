#!/usr/bin/env python3
"""
MIT Engineering Audit — Integration Test Suite
Simulates every claimed feature with realistic data.
Runs WITHOUT any API keys or network access.

Usage: python tests/integration_audit.py
"""

import json
import os
import sys
import re
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================
# REALISTIC SIMULATION DATA
# Based on actual UNHCR/WFP/OCHA reports from March 2026
# ============================================================

SIMULATED_RELIEFWEB_RESPONSE = {
    "count": 3,
    "data": [
        {
            "id": "4182931",
            "fields": {
                "title": "WFP Middle East Regional Escalation Emergency Response — Situation Report #4",
                "body-html": "<p>Almost a month into the escalation, hostilities continue to intensify and expand across multiple fronts, driving displacement, disrupting livelihoods. In <strong>Iran</strong>, WFP continues to provide food and cash assistance to around 33,000 Afghan refugees in settlements. In <strong>Lebanon</strong>, as evacuation orders widen and displacement accelerates, access remains unpredictable. In <strong>Syria</strong>, WFP has provided date bars to over 58,000 Syrian returnees.</p>",
                "date": {"created": "2026-03-26T00:00:00+00:00"},
                "source": [{"name": "World Food Programme"}],
                "url": "https://reliefweb.int/report/iran-islamic-republic/wfp-middle-east-regional-escalation-emergency-response-situation-report-4"
            }
        },
        {
            "id": "4182845",
            "fields": {
                "title": "Lebanon: Conflict Intensity, 2 March – 25 March 2026",
                "body-html": "<p>Published by OCHA, this snapshot report maps conflict intensity and displacement orders across Lebanon. Active hostilities continue in multiple areas, particularly in the south. Evacuation orders have expanded geographically. An estimated 135,000 people are sheltering in 645 collective shelters. Humanitarian access remains severely restricted.</p>",
                "date": {"created": "2026-03-26T00:00:00+00:00"},
                "source": [{"name": "UN Office for the Coordination of Humanitarian Affairs"}],
                "url": "https://reliefweb.int/report/lebanon/lebanon-conflict-intensity-2-march-25-march-2026"
            }
        },
        {
            "id": "4182799",
            "fields": {
                "title": "Flash Refugee Response Plan: Refugees in Iran, March–May 2026",
                "body-html": "<p>Iran hosts the largest refugee population in the sub-region, the vast majority from Afghanistan. 600,000 to one million households have temporarily left their residences. Refugees are struggling with safety concerns, job loss, psychological distress, and urgent shelter needs. Ongoing conflict and frequent aerial strikes make it harder to reach humanitarian services.</p>",
                "date": {"created": "2026-03-26T00:00:00+00:00"},
                "source": [{"name": "UN High Commissioner for Refugees"}],
                "url": "https://reliefweb.int/report/iran-islamic-republic/rrp-flash-refugee-response-plan"
            }
        }
    ]
}

SIMULATED_USER_FEEDBACK = [
    {"text": "No water in Khuzestan for 3 days, 200 people need help urgently", "district": "Khuzestan", "lang": "en"},
    {"text": "All shelters full in South Beirut, families sleeping in cars", "district": "South Beirut", "lang": "en"},
    {"text": "Need medicine for children, hospital destroyed", "district": "Tyre", "lang": "en"},
    {"text": "No electricity, no internet, cannot contact family in Tehran", "district": "Isfahan", "lang": "en"},
    {"text": "Food running out, no distribution for 5 days, 50 families", "district": "Khuzestan", "lang": "en"},
]

# ============================================================
# TEST RESULTS TRACKING
# ============================================================
results = []

def test(name, passed, detail=""):
    icon = "PASS" if passed else "FAIL"
    results.append({"name": name, "passed": passed, "detail": detail})
    print(f"  [{icon}] {name}")
    if detail and not passed:
        print(f"         {detail}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ============================================================
# MODULE 1: SCRAPER — ReliefWeb API Parser
# ============================================================
section("MODULE 1: SCRAPER (src/scraper/)")

try:
    from src.scraper.reliefweb import _parse_report
    
    # Test: Parse a simulated ReliefWeb API response entry
    raw_entry = SIMULATED_RELIEFWEB_RESPONSE["data"][0]["fields"]
    parsed = _parse_report(SIMULATED_RELIEFWEB_RESPONSE["data"][0])
    
    test("_parse_report returns dict", isinstance(parsed, dict))
    test("Parsed has 'title'", "title" in parsed, f"Keys: {list(parsed.keys())}")
    test("Title matches", "WFP" in parsed.get("title", ""), f"Got: {parsed.get('title', '')[:50]}")
    test("Has 'url' field", "url" in parsed and parsed["url"].startswith("http"))
    test("Has 'date' field", "date" in parsed)
    test("Has 'source' field", "source" in parsed)
    test("Has 'body' or 'summary'", "body" in parsed or "summary" in parsed)
    
except ImportError as e:
    test("Import reliefweb module", False, str(e))
except Exception as e:
    test("Parse ReliefWeb entry", False, f"{type(e).__name__}: {e}")

try:
    from src.scraper.parser import parse_report, _strip_html, _extract_key_points
    
    # Test: HTML stripping
    html = "<p>This is <strong>bold</strong> text with <a href='#'>a link</a>.</p>"
    stripped = _strip_html(html)
    test("HTML strip removes tags", "<" not in stripped, f"Got: {stripped}")
    test("HTML strip preserves text", "bold" in stripped and "link" in stripped)
    
    # Test: Key point extraction
    long_text = "WFP provides food to 33,000 refugees. Access is restricted in Lebanon. 58,000 returnees received aid. Evacuation orders expanded. Humanitarian operations face challenges."
    points = _extract_key_points(long_text, max_points=3)
    test("Key points returns list", isinstance(points, list))
    test("Key points count <= max", len(points) <= 3, f"Got {len(points)} points")
    
    # Test: Full parse_report
    sample_report = {
        "title": "Test Report",
        "body": long_text,
        "url": "https://example.com",
        "source": "WFP",
        "date": "2026-03-26"
    }
    parsed_full = parse_report(sample_report)
    test("parse_report returns dict", isinstance(parsed_full, dict))
    test("Parsed has key_points", "key_points" in parsed_full)
    
except ImportError as e:
    test("Import parser module", False, str(e))
except Exception as e:
    test("Parser functions", False, f"{type(e).__name__}: {e}")

# ============================================================
# MODULE 2: TRANSLATOR
# ============================================================
section("MODULE 2: TRANSLATOR (src/translator/)")

try:
    from src.translator.translate import (
        load_glossary, StubBackend, translate_bulletin,
        check_glossary_consistency, TranslationBackend
    )
    
    # Test: Load glossary
    glossary_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "glossary.json")
    glossary = load_glossary(glossary_path)
    test("load_glossary returns list", isinstance(glossary, list))
    test("Glossary has 40 entries", len(glossary) == 40, f"Got {len(glossary)}")
    test("Each entry has 'en'", all("en" in g for g in glossary))
    test("Each entry has 'fa'", all("fa" in g for g in glossary))
    test("Each entry has 'dar'", all("dar" in g for g in glossary))
    test("Each entry has 'ar'", all("ar" in g for g in glossary))
    test("Each entry has 'fr'", all("fr" in g for g in glossary))
    test("Each entry has 'es'", all("es" in g for g in glossary))
    test("Each entry has 'ru'", all("ru" in g for g in glossary))
    test("Each entry has 'verified'", all("verified" in g for g in glossary))
    
    # Test: Verification tracking
    fa_unverified = sum(1 for g in glossary if not g.get("verified", {}).get("fa", True))
    ar_verified = sum(1 for g in glossary if g.get("verified", {}).get("ar", False))
    test("FA terms marked unverified", fa_unverified == 40, f"{fa_unverified}/40 unverified")
    test("AR terms marked verified", ar_verified == 40, f"{ar_verified}/40 verified")
    
    # Test: StubBackend
    stub = StubBackend()
    test("StubBackend is TranslationBackend", isinstance(stub, TranslationBackend))
    stub_result = stub.translate("displaced persons need shelter", "fa")
    test("StubBackend returns string", isinstance(stub_result, str))
    test("StubBackend returns non-empty", len(stub_result) > 0)
    
    # Test: translate_bulletin
    bulletin = translate_bulletin(
        text="WFP provides food assistance to 33,000 displaced persons in Iran",
        source_lang="en",
        target_lang="fa",
        backend=stub,
        glossary=glossary
    )
    test("translate_bulletin returns string", isinstance(bulletin, str))
    test("translate_bulletin non-empty", len(bulletin) > 0)
    
    # Test: Glossary consistency check
    consistency = check_glossary_consistency(
        text="displaced persons need humanitarian access to shelter",
        glossary=glossary,
        language="fa"
    )
    test("check_glossary_consistency returns dict", isinstance(consistency, dict))
    
except ImportError as e:
    test("Import translator module", False, str(e))
except Exception as e:
    test("Translator functions", False, f"{type(e).__name__}: {e}")

# Quality Check
try:
    from src.translator.quality_check import (
        quality_check, check_word_count, check_source_attribution,
        check_terminology, check_numeric_format
    )
    
    # Test: Word count check
    short_text = "This is a short bulletin about displaced persons in Iran."
    wc_result = check_word_count(short_text, max_words=200)
    test("check_word_count returns CheckResult", hasattr(wc_result, 'passed'))
    test("Short text passes word count", wc_result.passed)
    
    long_text = " ".join(["word"] * 250)
    wc_fail = check_word_count(long_text, max_words=200)
    test("Long text fails word count", not wc_fail.passed)
    
    # Test: Source attribution
    with_source = "Report by OCHA, March 2026. Source: reliefweb.int"
    without_source = "Some information without any attribution."
    sa_pass = check_source_attribution(with_source)
    sa_fail = check_source_attribution(without_source)
    test("Text with source passes attribution", sa_pass.passed)
    test("Text without source fails attribution", not sa_fail.passed)
    
    # Test: Full quality check
    qc_result = quality_check(
        text=short_text,
        language="fa",
        glossary=glossary if 'glossary' in dir() else None
    )
    test("quality_check returns QualityReport", hasattr(qc_result, 'passed'))
    
except ImportError as e:
    test("Import quality_check module", False, str(e))
except Exception as e:
    test("Quality check functions", False, f"{type(e).__name__}: {e}")

# ============================================================
# MODULE 3: NLP ENGINE
# ============================================================
section("MODULE 3: NLP ENGINE (src/nlp/)")

try:
    from src.nlp.extractor import CrisisExtractor
    
    extractor = CrisisExtractor()
    
    # Test with realistic text
    crisis_text = """
    Almost a month into the escalation, at least 1,200 people have been killed 
    and 17,000 injured since February 28, 2026. In Iran, WFP continues to provide 
    food and cash assistance to around 33,000 Afghan refugees. In Lebanon, evacuation 
    orders widen and displacement accelerates. 600,000 to 1 million households 
    have been displaced. Humanitarian access remains severely restricted in 
    southern Lebanon. Urgent shelter needs persist.
    """
    
    result = extractor.extract(crisis_text)
    
    test("Extractor returns dict", isinstance(result, dict))
    test("Extracts casualties", result["casualties"]["killed"] >= 1200, 
         f"Got killed={result['casualties']['killed']}")
    test("Extracts injuries", result["casualties"]["injured"] >= 17000,
         f"Got injured={result['casualties']['injured']}")
    test("Identifies Iran", "Iran" in result["locations"])
    test("Identifies Lebanon", "Lebanon" in result["locations"])
    test("Detects food need", "food" in result["needs"])
    test("Detects shelter need", "shelter" in result["needs"])
    test("Urgency is high or critical", result["urgency"] in ["critical", "high"],
         f"Got: {result['urgency']}")
    test("Extracts numbers", len(result["key_numbers"]) > 0,
         f"Found {len(result['key_numbers'])} numbers")
    
except ImportError as e:
    test("Import NLP extractor", False, str(e))
except Exception as e:
    test("NLP extractor", False, f"{type(e).__name__}: {e}")

try:
    from src.nlp.classifier import SectorClassifier
    
    classifier = SectorClassifier()
    sectors = classifier.classify(crisis_text, threshold=1)
    
    test("Classifier returns list", isinstance(sectors, list))
    test("Identifies food_security sector", any(s["sector"] == "food_security" for s in sectors),
         f"Sectors: {[s['sector'] for s in sectors]}")
    test("Identifies shelter sector", any(s["sector"] == "shelter" for s in sectors))
    test("Identifies coordination sector", any(s["sector"] == "coordination" for s in sectors))
    
    primary = classifier.get_primary_sector(crisis_text)
    test("get_primary_sector returns dict", isinstance(primary, dict))
    test("Primary sector has confidence", "confidence" in primary)
    
except ImportError as e:
    test("Import NLP classifier", False, str(e))
except Exception as e:
    test("NLP classifier", False, f"{type(e).__name__}: {e}")

try:
    from src.nlp.summarizer import BulletinSummarizer
    
    summarizer = BulletinSummarizer()
    summary = summarizer.summarize(crisis_text, max_words=50)
    
    test("Summarizer returns string", isinstance(summary, str))
    test("Summary within word limit", len(summary.split()) <= 55,  # small margin
         f"Got {len(summary.split())} words")
    test("Summary is non-empty", len(summary) > 20)
    
except ImportError as e:
    test("Import NLP summarizer", False, str(e))
except Exception as e:
    test("NLP summarizer", False, f"{type(e).__name__}: {e}")

try:
    from src.nlp.entities import HumanitarianNER
    
    ner = HumanitarianNER()
    entities = ner.extract_entities(crisis_text)
    
    test("NER returns dict", isinstance(entities, dict))
    test("Finds WFP org", any(o["abbreviation"] == "WFP" for o in entities["organizations"]))
    test("Finds Iran location", any(l["name"] == "Iran" for l in entities["locations"]))
    test("Finds Lebanon location", any(l["name"] == "Lebanon" for l in entities["locations"]))
    test("Extracts dates", isinstance(entities["dates"], list))
    
except ImportError as e:
    test("Import NLP NER", False, str(e))
except Exception as e:
    test("NLP NER", False, f"{type(e).__name__}: {e}")

# ============================================================
# MODULE 4: REPORTING
# ============================================================
section("MODULE 4: REPORTING (src/reporting/)")

try:
    from src.reporting.auto_sitrep import AutoSitrepGenerator
    
    generator = AutoSitrepGenerator()
    
    # Use simulated documents
    docs = [
        {"title": "WFP Report", "text": crisis_text, "source": "WFP", 
         "url": "https://reliefweb.int/example1", "date": "2026-03-26"},
        {"title": "OCHA Update", "text": "Humanitarian access restricted in southern Lebanon. 645 shelters. 135,000 people sheltering.", 
         "source": "OCHA", "url": "https://reliefweb.int/example2", "date": "2026-03-26"},
    ]
    
    report = generator.generate(docs, date="2026-03-27")
    
    test("generate returns dict", isinstance(report, dict))
    test("Report has sections", "sections" in report)
    test("Report has sources", "sources" in report)
    test("Report date correct", report["date"] == "2026-03-27")
    test("Source count correct", report["source_documents"] == 2)
    test("Has methodology ref", "arXiv" in report.get("methodology", ""))
    
    # Test markdown output
    md = generator.to_markdown(report)
    test("to_markdown returns string", isinstance(md, str))
    test("Markdown has title", "Situation Report" in md)
    test("Markdown has sections", "##" in md)
    
except ImportError as e:
    test("Import reporting module", False, str(e))
except Exception as e:
    test("Reporting module", False, f"{type(e).__name__}: {e}")

try:
    from src.reporting.citation_linker import CitationLinker
    
    linker = CitationLinker()
    key = linker.register_source("WFP report text about food", "https://reliefweb.int/wfp", "WFP", "2026-03-26")
    test("register_source returns key", key.startswith("src_"))
    
    source_match = linker.find_source("food assistance to refugees", 
                                       [{"text": "WFP provides food assistance to Afghan refugees", "source": "WFP", "url": "https://reliefweb.int/wfp"}])
    test("find_source returns dict", isinstance(source_match, dict))
    test("find_source has confidence", "confidence" in source_match)
    
except ImportError as e:
    test("Import citation_linker", False, str(e))
except Exception as e:
    test("Citation linker", False, f"{type(e).__name__}: {e}")

try:
    from src.reporting.quality_scorer import QualityScorer
    
    scorer = QualityScorer()
    score = scorer.score(report)
    
    test("score returns dict", isinstance(score, dict))
    test("Has overall score", 0 <= score["overall"] <= 1, f"Score: {score['overall']}")
    test("Has grade", score["grade"] in ["A", "B", "C", "D", "F"], f"Grade: {score['grade']}")
    test("Has 4 dimensions", len(score["dimensions"]) == 4)
    
except ImportError as e:
    test("Import quality_scorer", False, str(e))
except Exception as e:
    test("Quality scorer", False, f"{type(e).__name__}: {e}")

# ============================================================
# MODULE 5: VERIFICATION
# ============================================================
section("MODULE 5: VERIFICATION (src/verification/)")

try:
    from src.verification.source_checker import SourceChecker
    
    checker = SourceChecker()
    
    # Test tier 1
    ocha = checker.check("OCHA")
    test("OCHA = tier 1", ocha["tier"] == "tier_1_un_agency")
    test("OCHA credibility = 1.0", ocha["credibility"] == 1.0)
    test("OCHA no review needed", not ocha["requires_review"])
    
    # Test tier 2
    reuters = checker.check("Reuters")
    test("Reuters = tier 2", reuters["tier"] == "tier_2_established")
    test("Reuters credibility >= 0.8", reuters["credibility"] >= 0.8)
    
    # Test unknown
    blog = checker.check("Random Blog Post")
    test("Unknown = unverified", blog["tier"] == "unverified")
    test("Unknown requires review", blog["requires_review"])
    test("Unknown low credibility", blog["credibility"] < 0.5)
    
    # Test URL-based detection
    url_check = checker.check("Some Report", "https://reliefweb.int/report/test")
    test("reliefweb.int URL = high credibility", url_check["credibility"] >= 0.9)
    
except ImportError as e:
    test("Import source_checker", False, str(e))
except Exception as e:
    test("Source checker", False, f"{type(e).__name__}: {e}")

try:
    from src.verification.cross_reference import CrossReferencer
    
    xref = CrossReferencer()
    
    sources = [
        {"text": "WFP provides food to 33,000 Afghan refugees in Iran settlements", "source": "WFP"},
        {"text": "Around 33,000 Afghan refugees receive food assistance in Iranian camps", "source": "UNHCR"},
        {"text": "Food aid reaches 33,000 Afghan refugee communities in Iran", "source": "OCHA"},
    ]
    
    result = xref.check_claim("food assistance to Afghan refugees in Iran", sources)
    test("Cross-ref returns dict", isinstance(result, dict))
    test("Multiple sources found", result["supporting_sources"] >= 2,
         f"Found {result['supporting_sources']} sources")
    test("Has verification level", "verification_level" in result)
    
    # Test number consistency
    numbers = [
        {"value": 33000, "source": "WFP"},
        {"value": 33500, "source": "UNHCR"},
    ]
    num_check = xref.check_number_consistency(numbers)
    test("Numbers consistent (within 20%)", num_check["consistent"])
    
    # Test conflicting numbers
    conflict_numbers = [
        {"value": 33000, "source": "WFP"},
        {"value": 100000, "source": "Unknown"},
    ]
    conflict_check = xref.check_number_consistency(conflict_numbers)
    test("Conflicting numbers detected", not conflict_check["consistent"],
         f"Variance: {conflict_check.get('variance', 'N/A')}")
    
except ImportError as e:
    test("Import cross_reference", False, str(e))
except Exception as e:
    test("Cross reference", False, f"{type(e).__name__}: {e}")

try:
    from src.verification.disclaimer_generator import DisclaimerGenerator
    
    gen = DisclaimerGenerator()
    
    verified = gen.generate({"verification_level": "cross_verified", "supporting_sources": 3, "source_names": ["WFP", "UNHCR", "OCHA"]})
    test("Verified disclaimer has checkmark", "✅" in verified)
    
    single = gen.generate({"verification_level": "single_source", "source_names": ["WFP"]})
    test("Single source has warning", "⚠️" in single)
    
    unverified = gen.generate({"verification_level": "unverified"})
    test("Unverified has X mark", "❌" in unverified)
    
    footer = gen.standard_footer()
    test("Standard footer exists", len(footer) > 50)
    test("Footer mentions AI-generated", "AI-generated" in footer)
    
except ImportError as e:
    test("Import disclaimer_generator", False, str(e))
except Exception as e:
    test("Disclaimer generator", False, f"{type(e).__name__}: {e}")

# ============================================================
# MODULE 6: FEEDBACK SYSTEM
# ============================================================
section("MODULE 6: FEEDBACK (src/feedback/)")

try:
    from src.feedback.collector import FeedbackCollector
    from src.feedback.anonymizer import Anonymizer
    from src.feedback.aggregator import ReportAggregator
    from src.feedback.nlp_analyzer import FeedbackAnalyzer
    from src.feedback.trend_detector import TrendDetector
    
    # Test collector
    collector = FeedbackCollector()
    report = collector.process_report(
        district="Khuzestan",
        need_type="water",
        description="No clean water for 3 days, 200 people affected"
    )
    test("Collector returns report", isinstance(report, dict))
    test("Report has ID", "report_id" in report)
    test("Report has district", report["district"] == "Khuzestan")
    test("Report has NO user_id", "user_id" not in report)
    test("Report has NO phone", "phone" not in report)
    
    # Test anonymizer
    anon = Anonymizer()
    text_with_pii = "My name is Ahmad, call me at +98-912-345-6789, email ahmad@test.com, I am at 35.6892, 51.3890"
    cleaned = anon.anonymize_text(text_with_pii)
    test("Phone redacted", "+98-912-345-6789" not in cleaned)
    test("Email redacted", "ahmad@test.com" not in cleaned)
    test("Coords redacted", "35.6892" not in cleaned)
    
    # Test aggregator
    agg = ReportAggregator()
    for fb in SIMULATED_USER_FEEDBACK:
        agg.add_report(collector.process_report(
            district=fb["district"],
            need_type="water" if "water" in fb["text"].lower() else "shelter",
            description=fb["text"]
        ))
    
    summary = agg.generate_summary()
    test("Aggregator summary has total", summary["total_reports"] == 5)
    test("Aggregator finds hotspots", len(summary["hotspots"]) > 0)
    test("Khuzestan is hotspot", any(h["district"] == "Khuzestan" for h in summary["hotspots"]))
    
    # Test NLP analyzer
    analyzer = FeedbackAnalyzer()
    analysis = analyzer.analyze("No water in our area for 3 days, 200 people need help urgently")
    test("Analyzer detects water need", "water" in analysis["needs"])
    test("Analyzer detects urgency", analysis["urgency"] in ["critical", "high"])
    test("Analyzer extracts people count", analysis["estimated_people"] == 200,
         f"Got: {analysis['estimated_people']}")
    
    # Test trend detector
    detector = TrendDetector()
    for fb in SIMULATED_USER_FEEDBACK:
        analyzed = analyzer.analyze(fb["text"])
        detector.add_report(analyzed, fb["district"])
    
    trends = detector.detect_trends(hours=24)
    test("Trend detector returns dict", isinstance(trends, dict))
    test("Has hotspots", len(trends["hotspots"]) > 0)
    test("Has emerging needs", len(trends["emerging_needs"]) > 0)
    
except ImportError as e:
    test("Import feedback modules", False, str(e))
except Exception as e:
    test("Feedback system", False, f"{type(e).__name__}: {e}")

# ============================================================
# MODULE 7: HUMSET FORMAT
# ============================================================
section("MODULE 7: DATA FORMAT (src/data/)")

try:
    from src.data.humset_format import HumSetFormatter
    
    formatter = HumSetFormatter()
    entry = formatter.format_entry(
        text="WFP provides food to 33,000 refugees in Iran",
        language="en",
        source_url="https://reliefweb.int/example",
        sectors=["food_security"],
        severity="high",
        confidence=0.85,
        original_title="WFP Situation Report #4",
        source_org="WFP"
    )
    
    test("HumSet entry has document_id", "document_id" in entry)
    test("HumSet entry has text", entry["text"] == "WFP provides food to 33,000 refugees in Iran")
    test("HumSet entry has language", entry["language"] == "en")
    test("HumSet entry has sectors", entry["sectors"] == ["food_security"])
    test("HumSet entry has confidence", entry["confidence_score"] == 0.85)
    test("HumSet entry has generator", entry["generator"] == "openclaw-humanitarian")
    
    # Test JSON serialization
    json_out = formatter.to_json([entry])
    parsed = json.loads(json_out)
    test("JSON output is valid", "entries" in parsed)
    test("JSON has metadata", "metadata" in parsed)
    test("Entry count correct", parsed["metadata"]["entry_count"] == 1)
    
except ImportError as e:
    test("Import humset_format", False, str(e))
except Exception as e:
    test("HumSet format", False, f"{type(e).__name__}: {e}")

# ============================================================
# MODULE 8: BOT i18n
# ============================================================
section("MODULE 8: BOT i18n (src/bot/locales/)")

locales_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "bot", "locales")
expected_locales = ["en", "ar", "fa", "dar", "zh", "tr", "fr", "es", "ru"]
required_keys = ["welcome", "help", "latest_header", "shelter_header", "language_set", "about", "disclaimer", "error"]

for lang in expected_locales:
    filepath = os.path.join(locales_dir, f"{lang}.json")
    exists = os.path.isfile(filepath)
    test(f"Locale {lang}.json exists", exists)
    
    if exists:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in required_keys:
            has_key = key in data and len(data[key]) > 0
            if not has_key:
                test(f"  {lang}.json has '{key}'", False, f"Missing or empty")

# ============================================================
# MODULE 9: SAMPLE DATA
# ============================================================
section("MODULE 9: SAMPLE DATA (data/)")

sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_reports")
for i in range(1, 4):
    filepath = os.path.join(sample_dir, f"sample_{i}.json")
    exists = os.path.isfile(filepath)
    test(f"sample_{i}.json exists", exists)
    if exists:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        test(f"  sample_{i} has required fields", 
             all(k in data for k in ["title", "date", "source", "url", "text"]))
        test(f"  sample_{i} URL is valid", data["url"].startswith("https://"))
        test(f"  sample_{i} text is substantial", len(data["text"]) > 100,
             f"Text length: {len(data['text'])}")

# ============================================================
# FINAL SUMMARY
# ============================================================
section("FINAL SUMMARY")

total = len(results)
passed = sum(1 for r in results if r["passed"])
failed = sum(1 for r in results if not r["passed"])

print(f"\n  Total tests: {total}")
print(f"  Passed:      {passed}")
print(f"  Failed:      {failed}")
print(f"  Pass rate:   {passed/total*100:.1f}%")

if failed > 0:
    print(f"\n  FAILED TESTS:")
    for r in results:
        if not r["passed"]:
            print(f"    - {r['name']}: {r['detail']}")

print(f"\n  {'AUDIT PASSED' if failed == 0 else 'AUDIT FAILED'}")
print(f"  Date: {datetime.utcnow().isoformat()}")

sys.exit(0 if failed == 0 else 1)
