"""
parser.py — 报告解析模块
Report parser: extracts structured information from raw scraped reports.

输入：reliefweb.py / ocha.py 返回的原始报告 JSON 列表
输出：{title, key_points, date, source_url, word_count}

Input:  raw report list from reliefweb.py / ocha.py
Output: {title, key_points, date, source_url, word_count}
"""

import logging
import re
from typing import Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def _strip_html(text: str) -> str:
    """
    清除文本中的所有 HTML 标签。
    Strip all HTML tags from the given text.

    使用 BeautifulSoup 解析，比正则更安全。
    Uses BeautifulSoup for safer parsing than regex alone.

    Args:
        text: 可能含有 HTML 标签的字符串。

    Returns:
        纯文本字符串 / Plain-text string.
    """
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    # 将 <br> 和 <p> 替换为换行符，保留段落结构
    for tag in soup.find_all(["br", "p"]):
        tag.replace_with("\n" + (tag.get_text() or ""))
    cleaned = soup.get_text(separator=" ")
    # 合并多余的空白 / Collapse excessive whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _extract_key_points(text: str, max_points: int = 5) -> list[str]:
    """
    从报告文本中提取关键要点。
    Extract key bullet points from report text.

    策略：
    1. 优先识别以 "-", "•", "*", 数字+". " 开头的行（已有项目符号）
    2. 否则按句子切分，取前 max_points 句

    Strategy:
    1. Prefer lines that already start with bullets (-, •, *, N.)
    2. Fall back to splitting by sentence and taking first max_points.

    Args:
        text: 已清洗的纯文本。
        max_points: 最多提取几个要点。

    Returns:
        要点字符串列表 / List of key-point strings.
    """
    lines = text.splitlines()
    bullet_pattern = re.compile(r"^\s*[-•*]|\s*\d+\.\s")
    bullets = [
        line.strip().lstrip("-•* ").strip()
        for line in lines
        if bullet_pattern.match(line) and len(line.strip()) > 10
    ]

    if bullets:
        return bullets[:max_points]

    # 按句子切割作为备选 / Fallback: split by sentence
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 20][:max_points]


def parse_report(raw_report: dict[str, Any]) -> dict[str, Any]:
    """
    将单条原始报告解析为结构化输出。
    Parse a single raw report dict into structured output.

    Args:
        raw_report: 来自 reliefweb.py / ocha.py 的标准报告字典。
                    Standard report dict from reliefweb.py / ocha.py.
                    Expected keys: title, summary, date, source, url

    Returns:
        结构化报告 / Structured report dict:
        {
            "title":      str,
            "key_points": list[str],
            "date":       str,
            "source_url": str,
            "word_count": int,
        }
    """
    title = _strip_html(raw_report.get("title", ""))
    raw_body = raw_report.get("summary", "")
    clean_body = _strip_html(raw_body)

    key_points = _extract_key_points(clean_body)
    word_count = len(clean_body.split()) if clean_body else 0

    return {
        "title": title,
        "key_points": key_points,
        "date": raw_report.get("date", ""),
        "source_url": raw_report.get("url", ""),
        "word_count": word_count,
    }


def parse_reports(raw_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    批量解析报告列表。
    Parse a list of raw reports.

    Args:
        raw_reports: 原始报告列表 / List of raw report dicts.

    Returns:
        结构化报告列表 / List of structured report dicts.
    """
    results = []
    for i, report in enumerate(raw_reports):
        try:
            parsed = parse_report(report)
            results.append(parsed)
        except Exception as exc:
            logger.warning("Failed to parse report %d: %s", i, exc)
            # 跳过解析失败的条目，继续处理其余 / Skip failed entries
    return results


if __name__ == "__main__":
    import json

    # 简单测试 / Quick smoke test
    sample = [
        {
            "title": "<b>Situation Report #5</b>",
            "summary": (
                "- 33,000 Afghan refugees received food assistance.\n"
                "- Southern Lebanon access remains restricted.\n"
                "- WFP distributed 500 MT of food."
            ),
            "date": "2026-03-27T00:00:00+00:00",
            "source": "WFP",
            "url": "https://reliefweb.int/report/example",
        }
    ]
    parsed = parse_reports(sample)
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
