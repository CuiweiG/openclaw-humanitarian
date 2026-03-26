"""
reliefweb.py — ReliefWeb API v2 数据抓取脚本
ReliefWeb API v2 scraper for humanitarian reports.

抓取伊朗和黎巴嫩最新24小时内的人道主义报告。
Fetches the latest humanitarian reports for Iran and Lebanon from the past 24 hours.

API Docs: https://apidoc.reliefweb.int/
"""

import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import requests

# 配置日志 / Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# 常量 / Constants
# ──────────────────────────────────────────
RELIEFWEB_API_URL = "https://api.reliefweb.int/v1/reports"
DEFAULT_COUNTRIES = ["Iran", "Lebanon"]
DEFAULT_LIMIT = 10
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2  # 指数退避基数 / Exponential backoff base


def _build_query(
    countries: list[str],
    hours_back: int = 24,
    limit: int = DEFAULT_LIMIT,
    extra_filters: Optional[list[dict]] = None,
) -> dict[str, Any]:
    """
    构建 ReliefWeb API 查询体。
    Build the ReliefWeb API request body.

    Args:
        countries: 要过滤的国家名称列表 / List of country names to filter by.
        hours_back: 向前查询多少小时 / How many hours back to look.
        limit: 最多返回多少条报告 / Maximum number of reports to return.
        extra_filters: 额外的 AND 过滤条件 / Additional AND-level filter conditions.

    Returns:
        完整的 API 请求体字典 / Full API request body dict.
    """
    # 计算时间范围 / Calculate time range
    since = datetime.now(tz=timezone.utc) - timedelta(hours=hours_back)
    since_str = since.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # 构建国家过滤器（OR 逻辑）/ Build country filter (OR logic)
    country_conditions = [
        {"field": "country.name", "value": c} for c in countries
    ]

    # 基础过滤条件 / Base filter conditions
    and_conditions: list[dict] = [
        {
            "operator": "OR",
            "conditions": country_conditions,
        },
        {
            "field": "date.created",
            "value": {"from": since_str},
        },
    ]

    # 合并额外过滤条件 / Merge extra filters if any
    if extra_filters:
        and_conditions.extend(extra_filters)

    query = {
        "filter": {
            "operator": "AND",
            "conditions": and_conditions,
        },
        "fields": {
            "include": ["title", "body", "source", "date", "url"],
        },
        "sort": ["date.created:desc"],
        "limit": limit,
    }
    return query


def _parse_report(raw: dict[str, Any]) -> dict[str, Any]:
    """
    将 ReliefWeb 原始报告条目转换为标准输出格式。
    Convert a raw ReliefWeb report entry to the standard output format.

    Args:
        raw: ReliefWeb API 返回的单条报告字典 / Single report dict from API.

    Returns:
        标准化的报告字典 / Standardised report dict.
        Schema: {title, summary, date, source, url}
    """
    fields = raw.get("fields", {})

    # 提取来源名称（可能是列表）/ Extract source name (may be a list)
    sources = fields.get("source", [])
    if isinstance(sources, list):
        source_name = ", ".join(s.get("name", "") for s in sources)
    else:
        source_name = str(sources)

    # 摘要：截取 body 前 300 字符 / Summary: first 300 chars of body
    body = fields.get("body", "") or ""
    summary = body[:300].strip()
    if len(body) > 300:
        summary += "…"

    # 日期 / Date
    date_obj = fields.get("date", {})
    date_str = date_obj.get("created", "") if isinstance(date_obj, dict) else ""

    return {
        "title": fields.get("title", ""),
        "summary": summary,
        "date": date_str,
        "source": source_name,
        "url": raw.get("href", ""),
    }


def fetch_reports(
    countries: list[str] = None,
    hours_back: int = 24,
    limit: int = DEFAULT_LIMIT,
    extra_filters: Optional[list[dict]] = None,
) -> list[dict[str, Any]]:
    """
    从 ReliefWeb API 抓取最新报告，带重试逻辑。
    Fetch latest reports from ReliefWeb API with retry logic.

    Args:
        countries: 国家过滤列表，默认 Iran 和 Lebanon。
        hours_back: 查询最近 N 小时内的报告。
        limit: 最多返回条数。
        extra_filters: 附加的 AND 过滤条件（供子类复用）。

    Returns:
        标准化报告列表 / List of standardised report dicts.

    Raises:
        RuntimeError: 所有重试均失败时抛出。
    """
    if countries is None:
        countries = DEFAULT_COUNTRIES

    query = _build_query(
        countries=countries,
        hours_back=hours_back,
        limit=limit,
        extra_filters=extra_filters,
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        # 标识自己的 user-agent，遵守 ReliefWeb API 使用规范
        "User-Agent": "OpenClaw-HumanitarianBot/1.0 (aid@agentmail.to)",
    }

    last_error: Optional[Exception] = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "Fetching ReliefWeb reports (attempt %d/%d) for countries: %s",
                attempt,
                MAX_RETRIES,
                countries,
            )
            response = requests.post(
                RELIEFWEB_API_URL,
                json=query,
                headers=headers,
                timeout=15,  # 15 秒超时 / 15-second timeout
            )
            response.raise_for_status()

            data = response.json()
            raw_reports = data.get("data", [])

            reports = [_parse_report(r) for r in raw_reports]
            logger.info("Fetched %d reports.", len(reports))
            return reports

        except requests.exceptions.Timeout as e:
            logger.warning("Request timed out (attempt %d): %s", attempt, e)
            last_error = e
        except requests.exceptions.HTTPError as e:
            logger.warning("HTTP error (attempt %d): %s", attempt, e)
            last_error = e
        except requests.exceptions.RequestException as e:
            logger.warning("Request error (attempt %d): %s", attempt, e)
            last_error = e

        # 指数退避等待 / Exponential backoff before retry
        if attempt < MAX_RETRIES:
            wait = RETRY_BACKOFF_SECONDS ** attempt
            logger.info("Retrying in %d seconds…", wait)
            time.sleep(wait)

    raise RuntimeError(
        f"Failed to fetch ReliefWeb reports after {MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )


def main() -> None:
    """
    命令行入口：抓取并打印 JSON 报告。
    CLI entry point: fetch and print reports as JSON.
    """
    try:
        reports = fetch_reports()
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    except RuntimeError as e:
        logger.error("Fatal error: %s", e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
