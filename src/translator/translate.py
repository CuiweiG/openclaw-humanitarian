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
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 默认 glossary 路径（相对于项目根目录）/ Default glossary path
DEFAULT_GLOSSARY_PATH = Path(__file__).parent.parent.parent / "data" / "glossary.json"

# 支持的目标语言列表 / Supported target language codes
SUPPORTED_LANGUAGES: list[str] = ["fa", "dar", "ar", "zh", "tr", "en"]

# 语言显示名称（用于 Markdown 标题）/ Display names for Markdown headers
LANGUAGE_DISPLAY: dict[str, str] = {
    "fa":  "🇮🇷 Persian (فارسی)",
    "dar": "🇦🇫 Dari (دری)",
    "ar":  "🇱🇧 Arabic (العربية)",
    "zh":  "🇨🇳 Chinese (中文)",
    "tr":  "🇹🇷 Turkish (Türkçe)",
    "en":  "🇬🇧 English",
}


# ──────────────────────────────────────────
# 可插拔翻译后端 / Pluggable translation backends
# ──────────────────────────────────────────

class TranslationBackend(ABC):
    """翻译后端抽象基类 / Abstract base class for translation backends."""

    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        """
        翻译文本到目标语言。
        Translate text to the target language.

        Args:
            text: 源语言（英文）文本。
            target_lang: 目标语言代码（如 'fa', 'ar'）。

        Returns:
            翻译后的文本字符串。
        """
        ...


class ClaudeBackend(TranslationBackend):
    """
    使用 Anthropic Claude API 进行翻译。
    Translation backend using the Anthropic Claude API.

    需要环境变量 ANTHROPIC_API_KEY。
    Requires the ANTHROPIC_API_KEY environment variable.
    """

    def __init__(self, model: str = "claude-3-5-haiku-20241022") -> None:
        """
        初始化 Claude 后端。
        Initialise the Claude backend.

        Args:
            model: 使用的 Claude 模型名称。
        """
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

    def translate(self, text: str, target_lang: str) -> str:
        """
        使用 Claude API 翻译文本。
        Translate text using the Claude API.
        """
        lang_names = {
            "fa": "Persian (Farsi)",
            "dar": "Dari",
            "ar": "Modern Standard Arabic",
            "zh": "Simplified Chinese",
            "tr": "Turkish",
        }
        lang_name = lang_names.get(target_lang, target_lang)

        prompt = (
            f"You are a professional humanitarian translator. "
            f"Translate the following English humanitarian bulletin into {lang_name}. "
            f"Keep it under 200 words. Be accurate, neutral, and use appropriate "
            f"humanitarian terminology. Output only the translation, no commentary.\n\n"
            f"{text}"
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()


class StubBackend(TranslationBackend):
    """
    占位翻译后端（用于测试）。
    Stub translation backend for testing without a real API.
    """

    def translate(self, text: str, target_lang: str) -> str:
        """返回带语言标记的原文（仅供测试）/ Return tagged source text (testing only)."""
        return f"[{target_lang.upper()} TRANSLATION PLACEHOLDER]\n{text}"


# ──────────────────────────────────────────
# Glossary 工具 / Glossary utilities
# ──────────────────────────────────────────

def load_glossary(path: Path = DEFAULT_GLOSSARY_PATH) -> list[dict]:
    """
    从 JSON 文件加载术语表。
    Load the terminology glossary from a JSON file.

    Args:
        path: glossary.json 文件路径。

    Returns:
        术语表列表 / List of glossary entry dicts.
    """
    if not path.exists():
        logger.warning("Glossary file not found at %s. Continuing without it.", path)
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_glossary_consistency(
    translated_text: str,
    target_lang: str,
    glossary: list[dict],
) -> list[str]:
    """
    检查翻译文本中是否使用了 glossary 规定的标准术语。
    Check whether the translated text uses glossary-approved terminology.

    Args:
        translated_text: 翻译后的文本。
        target_lang: 目标语言代码。
        glossary: 术语表列表。

    Returns:
        发现的不一致术语列表（空列表表示通过）/ List of inconsistency notes (empty = pass).
    """
    issues: list[str] = []
    for entry in glossary:
        en_term = entry.get("en", "")
        preferred = entry.get(target_lang, "")
        if not preferred:
            continue
        # 如果英文术语出现在翻译中，警告（翻译应使用目标语言术语）
        if en_term.lower() in translated_text.lower():
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
    """
    将英文人道主义简报翻译成多语言 Markdown 文档。
    Translate an English humanitarian bulletin into a multi-language Markdown document.

    Args:
        english_text: 源英文文本。
        target_languages: 目标语言代码列表，如 ['fa', 'ar', 'zh']。
        backend: 翻译后端实例；默认使用 StubBackend。
        glossary_path: glossary.json 文件路径。
        source_url: 原始报告的 URL（用于来源标注）。
        report_date: 报告日期字符串（用于文档头部）。

    Returns:
        Markdown 格式的多语言简报字符串。
    """
    if backend is None:
        logger.warning("No translation backend provided. Using StubBackend (testing mode).")
        backend = StubBackend()

    # 1. 加载术语表 / Load glossary
    glossary = load_glossary(glossary_path)
    logger.info("Loaded %d glossary entries.", len(glossary))

    # 2. 过滤有效语言 / Filter valid languages
    valid_langs = [lang for lang in target_languages if lang in SUPPORTED_LANGUAGES]
    if not valid_langs:
        raise ValueError(f"No valid target languages. Supported: {SUPPORTED_LANGUAGES}")

    # 3. 构建 Markdown 输出 / Build Markdown output
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
            # 英文直接输出，不翻译 / English passthrough
            translated = english_text
        else:
            try:
                translated = backend.translate(english_text, lang)
            except Exception as exc:
                logger.error("Translation to '%s' failed: %s", lang, exc)
                translated = f"[Translation failed: {exc}]"

        # 后处理：验证术语一致性 / Post-process: check terminology
        issues = check_glossary_consistency(translated, lang, glossary)
        if issues:
            logger.warning(
                "Glossary inconsistencies for '%s': %s", lang, issues
            )

        lines.append(translated)
        lines.append("")

        # 来源标注 / Source attribution
        if source_url:
            lines.append(f"*Source: {source_url}*")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # 快速冒烟测试 / Quick smoke test
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
