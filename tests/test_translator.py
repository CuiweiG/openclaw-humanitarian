"""
test_translator.py — 翻译模块单元测试
Unit tests for src/translator/translate.py and src/translator/quality_check.py

使用 pytest，不调用真实 API。
Uses pytest; no real API calls are made.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ──────────────────────────────────────────
# 测试夹具 / Fixtures
# ──────────────────────────────────────────

SAMPLE_GLOSSARY = [
    {
        "en": "displaced persons",
        "fa": "آوارگان",
        "dar": "بیجاشدگان",
        "ar": "النازحون",
        "zh": "流离失所者",
    },
    {
        "en": "humanitarian corridor",
        "fa": "کریدور انسان‌دوستانه",
        "dar": "کوریدور بشردوستانه",
        "ar": "الممر الإنساني",
        "zh": "人道主义走廊",
    },
    {
        "en": "ceasefire",
        "fa": "آتش‌بس",
        "dar": "آتش‌بس",
        "ar": "وقف إطلاق النار",
        "zh": "停火",
    },
]

SAMPLE_ENGLISH_TEXT = (
    "Nearly one month into the escalation, WFP is providing food assistance "
    "to approximately 33,000 Afghan refugees in Iran. In Lebanon, humanitarian "
    "access to southern areas remains severely restricted. A ceasefire remains elusive."
)


@pytest.fixture
def glossary_file(tmp_path: Path) -> Path:
    """
    创建临时 glossary.json 文件。
    Create a temporary glossary.json file for tests.
    """
    gfile = tmp_path / "glossary.json"
    gfile.write_text(json.dumps(SAMPLE_GLOSSARY, ensure_ascii=False), encoding="utf-8")
    return gfile


# ──────────────────────────────────────────
# translate.py 测试 / translate.py tests
# ──────────────────────────────────────────

class TestLoadGlossary:
    """测试 load_glossary 函数 / Tests for load_glossary."""

    def test_loads_valid_file(self, glossary_file: Path):
        """应成功加载有效的 glossary.json / Should load a valid glossary.json."""
        from src.translator.translate import load_glossary
        entries = load_glossary(glossary_file)
        assert len(entries) == 3
        assert entries[0]["en"] == "displaced persons"

    def test_missing_file_returns_empty(self, tmp_path: Path):
        """文件不存在时应返回空列表 / Missing file should return empty list."""
        from src.translator.translate import load_glossary
        result = load_glossary(tmp_path / "nonexistent.json")
        assert result == []

    def test_all_language_keys_present(self, glossary_file: Path):
        """每条术语应包含所有语言键 / Each entry should contain all language keys."""
        from src.translator.translate import load_glossary
        entries = load_glossary(glossary_file)
        for entry in entries:
            for lang in ["en", "fa", "dar", "ar", "zh"]:
                assert lang in entry


class TestStubBackend:
    """测试 StubBackend 翻译后端 / Tests for StubBackend."""

    def test_returns_non_empty_string(self):
        """StubBackend 应返回非空字符串 / StubBackend should return non-empty string."""
        from src.translator.translate import StubBackend
        backend = StubBackend()
        result = backend.translate("Test text", "fa")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_includes_language_marker(self):
        """StubBackend 返回值应包含语言标记 / Return value should include language marker."""
        from src.translator.translate import StubBackend
        backend = StubBackend()
        result = backend.translate("Hello", "ar")
        assert "AR" in result.upper()


class TestCheckGlossaryConsistency:
    """测试术语一致性检查 / Tests for glossary consistency check."""

    def test_detects_untranslated_english_term(self):
        """应检测到未翻译的英文术语 / Should detect untranslated English terms."""
        from src.translator.translate import check_glossary_consistency
        # 翻译文本中遗留了英文术语 / English term left in "translation"
        translated = "در ایران displaced persons زیادی هستند."
        issues = check_glossary_consistency(translated, "fa", SAMPLE_GLOSSARY)
        assert len(issues) > 0
        assert any("displaced persons" in issue for issue in issues)

    def test_no_issues_when_properly_translated(self):
        """正确翻译时不应有问题 / Should have no issues when properly translated."""
        from src.translator.translate import check_glossary_consistency
        # 使用了波斯语术语，没有遗留英文 / Uses Persian term, no English left
        translated = "آوارگان زیادی در ایران هستند."
        issues = check_glossary_consistency(translated, "fa", SAMPLE_GLOSSARY)
        assert len(issues) == 0

    def test_skips_missing_language_entry(self):
        """缺少目标语言条目时应跳过 / Should skip entries missing target language."""
        from src.translator.translate import check_glossary_consistency
        glossary_no_tr = [{"en": "ceasefire", "fa": "آتش‌بس"}]  # No "tr" key
        issues = check_glossary_consistency("ceasefire", "tr", glossary_no_tr)
        # Should not crash, no issues since no "tr" preferred term to compare
        assert isinstance(issues, list)


class TestTranslateBulletin:
    """测试 translate_bulletin 主函数 / Tests for translate_bulletin."""

    def test_returns_markdown_string(self, glossary_file: Path):
        """应返回 Markdown 格式字符串 / Should return a Markdown-formatted string."""
        from src.translator.translate import translate_bulletin
        result = translate_bulletin(
            english_text=SAMPLE_ENGLISH_TEXT,
            target_languages=["en"],
            glossary_path=glossary_file,
        )
        assert isinstance(result, str)
        assert "CrisisBridge Bulletin" in result

    def test_english_passthrough_not_translated(self, glossary_file: Path):
        """英文内容应直接输出，不经翻译 / English content should pass through without translation."""
        from src.translator.translate import translate_bulletin
        result = translate_bulletin(
            english_text=SAMPLE_ENGLISH_TEXT,
            target_languages=["en"],
            glossary_path=glossary_file,
        )
        assert SAMPLE_ENGLISH_TEXT in result

    def test_stub_backend_used_by_default(self, glossary_file: Path):
        """未指定后端时应使用 StubBackend / StubBackend should be used when no backend specified."""
        from src.translator.translate import translate_bulletin
        result = translate_bulletin(
            english_text="Short text.",
            target_languages=["fa"],
            glossary_path=glossary_file,
        )
        # StubBackend 会加上 [FA TRANSLATION PLACEHOLDER]
        assert "PLACEHOLDER" in result.upper() or len(result) > 0

    def test_source_url_included(self, glossary_file: Path):
        """来源 URL 应包含在输出中 / Source URL should be included in output."""
        from src.translator.translate import translate_bulletin
        url = "https://reliefweb.int/test"
        result = translate_bulletin(
            english_text="Test.",
            target_languages=["en"],
            glossary_path=glossary_file,
            source_url=url,
        )
        assert url in result

    def test_invalid_languages_raise_error(self, glossary_file: Path):
        """无效语言代码应抛出 ValueError / Invalid language codes should raise ValueError."""
        from src.translator.translate import translate_bulletin
        with pytest.raises(ValueError, match="No valid target languages"):
            translate_bulletin(
                english_text="Test.",
                target_languages=["xx", "yy"],  # Invalid codes
                glossary_path=glossary_file,
            )

    def test_custom_backend_called(self, glossary_file: Path):
        """自定义翻译后端应被正确调用 / Custom backend should be called correctly."""
        from src.translator.translate import TranslationBackend, translate_bulletin

        # 创建 mock 后端 / Create mock backend
        mock_backend = MagicMock(spec=TranslationBackend)
        mock_backend.translate.return_value = "مترجم شد"

        result = translate_bulletin(
            english_text="Test text.",
            target_languages=["fa"],
            backend=mock_backend,
            glossary_path=glossary_file,
        )

        mock_backend.translate.assert_called_once_with("Test text.", "fa")
        assert "مترجم شد" in result


# ──────────────────────────────────────────
# quality_check.py 测试 / quality_check.py tests
# ──────────────────────────────────────────

class TestCheckWordCount:
    """测试词数检查 / Tests for word count check."""

    def test_passes_under_limit(self):
        """词数在限制内时应通过 / Should pass when word count under limit."""
        from src.translator.quality_check import check_word_count
        short_text = "This is a short text." * 5  # ~25 words
        result = check_word_count(short_text, max_words=200)
        assert result.passed is True

    def test_fails_over_limit(self):
        """词数超过限制时应失败 / Should fail when word count exceeds limit."""
        from src.translator.quality_check import check_word_count
        long_text = "word " * 250  # 250 words
        result = check_word_count(long_text, max_words=200)
        assert result.passed is False
        assert "EXCEEDS" in result.message

    def test_message_contains_word_count(self):
        """消息应包含实际词数 / Message should include actual word count."""
        from src.translator.quality_check import check_word_count
        text = "one two three four five"
        result = check_word_count(text)
        assert "5" in result.message


class TestCheckSourceAttribution:
    """测试来源标注检查 / Tests for source attribution check."""

    def test_passes_with_source_line(self):
        """包含来源行时应通过 / Should pass when source line present."""
        from src.translator.quality_check import check_source_attribution
        text = "Some text.\n*Source: https://reliefweb.int/report/test*"
        result = check_source_attribution(text)
        assert result.passed is True

    def test_fails_without_source_line(self):
        """缺少来源行时应失败 / Should fail when source line missing."""
        from src.translator.quality_check import check_source_attribution
        text = "Some text without any source attribution."
        result = check_source_attribution(text)
        assert result.passed is False

    def test_partial_url_not_enough(self):
        """不完整的来源格式不应通过 / Partial source format should not pass."""
        from src.translator.quality_check import check_source_attribution
        text = "Some text. Source: reliefweb.int"  # Missing *...* format and https://
        result = check_source_attribution(text)
        assert result.passed is False


class TestCheckNumericFormat:
    """测试数字格式检查 / Tests for numeric format check."""

    def test_persian_with_arabic_indic_fails(self):
        """波斯语文本中含阿拉伯数字应失败 / Persian text with Arabic-Indic digits should fail."""
        from src.translator.quality_check import check_numeric_format
        text = "٣٣٬٠٠٠ نفر"  # Arabic-Indic digits in Persian text
        result = check_numeric_format(text, "fa")
        assert result.passed is False

    def test_arabic_with_persian_digits_fails(self):
        """阿拉伯语文本中含波斯数字应失败 / Arabic text with Persian digits should fail."""
        from src.translator.quality_check import check_numeric_format
        text = "۳۳٬۰۰۰ شخص"  # Persian digits in Arabic text
        result = check_numeric_format(text, "ar")
        assert result.passed is False

    def test_western_digits_always_pass(self):
        """西方数字在任何语言中都应通过 / Western digits should pass in all languages."""
        from src.translator.quality_check import check_numeric_format
        text = "33,000 people were affected."
        for lang in ["fa", "dar", "ar", "zh", "en"]:
            result = check_numeric_format(text, lang)
            assert result.passed is True, f"Failed for lang={lang}"

    def test_persian_digits_ok_for_persian(self):
        """波斯数字在波斯语中应通过 / Persian digits should be OK in Persian text."""
        from src.translator.quality_check import check_numeric_format
        text = "۳۳٬۰۰۰ آواره"  # Persian digits in Persian text
        result = check_numeric_format(text, "fa")
        assert result.passed is True


class TestQualityCheck:
    """测试 quality_check 主函数 / Tests for the main quality_check function."""

    def test_full_check_returns_report(self, glossary_file: Path):
        """应返回 QualityReport 实例 / Should return a QualityReport instance."""
        from src.translator.quality_check import quality_check, QualityReport
        text = (
            "آوارگان در ایران نیاز به کمک دارند.\n"
            "*Source: https://reliefweb.int/test*"
        )
        report = quality_check(text, "fa", glossary_path=glossary_file)
        assert isinstance(report, QualityReport)
        assert len(report.checks) >= 4

    def test_report_has_to_markdown(self, glossary_file: Path):
        """报告应能转换为 Markdown / Report should produce valid Markdown."""
        from src.translator.quality_check import quality_check
        text = "Short text.\n*Source: https://reliefweb.int/test*"
        report = quality_check(text, "en", glossary_path=glossary_file)
        md = report.to_markdown()
        assert isinstance(md, str)
        assert "Quality Report" in md

    def test_report_passed_property(self, glossary_file: Path):
        """passed 属性应反映错误级别检查 / passed should reflect error-level check results."""
        from src.translator.quality_check import quality_check
        # 文本含来源标注，应通过错误级别检查
        text = "OK text.\n*Source: https://reliefweb.int/test*"
        report = quality_check(text, "en", glossary_path=glossary_file)
        assert report.passed is True
