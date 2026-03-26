"""
ocha.py — OCHA 报告抓取脚本
Scraper for OCHA (UN Office for the Coordination of Humanitarian Affairs) reports.

复用 reliefweb.py 的核心逻辑，在 source filter 层面过滤 OCHA 来源。
Reuses reliefweb.py core logic, filtered by OCHA as the source organisation.
"""

import json
import logging
from typing import Any

from .reliefweb import fetch_reports

logger = logging.getLogger(__name__)

# OCHA 在 ReliefWeb 中的来源名称 / OCHA's source name in ReliefWeb
OCHA_SOURCE_FILTER = [
    {
        "field": "source.name",
        "value": "OCHA",
    }
]

DEFAULT_COUNTRIES = ["Iran", "Lebanon"]


def fetch_ocha_reports(
    countries: list[str] = None,
    hours_back: int = 24,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    抓取 OCHA 发布的最新人道主义报告。
    Fetch the latest humanitarian reports published by OCHA.

    通过 ReliefWeb API 过滤 source = OCHA，复用 reliefweb.fetch_reports 核心逻辑。
    Filters source = OCHA via the ReliefWeb API, reusing reliefweb.fetch_reports.

    Args:
        countries: 国家过滤列表，默认 Iran 和 Lebanon。
        hours_back: 查询最近 N 小时内的报告。
        limit: 最多返回条数。

    Returns:
        OCHA 报告的标准化列表 / List of standardised OCHA report dicts.
        Schema: [{title, summary, date, source, url}, ...]
    """
    if countries is None:
        countries = DEFAULT_COUNTRIES

    logger.info(
        "Fetching OCHA reports for countries=%s, hours_back=%d",
        countries,
        hours_back,
    )

    reports = fetch_reports(
        countries=countries,
        hours_back=hours_back,
        limit=limit,
        extra_filters=OCHA_SOURCE_FILTER,
    )

    logger.info("Retrieved %d OCHA reports.", len(reports))
    return reports


def main() -> None:
    """
    命令行入口：抓取 OCHA 报告并输出 JSON。
    CLI entry point: fetch OCHA reports and print as JSON.
    """
    try:
        reports = fetch_ocha_reports()
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    except RuntimeError as e:
        logger.error("Fatal: %s", e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
