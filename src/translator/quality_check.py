"""
quality_check.py — 翻译质量检查模块
Translation quality checker for humanitarian bulletins.

检查项目 / Checks performed:
  1. 术语一致性（对比 glossary.json）/ Terminology consistency (vs glossary.json)
  2. 文本长度 ≤200 字 / Text length ≤ 200 words
  3. 来源标注完整性 / Source attribution completeness
  4. 数字格式正确性（波斯语 ۱۲۳ vs 阿拉伯语 ١٢٣）/ Numeric format correctness
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .translate import DEFAULT_GLOSSARY_PATH, load_glossary

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# 数字格式正则 / Numeric format patterns
# ──────────────────────────────────────────

# 波斯语/扩展阿拉伯数字（波斯语专用）/ Persian (Extended Arabic) digits: ۰-۹
PERSIAN_DIGIT_PATTERN = re.compile(r"[۰-۹]")

# 阿拉伯语印度数字 / Arabic-Indic digits: ٠-٩
ARABIC_INDIC_DIGIT_PATTERN = re.compile(r"[٠-٩]")

# 西方阿拉伯数字（普通 0-9）/ Western Arabic digits
WESTERN_DIGIT_PATTERN = re.compile(r"\d")

# URL 匹配（用于来源检查）/ URL pattern for source check
URL_PATTERN = re.compile(r"https?://\S+")

# Source 行匹配（Markdown 格式）/ Source line pattern in Markdown
SOURCE_LINE_PATTERN = re.compile(r"\*Source:\s*https?://\S+\*")


@dataclass
class CheckResult:
    """
    单项检查结果。
    Result of a single quality check.
    """
    check_name: str
    passed: bool
    message: str
    severity: str = "warning"  # "info" | "warning" | "error"


@dataclass
class QualityReport:
    """
    完整的质量检查报告。
    Full quality check report for a translated bulletin.
    """
    language: str
    text: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """所有错误级别检查均通过时返回 True / True if no error-level checks failed."""
        return all(c.passed for c in self.checks if c.severity == "error")

    @property
    def warnings(self) -> list[CheckResult]:
        """警告列表 / List of warning-level failures."""
        return [c for c in self.checks if not c.passed and c.severity == "warning"]

    def to_markdown(self) -> str:
        """
        将报告格式化为 Markdown 字符串。
        Format the report as a Markdown string.
        """
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines = [
            f"### Quality Report — `{self.language}` {status}",
            "",
        ]
        for c in self.checks:
            icon = "✅" if c.passed else ("⚠️" if c.severity == "warning" else "❌")
            lines.append(f"- {icon} **{c.check_name}**: {c.message}")
        lines.append("")
        return "\n".join(lines)


# ──────────────────────────────────────────
# 各项检查函数 / Individual check functions
# ──────────────────────────────────────────

def check_word_count(text: str, max_words: int = 200) -> CheckResult:
    """
    检查文本长度是否在允许范围内（≤200 字）。
    Check whether the text length is within the allowed limit (≤200 words).

    Args:
        text: 待检查的翻译文本。
        max_words: 最大允许词数。

    Returns:
        CheckResult 实例。
    """
    word_count = len(text.split())
    passed = word_count <= max_words
    return CheckResult(
        check_name="Word Count",
        passed=passed,
        message=(
            f"{word_count} words (limit: {max_words})"
            if passed
            else f"{word_count} words — EXCEEDS limit of {max_words}"
        ),
        severity="warning",
    )


def check_source_attribution(text: str) -> CheckResult:
    """
    检查文本中是否包含来源标注（Markdown `*Source: URL*` 格式）。
    Check whether the text includes a source attribution line.

    Args:
        text: 待检查的翻译文本。

    Returns:
        CheckResult 实例。
    """
    has_source = bool(SOURCE_LINE_PATTERN.search(text))
    return CheckResult(
        check_name="Source Attribution",
        passed=has_source,
        message=(
            "Source attribution found."
            if has_source
            else "Missing source attribution. Add `*Source: <URL>*` line."
        ),
        severity="error",
    )


def check_terminology(
    text: str,
    language: str,
    glossary: list[dict],
) -> CheckResult:
    """
    检查翻译文本中是否出现了未翻译的英文术语（应使用 glossary 对应词）。
    Check whether untranslated English terms appear (should use glossary equivalents).

    Args:
        text: 翻译后文本。
        language: 目标语言代码（如 'fa'）。
        glossary: 术语表列表。

    Returns:
        CheckResult 实例。
    """
    issues: list[str] = []
    for entry in glossary:
        en_term = entry.get("en", "").lower()
        preferred = entry.get(language, "")
        if not preferred or not en_term:
            continue
        # 检测英文术语是否遗留在翻译文本中 / Detect English term left in translation
        if re.search(r"\b" + re.escape(en_term) + r"\b", text.lower()):
            issues.append(f"'{en_term}' → expected '{preferred}'")

    passed = len(issues) == 0
    return CheckResult(
        check_name="Terminology Consistency",
        passed=passed,
        message=(
            "All glossary terms correctly translated."
            if passed
            else f"Found {len(issues)} untranslated term(s): {'; '.join(issues[:3])}"
              + (" …" if len(issues) > 3 else "")
        ),
        severity="warning",
    )


def check_numeric_format(text: str, language: str) -> CheckResult:
    """
    检查数字格式是否符合目标语言规范。
    Check that numeric format matches the target language convention.

    规则 / Rules:
    - Persian (fa/dar): 应使用扩展阿拉伯数字 ۰-۹，或西方数字均可（但不应混有阿拉伯印度数字）
    - Arabic (ar): 应使用阿拉伯印度数字 ٠-٩，或西方数字均可（但不应混有波斯数字）
    - 其他语言：使用西方数字即可

    Args:
        text: 翻译后文本。
        language: 目标语言代码。

    Returns:
        CheckResult 实例。
    """
    persian_digits = PERSIAN_DIGIT_PATTERN.findall(text)
    arabic_indic_digits = ARABIC_INDIC_DIGIT_PATTERN.findall(text)

    if language in ("fa", "dar"):
        # 波斯语不应包含阿拉伯印度数字 / Persian should not contain Arabic-Indic digits
        if arabic_indic_digits:
            return CheckResult(
                check_name="Numeric Format",
                passed=False,
                message=(
                    f"Found {len(arabic_indic_digits)} Arabic-Indic digit(s) (٠-٩) "
                    f"in Persian text. Use Persian digits (۰-۹) or Western (0-9)."
                ),
                severity="warning",
            )
    elif language == "ar":
        # 阿拉伯语不应包含波斯数字 / Arabic should not contain Persian digits
        if persian_digits:
            return CheckResult(
                check_name="Numeric Format",
                passed=False,
                message=(
                    f"Found {len(persian_digits)} Persian digit(s) (۰-۹) "
                    f"in Arabic text. Use Arabic-Indic digits (٠-٩) or Western (0-9)."
                ),
                severity="warning",
            )

    return CheckResult(
        check_name="Numeric Format",
        passed=True,
        message="Numeric format looks correct.",
        severity="info",
    )


# ──────────────────────────────────────────
# 主检查入口 / Main check entry point
# ──────────────────────────────────────────

def quality_check(
    translated_text: str,
    language: str,
    glossary_path: Path = DEFAULT_GLOSSARY_PATH,
    max_words: int = 200,
) -> QualityReport:
    """
    对翻译文本执行全套质量检查，返回检查报告。
    Run all quality checks on a translated text and return a report.

    Args:
        translated_text: 翻译后的完整文本（含来源标注）。
        language: 目标语言代码（如 'fa', 'ar', 'zh'）。
        glossary_path: glossary.json 路径。
        max_words: 最大词数限制。

    Returns:
        QualityReport 实例，包含所有检查结果。
    """
    glossary = load_glossary(glossary_path)

    report = QualityReport(language=language, text=translated_text)

    # 逐项检查 / Run each check
    report.checks.append(check_word_count(translated_text, max_words))
    report.checks.append(check_source_attribution(translated_text))
    report.checks.append(check_terminology(translated_text, language, glossary))
    report.checks.append(check_numeric_format(translated_text, language))

    overall = "PASSED" if report.passed else "FAILED"
    logger.info("Quality check for '%s': %s", language, overall)

    return report


def check_bulletin(
    bulletin_markdown: str,
    languages: list[str],
    glossary_path: Path = DEFAULT_GLOSSARY_PATH,
) -> list[QualityReport]:
    """
    对多语言 Markdown 简报中每个语言段落分别进行质量检查。
    Run quality checks on each language section of a multi-language Markdown bulletin.

    Args:
        bulletin_markdown: translate_bulletin() 输出的完整 Markdown 字符串。
        languages: 要检查的语言代码列表。
        glossary_path: glossary.json 路径。

    Returns:
        每个语言的 QualityReport 列表。
    """
    # 简单按语言 header 切割 / Split by language section headers
    reports: list[QualityReport] = []
    for lang in languages:
        # 在 Markdown 中寻找该语言的段落
        # Find this language's section in the Markdown
        section_pattern = re.compile(
            rf"## [^\n]*?({re.escape(lang.upper())}|{re.escape(lang)})[^\n]*\n(.*?)(?=\n## |\Z)",
            re.DOTALL | re.IGNORECASE,
        )
        match = section_pattern.search(bulletin_markdown)
        section_text = match.group(2).strip() if match else bulletin_markdown

        report = quality_check(section_text, lang, glossary_path)
        reports.append(report)

    return reports


if __name__ == "__main__":
    # 快速测试 / Quick test
    sample = (
        "نزدیک به یک ماه پس از آغاز تشدید درگیری‌ها، "
        "WFP به حدود ۳۳٬۰۰۰ پناهنده افغان کمک غذایی ارائه می‌دهد.\n"
        "*Source: https://reliefweb.int/report/example*"
    )
    report = quality_check(sample, "fa")
    print(report.to_markdown())
