"""
telegram_bot.py — Telegram Bot 核心逻辑
Core Telegram Bot logic for CrisisBridge.

使用 python-telegram-bot v20+ 的异步框架。
Uses the python-telegram-bot v20+ async framework.

配置 / Configuration (via environment variables):
  TELEGRAM_BOT_TOKEN — Telegram Bot Token（从 @BotFather 获取）
  ANTHROPIC_API_KEY  — Anthropic Claude API Key（可选，用于翻译）

用法 / Usage:
  python -m src.bot.telegram_bot
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import Application, CommandHandler

from .commands import (
    cmd_help,
    cmd_language,
    cmd_latest,
    cmd_shelter,
    cmd_start,
)

# ──────────────────────────────────────────
# 加载环境变量 / Load environment variables
# ──────────────────────────────────────────
# 从项目根目录的 .env 文件加载 / Load from project root .env
_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# 配置日志 / Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────
# Bot 命令菜单定义 / Bot command menu definitions
# ──────────────────────────────────────────
BOT_COMMANDS = [
    BotCommand("start",    "Welcome message / رسالة الترحيب"),
    BotCommand("latest",   "Latest bulletin / آخرین خلاصه"),
    BotCommand("shelter",  "Find shelter / البحث عن مأوى"),
    BotCommand("language", "Set language / تنظیم زبان"),
    BotCommand("help",     "Help / راهنما"),
]


async def _post_init(application: Application) -> None:
    """
    Bot 启动后的初始化回调：设置命令菜单。
    Post-init callback: set bot command menu in Telegram.

    Args:
        application: python-telegram-bot Application 实例。
    """
    await application.bot.set_my_commands(BOT_COMMANDS)
    logger.info("Bot command menu registered.")


def build_application(token: str) -> Application:
    """
    构建并配置 Telegram Bot Application。
    Build and configure the Telegram Bot Application.

    Args:
        token: Telegram Bot Token（来自环境变量）。

    Returns:
        配置好的 Application 实例 / Configured Application instance.
    """
    app = (
        Application.builder()
        .token(token)
        .post_init(_post_init)
        .build()
    )

    # 注册命令处理器 / Register command handlers
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("latest",   cmd_latest))
    app.add_handler(CommandHandler("shelter",  cmd_shelter))
    app.add_handler(CommandHandler("language", cmd_language))
    app.add_handler(CommandHandler("help",     cmd_help))

    logger.info("All command handlers registered.")
    return app


def main() -> None:
    """
    Bot 主入口：读取 Token 并启动 polling 循环。
    Main entry point: read token and start polling loop.

    从环境变量 TELEGRAM_BOT_TOKEN 读取 Token。
    Reads bot token from TELEGRAM_BOT_TOKEN environment variable.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical(
            "TELEGRAM_BOT_TOKEN environment variable is not set. "
            "Please set it in your .env file or shell environment."
        )
        sys.exit(1)

    logger.info("Starting CrisisBridge Bot…")
    application = build_application(token)

    # 使用长轮询模式启动 / Start with long polling
    application.run_polling(
        allowed_updates=["message"],
        drop_pending_updates=True,  # 忽略离线期间积压的更新 / Drop backlog on start
    )


if __name__ == "__main__":
    main()
