"""
test_scraper.py — ReliefWeb 抓取器单元测试
Unit tests for src/scraper/reliefweb.py and src/scraper/parser.py

使用 pytest + unittest.mock，不发出真实网络请求。
Uses pytest + unittest.mock; no real network requests are made.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

# ──────────────────────────────────────────
# 测试夹具 / Test fixtures
# ──────────────────────────────────────────

# 模拟 ReliefWeb API 返回的原始数据 / Mock raw ReliefWeb API response
MOCK_API_RESPONSE = {
    "data": [
        {
            "href": "https://api.reliefweb.int/v1/reports/123",
            "fields": {
                "title": "Situation Report #5 — WFP Middle East",
                "body": (
                    "- 33,000 Afghan refugees receiving food assistance in Iran.\n"
                    "- Southern Lebanon access remains restricted.\n"
                    "- WFP distributed 500 MT of food at border crossings."
                ),
                "source": [{"name": "WFP"}],
                "date": {"created": "2026-03-27T00:00:00+00:00"},
                "url": "https://reliefweb.int/report/iran/situation-report-5",
            },
        },
        {
            "href": "https://api.reliefweb.int/v1/reports/124",
            "fields": {
                "title": "Lebanon Flash Update #2",
                "body": "Evacuation orders extended in southern Lebanon.",
                "source": [{"name": "OCHA"}],
                "date": {"created": "2026-03-26T18:00:00+00:00"},
                "url": "https://reliefweb.int/report/lebanon/flash-update-2",
            },
        },
    ],
    "totalCount": 2,
}

# 空响应 / Empty response
MOCK_EMPTY_RESPONSE = {"data": [], "totalCount": 0}


# ──────────────────────────────────────────
# reliefweb.py 测试 / reliefweb.py tests
# ──────────────────────────────────────────

class TestBuildQuery:
    """测试 _build_query 函数 / Tests for _build_query helper."""

    def test_default_countries_in_query(self):
        """查询体应包含默认国家过滤器 / Query should include default country filter."""
        from src.scraper.reliefweb import _build_query
        query = _build_query(countries=["Iran", "Lebanon"])
        conditions = query["filter"]["conditions"]
        # 应有 OR 条件包含两国 / Should have OR condition for two countries
        or_cond = next(c for c in conditions if c.get("operator") == "OR")
        country_values = [c["value"] for c in or_cond["conditions"]]
        assert "Iran" in country_values
        assert "Lebanon" in country_values

    def test_limit_applied(self):
        """查询体应应用 limit 参数 / Query should apply the limit parameter."""
        from src.scraper.reliefweb import _build_query
        query = _build_query(countries=["Iran"], limit=5)
        assert query["limit"] == 5

    def test_required_fields_present(self):
        """查询体应请求正确的字段 / Query should request the required fields."""
        from src.scraper.reliefweb import _build_query
        query = _build_query(countries=["Iran"])
        fields = query["fields"]["include"]
        for field in ["title", "body", "source", "date", "url"]:
            assert field in fields

    def test_extra_filters_appended(self):
        """额外过滤条件应追加到 AND 条件列表 / Extra filters should be appended."""
        from src.scraper.reliefweb import _build_query
        extra = [{"field": "source.name", "value": "OCHA"}]
        query = _build_query(countries=["Iran"], extra_filters=extra)
        conditions = query["filter"]["conditions"]
        assert any(c.get("field") == "source.name" for c in conditions)


class TestParseReport:
    """测试 _parse_report 函数 / Tests for _parse_report helper."""

    def test_title_extracted(self):
        """应正确提取标题 / Title should be correctly extracted."""
        from src.scraper.reliefweb import _parse_report
        raw = MOCK_API_RESPONSE["data"][0]
        result = _parse_report(raw)
        assert result["title"] == "Situation Report #5 — WFP Middle East"

    def test_source_extracted(self):
        """应正确提取来源名称 / Source name should be correctly extracted."""
        from src.scraper.reliefweb import _parse_report
        raw = MOCK_API_RESPONSE["data"][0]
        result = _parse_report(raw)
        assert result["source"] == "WFP"

    def test_url_extracted(self):
        """应提取正确的 URL / Correct URL should be extracted."""
        from src.scraper.reliefweb import _parse_report
        raw = MOCK_API_RESPONSE["data"][0]
        result = _parse_report(raw)
        assert "reliefweb.int" in result["url"]

    def test_summary_truncated_at_300_chars(self):
        """正文超过 300 字符时应截断 / Body > 300 chars should be truncated."""
        from src.scraper.reliefweb import _parse_report
        long_body = "x" * 500
        raw = {
            "href": "http://example.com",
            "fields": {
                "title": "Test",
                "body": long_body,
                "source": [{"name": "Test"}],
                "date": {"created": "2026-01-01T00:00:00+00:00"},
            },
        }
        result = _parse_report(raw)
        assert len(result["summary"]) <= 305  # 300 chars + ellipsis buffer
        assert result["summary"].endswith("…")

    def test_missing_source_graceful(self):
        """缺少来源字段时不应崩溃 / Missing source field should not crash."""
        from src.scraper.reliefweb import _parse_report
        raw = {
            "href": "http://example.com",
            "fields": {
                "title": "Test",
                "body": "Body text.",
                "date": {"created": "2026-01-01T00:00:00+00:00"},
            },
        }
        result = _parse_report(raw)
        assert result["source"] == ""


class TestFetchReports:
    """测试 fetch_reports 主函数 / Tests for the main fetch_reports function."""

    @patch("src.scraper.reliefweb.requests.post")
    def test_successful_fetch_returns_list(self, mock_post):
        """成功请求应返回报告列表 / Successful request should return report list."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        from src.scraper.reliefweb import fetch_reports
        results = fetch_reports()

        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]["title"] == "Situation Report #5 — WFP Middle East"

    @patch("src.scraper.reliefweb.requests.post")
    def test_empty_response_returns_empty_list(self, mock_post):
        """空响应应返回空列表 / Empty API response should return empty list."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_EMPTY_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        from src.scraper.reliefweb import fetch_reports
        results = fetch_reports()
        assert results == []

    @patch("src.scraper.reliefweb.requests.post")
    @patch("src.scraper.reliefweb.time.sleep")  # 跳过重试等待 / Skip retry sleep
    def test_retry_on_failure(self, mock_sleep, mock_post):
        """网络错误时应重试 / Should retry on network errors."""
        import requests as req_lib
        mock_post.side_effect = req_lib.exceptions.Timeout("timeout")

        from src.scraper.reliefweb import fetch_reports
        with pytest.raises(RuntimeError, match="Failed to fetch"):
            fetch_reports()

        # 应尝试 MAX_RETRIES 次 / Should have attempted MAX_RETRIES times
        from src.scraper.reliefweb import MAX_RETRIES
        assert mock_post.call_count == MAX_RETRIES

    @patch("src.scraper.reliefweb.requests.post")
    def test_custom_limit_passed_to_api(self, mock_post):
        """自定义 limit 应传递到 API 查询 / Custom limit should be passed to API query."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_EMPTY_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        from src.scraper.reliefweb import fetch_reports
        fetch_reports(limit=3)

        call_kwargs = mock_post.call_args
        sent_body = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][1]
        assert sent_body.get("limit") == 3


# ──────────────────────────────────────────
# parser.py 测试 / parser.py tests
# ──────────────────────────────────────────

class TestStripHtml:
    """测试 HTML 清理函数 / Tests for HTML stripping."""

    def test_removes_bold_tags(self):
        """应移除 <b> 标签 / Should remove <b> tags."""
        from src.scraper.parser import _strip_html
        result = _strip_html("<b>Hello</b> world")
        assert result == "Hello world"

    def test_removes_nested_tags(self):
        """应移除嵌套标签 / Should remove nested tags."""
        from src.scraper.parser import _strip_html
        result = _strip_html("<div><p><strong>Test</strong></p></div>")
        assert "Test" in result
        assert "<" not in result

    def test_empty_string_returns_empty(self):
        """空字符串应返回空字符串 / Empty string should return empty string."""
        from src.scraper.parser import _strip_html
        assert _strip_html("") == ""

    def test_plain_text_unchanged(self):
        """纯文本不应改变 / Plain text should be unchanged."""
        from src.scraper.parser import _strip_html
        text = "No HTML here."
        assert _strip_html(text) == text


class TestExtractKeyPoints:
    """测试关键点提取 / Tests for key point extraction."""

    def test_extracts_bullet_points(self):
        """应提取以 - 开头的项目符号 / Should extract lines starting with '-'."""
        from src.scraper.parser import _extract_key_points
        text = (
            "- 33,000 refugees received food aid.\n"
            "- Southern Lebanon access restricted.\n"
            "- WFP distributed 500 MT."
        )
        points = _extract_key_points(text)
        assert len(points) >= 2
        assert any("33,000" in p for p in points)

    def test_max_points_respected(self):
        """提取的要点数量不应超过 max_points / Should not exceed max_points."""
        from src.scraper.parser import _extract_key_points
        text = "\n".join(f"- Point number {i} with enough content." for i in range(10))
        points = _extract_key_points(text, max_points=3)
        assert len(points) <= 3


class TestParseReport:
    """测试 parse_report 函数 / Tests for parse_report function."""

    def test_output_schema_correct(self):
        """输出应包含所有必需字段 / Output should contain all required fields."""
        from src.scraper.parser import parse_report
        raw = {
            "title": "<b>Test Report</b>",
            "summary": "- Food aid distributed.\n- Access restricted.",
            "date": "2026-03-27T00:00:00+00:00",
            "source": "OCHA",
            "url": "https://reliefweb.int/test",
        }
        result = parse_report(raw)
        assert "title" in result
        assert "key_points" in result
        assert "date" in result
        assert "source_url" in result
        assert "word_count" in result

    def test_html_stripped_from_title(self):
        """标题中的 HTML 应被清除 / HTML should be stripped from title."""
        from src.scraper.parser import parse_report
        raw = {
            "title": "<b>Bold Title</b>",
            "summary": "Some text.",
            "date": "",
            "source": "",
            "url": "",
        }
        result = parse_report(raw)
        assert "<b>" not in result["title"]
        assert result["title"] == "Bold Title"

    def test_word_count_positive(self):
        """词数应大于零（有内容时）/ Word count should be > 0 when content present."""
        from src.scraper.parser import parse_report
        raw = {
            "title": "Title",
            "summary": "Word one two three.",
            "date": "",
            "source": "",
            "url": "",
        }
        result = parse_report(raw)
        assert result["word_count"] > 0

    def test_parse_reports_skips_failed(self):
        """批量解析时应跳过解析失败的条目 / Batch parse should skip failed entries."""
        from src.scraper.parser import parse_reports
        # 混入一个会触发异常的 None 值 / Mix in a None that will trigger an exception
        reports = [
            {"title": "Good", "summary": "Text.", "date": "", "source": "", "url": ""},
            None,  # 这会引发 AttributeError / This will cause AttributeError
        ]
        # 不应崩溃，应返回成功解析的条目 / Should not crash, returns successfully parsed
        results = parse_reports(reports)
        assert len(results) == 1
        assert results[0]["title"] == "Good"
