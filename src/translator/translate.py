"""
translate.py — 多语言翻译管线
Multilingual translation pipeline for humanitarian bulletins.

流程 / Pipeline:
  1. 加载 glossary.json / Load glossary.json
  2. 调用翻译后端（Claude API 或本地模型）/ Call translation backend (Claude API or local model)
  3. 后处理：用 glossary 验证术语一致性 / Post-process: validate terminology against glossary
  4. 输出 Markdown 格式多语言简报 / Output multi-language Markdown bulletin

支持的语言 / Supported languages:
  fa  — Persian (Farsi / فارسی)
  dar — Dari (دری)
  ar  — Arabic (العربية)
  zh  — Chinese (中文)
  tr  — Turkish (Türkçe)
  en  — English (passthrough, no translation)
"""

import json
import logging
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 默认 glossary 路径（相对于项目根目录）/ Default glossary path
DEFAULT_GLOSSARY_PATH = Path(__file__).parent.parent.parent / "data" / "glossary.json"

# 支持的目标语言列表 / Supported target language codes
SUPPORTED_LANGUAGES: list[str] = ["fa", "dar", "ar", "zh", "tr", "en", "fr", "es", "ru", "ps", "ku"]

# 语言显示名称（用于 Markdown 标题）/ Display names for Markdown headers
LANGUAGE_DISPLAY: dict[str, str] = {
    "fa":  "🇮🇷 Persian (فارسی)",
    "dar": "🇦🇫 Dari (دری)",
    "ar":  "🇱🇧 Arabic (العربية)",
    "zh":  "🇨🇳 Chinese (中文)",
    "tr":  "🇹🇷 Turkish (Türkçe)",
    "en":  "🇬🇧 English",
    "fr":  "🇫🇷 French (Français)",
    "es":  "🇪🇸 Spanish (Español)",
    "ru":  "🇷🇺 Russian (Русский)",
    "ps":  "🇦🇫 Pashto (پښتو)",
    "ku":  "Kurdish Kurmanji (Kurdî)",
}


# ──────────────────────────────────────────
# 可插拔翻译后端 / Pluggable translation backends
# ──────────────────────────────────────────

class TranslationBackend(ABC):
    """翻译后端抽象基类 / Abstract base class for translation backends."""

    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        ...


class ClaudeBackend(TranslationBackend):
    """
    使用 Anthropic Claude API 进行翻译。
    Translation backend using the Anthropic Claude API.
    """

    def __init__(self, model: str = "claude-3-5-haiku-20241022") -> None:
        self.model = model
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please set it before using ClaudeBackend."
            )
        try:
            import anthropic  # type: ignore
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError as exc:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            ) from exc

    def translate(self, text: str, target_lang: str, glossary: list[dict] = None) -> str:
        """Translate text using the Claude API with glossary constraints."""
        lang_names = {
            "fa": "Persian (Farsi)",
            "dar": "Dari",
            "ar": "Modern Standard Arabic",
            "zh": "Simplified Chinese",
            "tr": "Turkish",
        }
        lang_name = lang_names.get(target_lang, target_lang)

        # Build glossary constraints for the prompt
        glossary_block = ""
        if glossary:
            constraints = []
            for entry in glossary:
                en_term = entry.get("en", "")
                native = entry.get(target_lang, "")
                if en_term and native:
                    constraints.append(f"  {en_term} → {native}")
            if constraints:
                glossary_block = (
                    "\n\nMANDATORY terminology — use these exact translations:\n"
                    + "\n".join(constraints[:30])
                    + "\n"
                )

        prompt = (
            f"You are a professional humanitarian translator. "
            f"Translate the following English humanitarian bulletin into {lang_name}. "
            f"Keep it under 200 words. Be accurate, neutral, and use appropriate "
            f"humanitarian terminology. Output only the translation, no commentary."
            f"{glossary_block}\n\n"
            f"{text}"
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()


class StubBackend(TranslationBackend):
    """占位翻译后端（用于测试）/ Stub backend for testing without a real API."""

    def translate(self, text: str, target_lang: str) -> str:
        return f"[{target_lang.upper()} TRANSLATION PLACEHOLDER]\n{text}"


# ──────────────────────────────────────────
# Glossary 工具 / Glossary utilities
# ──────────────────────────────────────────

def load_glossary(path: Path = DEFAULT_GLOSSARY_PATH) -> list[dict]:
    if not path.exists():
        logger.warning("Glossary file not found at %s. Continuing without it.", path)
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# Languages that use non-Latin scripts where \b word boundaries are unreliable
_NON_LATIN_LANGS = {"fa", "dar", "ar", "zh", "ps", "ku"}


def _term_pattern(term: str, target_lang: str) -> re.Pattern:
    """
    Build a regex pattern for matching a glossary term in translated text.

    For Latin-script languages (en, fr, es, tr, ru) standard \\b word
    boundaries work correctly.  For Arabic-script and CJK languages the
    \\b anchor is unreliable because the regex engine treats every
    non-ASCII character as a non-word character.  We fall back to
    whitespace-or-boundary anchoring instead.
    """
    escaped = re.escape(term)
    if target_lang in _NON_LATIN_LANGS:
        # Match term preceded/followed by whitespace, punctuation, or string edge
        return re.compile(
            r'(?:^|(?<=[\s\u200c\u200b.,;:!?()\[\]{}"\'/«»]))'
            + escaped
            + r'(?=$|[\s\u200c\u200b.,;:!?()\[\]{}"\'/«»])',
            re.IGNORECASE,
        )
    return re.compile(r'\b' + escaped + r'\b', re.IGNORECASE)


def check_glossary_consistency(
    translated_text: str,
    target_lang: str,
    glossary: list[dict],
) -> list[str]:
    """
    Check whether the translated text uses glossary-approved terminology.

    Uses Unicode-aware boundary matching for non-Latin scripts (Arabic,
    Persian, Dari, Chinese) to avoid false negatives caused by \\b
    treating all non-ASCII characters as non-word characters.
    """
    issues: list[str] = []
    for entry in glossary:
        en_term = entry.get("en", "")
        preferred = entry.get(target_lang, "")
        if not preferred:
            continue
        pattern = _term_pattern(en_term, target_lang)
        if pattern.search(translated_text):
            issues.append(
                f"English term '{en_term}' found in {target_lang} translation. "
                f"Expected: '{preferred}'"
            )
    return issues


# ──────────────────────────────────────────
# 主翻译函数 / Main translation function
# ──────────────────────────────────────────

def translate_bulletin(
    english_text: str,
    target_languages: list[str],
    backend: Optional[TranslationBackend] = None,
    glossary_path: Path = DEFAULT_GLOSSARY_PATH,
    source_url: str = "",
    report_date: str = "",
) -> str:
    """Translate an English humanitarian bulletin into a multi-language Markdown document."""
    if backend is None:
        logger.warning("No translation backend provided. Using StubBackend (testing mode).")
        backend = StubBackend()

    glossary = load_glossary(glossary_path)
    logger.info("Loaded %d glossary entries.", len(glossary))

    valid_langs = [lang for lang in target_languages if lang in SUPPORTED_LANGUAGES]
    if not valid_langs:
        raise ValueError(f"No valid target languages. Supported: {SUPPORTED_LANGUAGES}")

    lines: list[str] = [
        "# 🌍 CrisisBridge Bulletin",
        "",
        f"**Date:** {report_date or 'N/A'}",
        f"**Source:** {source_url or 'N/A'}",
        "",
        "---",
        "",
    ]

    for lang in valid_langs:
        display = LANGUAGE_DISPLAY.get(lang, lang.upper())
        lines.append(f"## {display}")
        lines.append("")

        if lang == "en":
            translated = english_text
        else:
            try:
                if isinstance(backend, ClaudeBackend):
                    translated = backend.translate(english_text, lang, glossary=glossary)
                else:
                    translated = backend.translate(english_text, lang)
            except Exception as exc:
                logger.error("Translation to '%s' failed: %s", lang, exc)
                translated = f"[Translation failed: {exc}]"

        issues = check_glossary_consistency(translated, lang, glossary)
        if issues:
            logger.warning("Glossary inconsistencies for '%s': %s", lang, issues)

        lines.append(translated)
        lines.append("")

        if source_url:
            lines.append(f"*Source: {source_url}*")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    sample_text = (
        "Nearly one month into the escalation, WFP is providing food assistance "
        "to approximately 33,000 Afghan refugees in Iran. In Lebanon, humanitarian "
        "access to southern areas remains severely restricted."
    )
    result = translate_bulletin(
        english_text=sample_text,
        target_languages=["fa", "ar", "zh", "en"],
        source_url="https://reliefweb.int/report/example",
        report_date="2026-03-27",
    )
    print(result)
