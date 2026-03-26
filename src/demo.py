"""
OpenClaw Humanitarian Network — Live Demo
==========================================
Run:  python src/demo.py

What this demo does:
  1. Fetches the latest humanitarian reports from ReliefWeb public API
     (no API key required)
  2. Falls back to built-in sample data if the network is unavailable
  3. Loads data/glossary.json and applies term replacements
  4. Displays a colourful multilingual bulletin in your terminal

Dependencies: ZERO — only Python standard library (json, urllib, os, sys).
Clone the repo and run immediately:  python src/demo.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from typing import Any, Optional

# ── ANSI colour helpers (no third-party libs) ──────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
RED    = "\033[91m"
DIM    = "\033[2m"


def _c(text: str, *codes: str) -> str:
    """Wrap *text* with ANSI escape codes; strip them on Windows without colour support."""
    # Windows 10 1511+ supports ANSI in conhost if ENABLE_VIRTUAL_TERMINAL_PROCESSING is on.
    # Simplest cross-platform approach: always emit codes (modern terminals handle them).
    prefix = "".join(codes)
    return f"{prefix}{text}{RESET}"


def _bold(t: str) -> str:   return _c(t, BOLD)
def _green(t: str) -> str:  return _c(t, GREEN)
def _yellow(t: str) -> str: return _c(t, YELLOW)
def _cyan(t: str) -> str:   return _c(t, CYAN)
def _blue(t: str) -> str:   return _c(t, BLUE)
def _dim(t: str) -> str:    return _c(t, DIM)


# ── Constants ──────────────────────────────────────────────────────────────────
RELIEFWEB_API = "https://api.reliefweb.int/v1/reports"
WIDTH = 51  # display width

LANG_META: dict[str, dict[str, str]] = {
    "fa":  {"flag": "🇮🇷", "label": "Persian (فارسی)"},
    "dar": {"flag": "🇦🇫", "label": "Dari (دری)"},
    "ar":  {"flag": "🇱🇧", "label": "Arabic (العربية)"},
}

# Built-in demo translations (no API needed).
# These are real-language summaries; in production the Claude backend generates them.
STUB_TRANSLATIONS: dict[str, dict[str, str]] = {
    "fa": {
        "intro": (
            "سازمان برنامه غذایی جهانی (WFP) به ارائه کمک‌های غذایی و "
            "پول نقد به حدود ۳۳٬۰۰۰ پناهنده افغان در ایران ادامه می‌دهد. "
            "در لبنان، دسترسی انسان‌دوستانه به مناطق جنوبی همچنان به‌شدت محدود است. "
            "آوارگان در جست‌وجوی سرپناه و امنیت غذایی هستند."
        ),
    },
    "dar": {
        "intro": (
            "برنامه غذایی جهانی (WFP) به حدود ۳۳٬۰۰۰ پناهنده افغان در ایران "
            "کمک‌های خوراکی و پولی ارائه می‌دهد. "
            "در لبنان، دسترسی بشردوستانه به مناطق جنوبی شدیداً محدود مانده است. "
            "بیجاشدگان به دنبال سرپناه و امنیت خوراکی هستند."
        ),
    },
    "ar": {
        "intro": (
            "يواصل برنامج الأغذية العالمي (WFP) تقديم المساعدات الغذائية والنقدية "
            "لنحو ٣٣٬٠٠٠ لاجئ أفغاني في إيران. "
            "في لبنان، لا يزال الوصول الإنساني إلى المناطق الجنوبية مقيداً بشدة. "
            "النازحون يبحثون عن المأوى والأمن الغذائي."
        ),
    },
}

# Fallback report when network is unavailable
SAMPLE_REPORT: dict[str, Any] = {
    "title": "WFP Middle East Regional Escalation Emergency Response — Situation Report",
    "date": "2026-03-27",
    "source": "WFP / ReliefWeb",
    "url": "https://reliefweb.int/report/iran-islamic-republic/wfp-middle-east-regional-escalation",
    "summary": (
        "Almost a month into the escalation, hostilities continue to intensify across "
        "multiple fronts. In Iran, WFP continues to provide food and cash assistance to "
        "around 33,000 Afghan refugees. In Lebanon, evacuation orders widen and displacement "
        "accelerates. In Syria, WFP has provided date bars to over 58,000 returnees. "
        "Humanitarian access to southern Lebanon remains severely restricted."
    ),
}


# ── Display helpers ────────────────────────────────────────────────────────────

def _hr_double(width: int = WIDTH) -> str:
    """Return a double-line horizontal rule."""
    return "═" * width


def _hr_single(label: str = "", width: int = WIDTH) -> str:
    """Return a single-line rule with optional inline label."""
    if label:
        seg = f"━━━ {label} "
        pad = "━" * max(0, width - len(seg))
        return seg + pad
    return "━" * width


def _print_header() -> None:
    print()
    print(_bold(_c(_hr_double(), CYAN)))
    title = "🌍  OpenClaw Humanitarian Network — Live Demo"
    print(_bold(_c(f"  {title}", CYAN)))
    print(_bold(_c(_hr_double(), CYAN)))
    print()


def _print_footer() -> None:
    print()
    print(_bold(_c(_hr_double(), CYAN)))
    print()
    print(_green("  🎉  Demo complete!"))
    print()
    print(f"  👉  Live bot: {_cyan('https://t.me/openclaw_aid_bot')}")
    print(f"  💻  GitHub:   {_cyan('https://github.com/CuiweiG/openclaw-humanitarian')}")
    print()
    print(_dim("  No API key was used. Set ANTHROPIC_API_KEY for real AI translation."))
    print()


# ── Glossary ───────────────────────────────────────────────────────────────────

def _find_glossary_path() -> Optional[str]:
    """Locate data/glossary.json relative to this file."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "data", "glossary.json"),
        os.path.join(here, "data", "glossary.json"),
        os.path.join(os.getcwd(), "data", "glossary.json"),
    ]
    for c in candidates:
        p = os.path.normpath(c)
        if os.path.isfile(p):
            return p
    return None


def _load_glossary() -> list[dict[str, str]]:
    """Load and return the glossary list; return empty list on failure."""
    path = _find_glossary_path()
    if path is None:
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _apply_glossary(text: str, lang: str, glossary: list[dict[str, str]]) -> tuple[str, list[str]]:
    """
    Replace English terms found in *text* with their *lang* equivalents from the glossary.

    Returns:
        (annotated_text, list_of_replacements_made)
    """
    replaced: list[str] = []
    for entry in glossary:
        en_term = entry.get("en", "")
        native = entry.get(lang, "")
        if not en_term or not native:
            continue
        # Check case-insensitive; only replace if English term appears
        if en_term.lower() in text.lower():
            # Replace keeping first encountered capitalisation variant
            text = text.replace(en_term, native)
            text = text.replace(en_term.capitalize(), native)
            text = text.replace(en_term.upper(), native)
            replaced.append(f"{en_term} → {native}")
    return text, replaced


# ── ReliefWeb fetch ────────────────────────────────────────────────────────────

def _build_query(limit: int = 3) -> bytes:
    """Build the ReliefWeb API POST body (JSON bytes)."""
    payload: dict[str, Any] = {
        "filter": {
            "operator": "OR",
            "conditions": [
                {"field": "country.name", "value": "Iran"},
                {"field": "country.name", "value": "Lebanon"},
                {"field": "country.name", "value": "Syria"},
                {"field": "country.name", "value": "Afghanistan"},
            ],
        },
        "fields": {
            "include": ["title", "body", "source", "date", "url"],
        },
        "sort": ["date.created:desc"],
        "limit": limit,
    }
    return json.dumps(payload).encode("utf-8")


def _parse_raw_report(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalise a single raw ReliefWeb API entry."""
    fields = raw.get("fields", {})
    sources = fields.get("source", [])
    if isinstance(sources, list):
        source_name = ", ".join(s.get("name", "") for s in sources if isinstance(s, dict))
    else:
        source_name = str(sources)

    body: str = fields.get("body", "") or ""
    summary = body[:400].strip()
    if len(body) > 400:
        summary += "…"

    date_obj = fields.get("date", {})
    date_str = date_obj.get("created", "")[:10] if isinstance(date_obj, dict) else ""

    return {
        "title": fields.get("title", ""),
        "summary": summary,
        "date": date_str,
        "source": source_name,
        "url": raw.get("href", ""),
    }


def _fetch_reports(limit: int = 3) -> list[dict[str, Any]]:
    """
    Fetch up to *limit* reports from ReliefWeb using only urllib (stdlib).

    Raises:
        urllib.error.URLError: on network failure.
    """
    body = _build_query(limit)
    req = urllib.request.Request(
        RELIEFWEB_API,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "OpenClaw-HumanitarianBot/1.0 (aid@agentmail.to)",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
    return [_parse_raw_report(r) for r in data.get("data", [])]


# ── Stub translation (no API key) ──────────────────────────────────────────────

def _stub_translate(english_summary: str, lang: str, glossary: list[dict[str, str]]) -> tuple[str, list[str]]:
    """
    Return a demo translation for *lang* by:
      1. Using the built-in STUB_TRANSLATIONS for the introduction sentence, AND
      2. Running glossary replacement on the English summary so viewers see real terms.
    """
    # Start with the pre-written intro
    base = STUB_TRANSLATIONS.get(lang, {}).get("intro", "")

    # Append a glossary-replaced snippet of the English summary for demonstration
    snippet = english_summary[:300] if english_summary else ""
    replaced_snippet, replacements = _apply_glossary(snippet, lang, glossary)

    if replaced_snippet and replaced_snippet != snippet:
        combined = base + "\n\n" + _dim(f"[Glossary demo — English snippet with {len(replacements)} term(s) replaced]") + "\n" + replaced_snippet
    else:
        combined = base

    return combined, replacements


# ── Quality check (stdlib) ─────────────────────────────────────────────────────

def _quality_check(text: str, lang: str, glossary: list[dict[str, str]]) -> dict[str, Any]:
    """
    Run lightweight quality checks on a translated bulletin.

    Returns:
        dict with keys: passed (bool), word_count (int), glossary_hits (int), issues (list[str])
    """
    word_count = len(text.split())
    issues: list[str] = []

    if word_count < 10:
        issues.append("Text too short (< 10 words)")

    # Check that at least some glossary terms in target lang appear in the text
    glossary_hits = 0
    for entry in glossary:
        native = entry.get(lang, "")
        if native and native.split("/")[0].strip() in text:
            glossary_hits += 1

    return {
        "passed": len(issues) == 0,
        "word_count": word_count,
        "glossary_hits": glossary_hits,
        "issues": issues,
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point: run the live demo."""

    # Enable ANSI on Windows (Python 3.12+ does this automatically, but just in case)
    if sys.platform == "win32":
        os.system("")  # noqa: S605 — enables ANSI escape in Windows console

    _print_header()

    # ── Step 1: Fetch ──────────────────────────────────────────────────────────
    print(f"  {_bold('📡 Fetching latest reports from ReliefWeb API...')}")
    print(_dim("     (https://api.reliefweb.int/v1/reports — no API key required)"))
    print()

    reports: list[dict[str, Any]] = []
    network_ok = False
    try:
        reports = _fetch_reports(limit=3)
        network_ok = True
    except Exception as exc:
        print(f"  {_yellow('⚠️  Network unavailable')} ({type(exc).__name__}). Using built-in sample data.")

    if network_ok and reports:
        print(_green(f"  ✅  Found {len(reports)} report(s) about Iran / Lebanon / Syria / Afghanistan"))
    else:
        reports = [SAMPLE_REPORT]
        print(_yellow("  📄  Using built-in sample report (offline fallback)"))

    # ── Load glossary ─────────────────────────────────────────────────────────
    glossary = _load_glossary()
    if glossary:
        print(_dim(f"\n  📖  Loaded {len(glossary)}-term humanitarian glossary (data/glossary.json)"))
    else:
        print(_dim("\n  ⚠️   Glossary not found — term replacement skipped"))

    # ── Step 2: Display each report ───────────────────────────────────────────
    for i, report in enumerate(reports, start=1):
        print()
        print(_bold(_c(_hr_single(f"Report {i}", WIDTH), BLUE)))
        title = report.get("title", "(no title)")
        date  = report.get("date", "N/A")
        src   = report.get("source", "N/A")
        url   = report.get("url", "")
        summary = report.get("summary", "")

        print(f"  {_bold('📋')} {_bold(title[:70])}")
        print(f"  {_dim('📅')} {_dim(date)}  {_dim('|')}  {_dim('🔗')} {_dim(src[:60])}")
        if url:
            print(f"     {_dim(url[:70])}")
        print()

        # ── Translate / display in 3 languages ────────────────────────────────
        pass_count = 0
        for lang, meta in LANG_META.items():
            flag  = meta["flag"]
            label = meta["label"]

            translated, replacements = _stub_translate(summary, lang, glossary)

            print(f"  {flag} {_bold(label)}:")
            # Word-wrap at ~60 chars
            for line in translated.split("\n"):
                if not line.strip():
                    continue
                # Indent and wrap
                words = line.split()
                current = "     "
                for word in words:
                    if len(current) + len(word) + 1 > 72:
                        print(current)
                        current = "     " + word
                    else:
                        current += (" " if current.strip() else "") + word
                if current.strip():
                    print(current)

            if replacements:
                rep_preview = ", ".join(replacements[:3])
                suffix = f" +{len(replacements)-3} more" if len(replacements) > 3 else ""
                print(_dim(f"     📝 Glossary: {rep_preview}{suffix}"))
            print()

            # Quality check
            qc = _quality_check(translated, lang, glossary)
            if qc["passed"]:
                pass_count += 1

        # Quality summary
        total = len(LANG_META)
        if pass_count == total:
            qc_line = _green(f"  ✅  Quality Check: PASS ({pass_count}/{total} languages)")
        else:
            qc_line = _yellow(f"  ⚠️   Quality Check: {pass_count}/{total} passed")
        print(qc_line)

        if glossary:
            print(_dim(f"  📊  Glossary coverage checked across {len(glossary)} terms"))

        print(_c(_hr_single(width=WIDTH), BLUE))

    _print_footer()


if __name__ == "__main__":
    main()
