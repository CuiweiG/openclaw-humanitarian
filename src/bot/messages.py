"""
messages.py — 多语言消息模板字典
Multilingual message templates for the CrisisBridge Telegram Bot.

所有用户可见的文本集中在这里，方便翻译和维护。
All user-facing strings are centralised here for easy translation and maintenance.
"""

from typing import Any

# ──────────────────────────────────────────
# 语言配置 / Language configuration
# ──────────────────────────────────────────

SUPPORTED_LANGUAGES: list[str] = ["en", "fa", "dar", "ar", "zh", "tr"]

LANGUAGE_NAMES: dict[str, str] = {
    "en":  "English",
    "fa":  "فارسی (Persian)",
    "dar": "دری (Dari)",
    "ar":  "العربية (Arabic)",
    "zh":  "中文 (Chinese)",
    "tr":  "Türkçe (Turkish)",
}

# ──────────────────────────────────────────
# 欢迎消息 / Welcome messages
# ──────────────────────────────────────────

WELCOME_MESSAGES: dict[str, str] = {
    "en": (
        "🌍 *Welcome to CrisisBridge Bot*\n\n"
        "We deliver daily humanitarian bulletins in 9 languages: "
        "Arabic, Persian, Dari, English, Chinese, and Turkish.\n\n"
        "Commands:\n"
        "/latest — Latest bulletin\n"
        "/shelter [location] — Find shelter\n"
        "/language [code] — Set your language\n"
        "/help — Help\n\n"
        "🆘 *Emergency contacts:* UNHCR: +961 1 850 100 | ICRC: +961 1 333 407"
    ),
    "fa": (
        "🌍 *به ربات شبکه بشردوستانه CrisisBridge خوش آمدید*\n\n"
        "ما هر روز خلاصه‌های بشردوستانه را به ۶ زبان ارائه می‌دهیم: "
        "عربی، فارسی، دری، انگلیسی، چینی و ترکی.\n\n"
        "دستورات:\n"
        "/latest — آخرین خلاصه\n"
        "/shelter [مکان] — یافتن سرپناه\n"
        "/language [کد] — تنظیم زبان\n"
        "/help — راهنما\n\n"
        "🆘 *تماس اضطراری:* UNHCR: +98 21 8899 5000"
    ),
    "dar": (
        "🌍 *به ربات شبکه بشردوستانه CrisisBridge خوش آمدید*\n\n"
        "ما هر روز خلاصه‌های بشردوستانه را به ۶ زبان ارائه می‌دهیم: "
        "عربی، فارسی، دری، انگلیسی، چینی و ترکی.\n\n"
        "دستورات:\n"
        "/latest — آخرین خلاصه\n"
        "/shelter [مکان] — یافتن سرپناه\n"
        "/language [کد] — تنظیم زبان\n"
        "/help — کمک\n\n"
        "🆘 *تماس اضطراری:* UNHCR: +98 21 8899 5000"
    ),
    "ar": (
        "🌍 *مرحباً بكم في روبوت شبكة CrisisBridge الإنسانية*\n\n"
        "نوفر نشرات إنسانية يومية بـ 6 لغات: "
        "العربية والفارسية والدرية والإنجليزية والصينية والتركية.\n\n"
        "الأوامر:\n"
        "/latest — آخر نشرة\n"
        "/shelter [موقع] — ابحث عن مأوى\n"
        "/language [كود] — اختر لغتك\n"
        "/help — المساعدة\n\n"
        "🆘 *اتصالات الطوارئ:* UNHCR: +961 1 850 100 | ICRC: +961 1 333 407"
    ),
    "zh": (
        "🌍 *欢迎使用 CrisisBridge 人道主义网络机器人*\n\n"
        "我们每天以6种语言发布人道主义简报：阿拉伯语、波斯语、达里语、英语、中文和土耳其语。\n\n"
        "命令：\n"
        "/latest — 最新简报\n"
        "/shelter [地点] — 查找庇护所\n"
        "/language [代码] — 设置语言\n"
        "/help — 帮助\n\n"
        "🆘 *紧急联系：* UNHCR: +961 1 850 100"
    ),
    "tr": (
        "🌍 *CrisisBridge İnsani Yardım Ağı Botuna Hoş Geldiniz*\n\n"
        "Her gün 6 dilde insani yardım bültenleri sunuyoruz: "
        "Arapça, Farsça, Dari, İngilizce, Çince ve Türkçe.\n\n"
        "Komutlar:\n"
        "/latest — Son bülten\n"
        "/shelter [konum] — Barınak bul\n"
        "/language [kod] — Dil seç\n"
        "/help — Yardım\n\n"
        "🆘 *Acil iletişim:* UNHCR: +90 312 409 7000"
    ),
}

# ──────────────────────────────────────────
# 도움말 메시지 / Help messages
# ──────────────────────────────────────────

HELP_MESSAGES: dict[str, str] = {
    "en": (
        "ℹ️ *CrisisBridge Bot — Help*\n\n"
        "*/start* — Show welcome message\n"
        "*/latest* — Get the latest humanitarian bulletin\n"
        "*/shelter [location]* — Search for shelter near a location\n"
        "*/language [code]* — Set preferred language\n"
        "  Codes: `en` `fa` `dar` `ar` `zh` `tr`\n"
        "*/help* — Show this help message\n\n"
        "📧 Questions: aid@agentmail.to\n"
        "🤖 Bot: @openclaw_aid_bot"
    ),
    "fa": (
        "ℹ️ *ربات بشردوستانه CrisisBridge — راهنما*\n\n"
        "*/start* — نمایش پیام خوش‌آمدگویی\n"
        "*/latest* — دریافت آخرین خلاصه بشردوستانه\n"
        "*/shelter [مکان]* — جستجوی سرپناه\n"
        "*/language [کد]* — تنظیم زبان دلخواه\n"
        "  کدها: `en` `fa` `dar` `ar` `zh` `tr`\n"
        "*/help* — نمایش این راهنما"
    ),
    "dar": (
        "ℹ️ *ربات بشردوستانه CrisisBridge — کمک*\n\n"
        "*/start* — نشان دادن پیام خوش‌آمدگویی\n"
        "*/latest* — گرفتن آخرین خلاصه بشردوستانه\n"
        "*/shelter [مکان]* — جستجوی سرپناه\n"
        "*/language [کد]* — تنظیم زبان دلخواه\n"
        "  کدها: `en` `fa` `dar` `ar` `zh` `tr`\n"
        "*/help* — نشان دادن این کمک"
    ),
    "ar": (
        "ℹ️ *روبوت CrisisBridge الإنساني — المساعدة*\n\n"
        "*/start* — عرض رسالة الترحيب\n"
        "*/latest* — الحصول على آخر نشرة إنسانية\n"
        "*/shelter [موقع]* — البحث عن مأوى\n"
        "*/language [كود]* — تعيين اللغة المفضلة\n"
        "  الرموز: `en` `fa` `dar` `ar` `zh` `tr`\n"
        "*/help* — عرض هذه المساعدة"
    ),
    "zh": (
        "ℹ️ *CrisisBridge 人道主义机器人 — 帮助*\n\n"
        "*/start* — 显示欢迎消息\n"
        "*/latest* — 获取最新人道主义简报\n"
        "*/shelter [地点]* — 搜索庇护所\n"
        "*/language [代码]* — 设置偏好语言\n"
        "  代码: `en` `fa` `dar` `ar` `zh` `tr`\n"
        "*/help* — 显示此帮助"
    ),
    "tr": (
        "ℹ️ *CrisisBridge İnsani Bot — Yardım*\n\n"
        "*/start* — Karşılama mesajını göster\n"
        "*/latest* — Son insani yardım bültenini al\n"
        "*/shelter [konum]* — Barınak ara\n"
        "*/language [kod]* — Tercih edilen dili ayarla\n"
        "  Kodlar: `en` `fa` `dar` `ar` `zh` `tr`\n"
        "*/help* — Bu yardım mesajını göster"
    ),
}

# ──────────────────────────────────────────
# 语言设置确认消息 / Language set confirmation
# ──────────────────────────────────────────

LANGUAGE_SET_MESSAGES: dict[str, str] = {
    "en":  "✅ Language set to English.",
    "fa":  "✅ زبان به فارسی تنظیم شد.",
    "dar": "✅ زبان به دری تنظیم شد.",
    "ar":  "✅ تم تعيين اللغة إلى العربية.",
    "zh":  "✅ 语言已设置为中文。",
    "tr":  "✅ Dil Türkçe olarak ayarlandı.",
}

LANGUAGE_INVALID_MESSAGE = (
    "❌ Invalid language code. Supported: `en`, `fa`, `dar`, `ar`, `zh`, `tr`\n"
    "Example: /language fa"
)

# ──────────────────────────────────────────
# 简报相关消息 / Bulletin-related messages
# ──────────────────────────────────────────

LATEST_LOADING: dict[str, str] = {
    "en":  "⏳ Fetching latest bulletin…",
    "fa":  "⏳ در حال دریافت آخرین خلاصه…",
    "dar": "⏳ در حال گرفتن آخرین خلاصه…",
    "ar":  "⏳ جارٍ جلب آخر نشرة…",
    "zh":  "⏳ 正在获取最新简报…",
    "tr":  "⏳ Son bülten alınıyor…",
}

LATEST_EMPTY: dict[str, str] = {
    "en":  "ℹ️ No new reports in the last 24 hours. Check back later.",
    "fa":  "ℹ️ گزارشی در ۲۴ ساعت گذشته یافت نشد. بعداً دوباره بررسی کنید.",
    "dar": "ℹ️ گزارشی در ۲۴ ساعت گذشته یافت نشد.",
    "ar":  "ℹ️ لا توجد تقارير جديدة في آخر 24 ساعة. تحقق لاحقاً.",
    "zh":  "ℹ️ 过去24小时内没有新报告，请稍后再查。",
    "tr":  "ℹ️ Son 24 saatte yeni rapor yok. Daha sonra tekrar kontrol edin.",
}

# ──────────────────────────────────────────
# 避难所相关消息 / Shelter-related messages
# ──────────────────────────────────────────

SHELTER_NOT_IMPLEMENTED: dict[str, str] = {
    "en":  (
        "🏠 *Shelter Finder — Coming Soon*\n\n"
        "This feature is under development. "
        "For urgent shelter needs:\n"
        "• UNHCR Iran: +98 21 8899 5000\n"
        "• UNHCR Lebanon: +961 1 850 100\n"
        "• IOM: iom.int"
    ),
    "fa":  (
        "🏠 *جستجوی سرپناه — به زودی*\n\n"
        "این ویژگی در دست توسعه است. برای نیازهای فوری:\n"
        "• UNHCR ایران: +98 21 8899 5000\n"
        "• IOM: iom.int"
    ),
    "ar":  (
        "🏠 *البحث عن مأوى — قريباً*\n\n"
        "هذه الميزة قيد التطوير. للاحتياجات العاجلة:\n"
        "• UNHCR لبنان: +961 1 850 100\n"
        "• IOM: iom.int"
    ),
    "zh":  (
        "🏠 *庇护所查询 — 即将上线*\n\n"
        "此功能正在开发中。紧急住所需求请联系：\n"
        "• UNHCR: +961 1 850 100\n"
        "• IOM: iom.int"
    ),
    "dar": (
        "🏠 *جستجوی سرپناه — به زودی*\n\n"
        "این ویژگی در حال توسعه است."
    ),
    "tr":  (
        "🏠 *Barınak Bulucu — Yakında*\n\n"
        "Bu özellik geliştirme aşamasındadır."
    ),
}

# ──────────────────────────────────────────
# 错误消息 / Error messages
# ──────────────────────────────────────────

ERROR_GENERIC: dict[str, str] = {
    "en":  "❌ An error occurred. Please try again later.",
    "fa":  "❌ خطایی رخ داد. لطفاً بعداً دوباره تلاش کنید.",
    "dar": "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.",
    "ar":  "❌ حدث خطأ. يرجى المحاولة مرة أخرى لاحقاً.",
    "zh":  "❌ 发生错误，请稍后重试。",
    "tr":  "❌ Bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
}


# ──────────────────────────────────────────
# 辅助函数 / Helper function
# ──────────────────────────────────────────

def get_message(template: dict[str, str], lang: str, **kwargs: Any) -> str:
    """
    从消息模板中获取指定语言的文本，回退到英文。
    Get a localised message string, falling back to English if lang not found.

    Args:
        template: 语言代码 → 消息字符串的字典。
        lang: 用户偏好的语言代码。
        **kwargs: 格式化参数（如有占位符）。

    Returns:
        格式化后的消息字符串。
    """
    text = template.get(lang) or template.get("en", "")
    if kwargs:
        text = text.format(**kwargs)
    return text
