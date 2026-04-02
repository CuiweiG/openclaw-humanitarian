"""
commands.py — Telegram Bot 命令处理函数
Command handler functions for the CrisisBridge Telegram Bot.

每个函数对应一个 Bot 命令，负责处理业务逻辑并发送回复。
Each function corresponds to one bot command and handles business logic + reply.
"""

import logging
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import json
from pathlib import Path

from .messages import (
    ERROR_GENERIC,
    HELP_MESSAGES,
    LANGUAGE_INVALID_MESSAGE,
    LANGUAGE_NAMES,
    LANGUAGE_SET_MESSAGES,
    LATEST_EMPTY,
    LATEST_LOADING,
    SHELTER_NOT_IMPLEMENTED,
    SUPPORTED_LANGUAGES,
    WELCOME_MESSAGES,
    get_message,
)

# ──────────────────────────────────────────
# Locale file loader for languages not in messages.py inline dicts
# Falls back to JSON locale files in src/bot/locales/
# ──────────────────────────────────────────
_LOCALES_DIR = Path(__file__).parent / "locales"
_locale_cache: dict[str, dict[str, str]] = {}


def _load_locale(lang: str) -> dict[str, str]:
    """Load a locale JSON file, with caching."""
    if lang in _locale_cache:
        return _locale_cache[lang]
    locale_file = _LOCALES_DIR / f"{lang}.json"
    if locale_file.exists():
        try:
            with open(locale_file, encoding="utf-8") as f:
                data = json.load(f)
            _locale_cache[lang] = data
            return data
        except Exception:
            pass
    return {}


def _get_locale_message(lang: str, key: str, fallback: str = "") -> str:
    """Get a message from locale file, with English fallback."""
    locale = _load_locale(lang)
    if key in locale:
        return locale[key]
    # Try English locale as fallback
    en_locale = _load_locale("en")
    return en_locale.get(key, fallback)

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# 用户语言偏好存储 / User language preference storage
#
# SECURITY / DATA MINIMIZATION:
#   - Stores ONLY language preference keyed by Telegram user ID.
#   - No geolocation, IP, message content, or interaction history.
#   - In-memory only — all data lost on restart (by design during
#     this phase; persistence must undergo privacy review first).
#   - Never associate user IDs with geographic coordinates.
#   - See src/security/canary.py for scrape detection approach.
#   - See docs/threat-model.md for full security considerations.
#
# NOTE: 生产环境应替换为持久化存储（数据库/Redis），
#       但必须先通过隐私审查。
# In production, replace with persistent storage (DB/Redis)
# after privacy review.
# ──────────────────────────────────────────
user_language_cache: dict[int, str] = {}


def _get_user_lang(user_id: int) -> str:
    """
    获取用户设置的语言偏好，默认为英文。
    Get user's language preference, defaulting to English.

    Args:
        user_id: Telegram 用户 ID。

    Returns:
        语言代码字符串。
    """
    return user_language_cache.get(user_id, "en")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理 /start 命令：发送6语言欢迎消息。
    Handle /start command: send multilingual welcome message.

    Args:
        update: Telegram Update 对象。
        context: Bot 上下文。
    """
    user = update.effective_user
    if not user or not update.message:
        return

    lang = _get_user_lang(user.id)
    logger.info("/start from user %d (lang=%s)", user.id, lang)

    welcome_text = get_message(WELCOME_MESSAGES, lang)
    if not welcome_text or welcome_text == get_message(WELCOME_MESSAGES, "en") and lang != "en":
        # Fallback to locale JSON file for languages not in inline dicts
        locale_text = _get_locale_message(lang, "welcome")
        if locale_text:
            welcome_text = locale_text
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)


async def cmd_latest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理 /latest 命令：抓取并发送最新人道主义简报。
    Handle /latest command: fetch and send the latest humanitarian bulletin.

    流程 / Flow:
    1. 发送"加载中"消息 / Send loading message
    2. 调用 scraper 抓取最新报告 / Call scraper for latest reports
    3. 翻译为用户偏好语言 / Translate to user's preferred language
    4. 发送简报 / Send bulletin

    Args:
        update: Telegram Update 对象。
        context: Bot 上下文。
    """
    user = update.effective_user
    if not user or not update.message:
        return

    lang = _get_user_lang(user.id)
    logger.info("/latest from user %d (lang=%s)", user.id, lang)

    # 发送加载提示 / Send loading indicator
    loading_msg = get_message(LATEST_LOADING, lang)
    sent = await update.message.reply_text(loading_msg)

    try:
        # 导入抓取和翻译模块 / Import scraper and translator
        # 延迟导入以避免循环依赖 / Lazy import to avoid circular deps
        from src.scraper.reliefweb import fetch_reports
        from src.translator.translate import translate_bulletin, ClaudeBackend
        import os

        reports = fetch_reports(hours_back=24, limit=5)

        if not reports:
            empty_msg = get_message(LATEST_EMPTY, lang)
            await sent.edit_text(empty_msg, parse_mode=ParseMode.MARKDOWN)
            return

        # 取第一条报告作为简报内容 / Use the first report as bulletin content
        top_report = reports[0]
        english_text = (
            f"**{top_report['title']}**\n\n"
            f"{top_report['summary']}"
        )

        # 选择翻译后端 / Choose translation backend
        backend = None
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                backend = ClaudeBackend()
            except Exception as e:
                logger.warning("Claude backend unavailable: %s", e)

        target_langs = [lang] if lang != "en" else ["en"]
        bulletin = translate_bulletin(
            english_text=english_text,
            target_languages=target_langs,
            backend=backend,
            source_url=top_report.get("url", ""),
            report_date=top_report.get("date", ""),
        )

        # Telegram 消息有 4096 字符限制，截断如超出 / Truncate if over Telegram limit
        if len(bulletin) > 4096:
            bulletin = bulletin[:4090] + "\n…"

        await sent.edit_text(bulletin, parse_mode=ParseMode.MARKDOWN)

    except Exception as exc:
        logger.exception("Error in /latest handler: %s", exc)
        error_msg = get_message(ERROR_GENERIC, lang)
        await sent.edit_text(error_msg)


async def cmd_shelter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理 /shelter 命令：查询避难所（预留接口，暂未实现）。
    Handle /shelter command: query shelter availability (reserved interface, not yet implemented).

    未来计划 / Future plan:
    - 接入 IOM DTM 数据 / Integrate IOM DTM data
    - 与在地组织合作建立实时空位数据库 / Partner with on-ground orgs for real-time vacancy DB

    Args:
        update: Telegram Update 对象。
        context: Bot 上下文。
        context.args: 地点参数 / Location argument.
    """
    user = update.effective_user
    if not user or not update.message:
        return

    lang = _get_user_lang(user.id)
    location: Optional[str] = " ".join(context.args) if context.args else None
    logger.info("/shelter from user %d, location=%s", user.id, location)

    msg = get_message(SHELTER_NOT_IMPLEMENTED, lang)
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理 /language 命令：设置用户偏好语言。
    Handle /language command: set user's preferred language.

    用法 / Usage: /language [code]
    示例 / Example: /language fa

    Args:
        update: Telegram Update 对象。
        context: Bot 上下文。
        context.args: 语言代码 / Language code.
    """
    user = update.effective_user
    if not user or not update.message:
        return

    # 检查是否提供了语言代码 / Check if language code was provided
    if not context.args:
        lang_list = "\n".join(
            f"  `{code}` — {name}" for code, name in LANGUAGE_NAMES.items()
        )
        await update.message.reply_text(
            f"ℹ️ Please specify a language code:\n{lang_list}\n\nExample: `/language fa`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    requested_lang = context.args[0].lower().strip()

    if requested_lang not in SUPPORTED_LANGUAGES:
        await update.message.reply_text(
            LANGUAGE_INVALID_MESSAGE,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # 保存语言偏好 / Save language preference
    user_language_cache[user.id] = requested_lang
    logger.info("User %d set language to '%s'", user.id, requested_lang)

    confirm_msg = get_message(LANGUAGE_SET_MESSAGES, requested_lang)
    if not confirm_msg:
        locale_text = _get_locale_message(requested_lang, "language_set")
        if locale_text:
            confirm_msg = locale_text.replace("{language}", LANGUAGE_NAMES.get(requested_lang, requested_lang))
        else:
            confirm_msg = f"✅ Language set to {LANGUAGE_NAMES.get(requested_lang, requested_lang)}."
    await update.message.reply_text(confirm_msg)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理 /help 命令：发送帮助信息。
    Handle /help command: send help information.

    Args:
        update: Telegram Update 对象。
        context: Bot 上下文。
    """
    user = update.effective_user
    if not user or not update.message:
        return

    lang = _get_user_lang(user.id)
    logger.info("/help from user %d (lang=%s)", user.id, lang)

    help_text = get_message(HELP_MESSAGES, lang)
    if not help_text or help_text == get_message(HELP_MESSAGES, "en") and lang != "en":
        locale_text = _get_locale_message(lang, "help")
        if locale_text:
            help_text = locale_text
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
