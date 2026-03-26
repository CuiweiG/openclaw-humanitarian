# Bot API Reference — CrisisBridge

> Telegram Bot: [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)

---

## Commands

### `/start`

**Description:** Initialise the bot and display the welcome message.

**Usage:** `/start`

**Response:** Multilingual welcome message in the user's configured language (default: English), including:
- Project description
- Available commands list
- Emergency contact numbers

**Languages supported:** EN, FA, DAR, AR, ZH, TR

---

### `/latest`

**Description:** Fetch and display the latest humanitarian bulletin from ReliefWeb.

**Usage:** `/latest`

**Flow:**
1. Displays a loading indicator
2. Calls `src/scraper/reliefweb.py` to fetch reports from the last 24 hours
3. Translates the top report to the user's configured language
4. Returns a formatted bulletin with source attribution

**Response format:**
```
🌍 CrisisBridge Bulletin

Date: YYYY-MM-DD
Source: https://reliefweb.int/report/...

---

## 🇮🇷 Persian (فارسی)

[Translated bulletin text, ≤200 words]

*Source: https://reliefweb.int/report/...*

---
```

**Error states:**
- No reports in 24 hours → informational message
- API failure → generic error message with retry suggestion
- Translation failure → fallback to English with error note

---

### `/shelter [location]`

**Description:** Query shelter availability near a specified location.

**Status:** 🔧 Reserved interface — not yet implemented.

**Usage:** `/shelter Beirut`

**Arguments:**
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| location | string | No | City or region name |

**Planned response (future):**
```
🏠 Shelter Information — Beirut

[Name]: [Address]
Capacity: [N] / [Total]
Status: [Available / Full]
Contact: [Phone]
Updated: [timestamp]

Source: IOM DTM
```

**Current response:** Placeholder message with UNHCR/IOM contact numbers.

---

### `/language [code]`

**Description:** Set the user's preferred language for all bot responses.

**Usage:** `/language fa`

**Arguments:**
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| code | string | Yes | Language code (see table below) |

**Supported language codes:**

| Code | Language | Native Name |
|------|----------|-------------|
| `en` | English | English |
| `fa` | Persian (Farsi) | فارسی |
| `dar` | Dari | دری |
| `ar` | Arabic | العربية |
| `zh` | Chinese (Simplified) | 中文 |
| `tr` | Turkish | Türkçe |

**Responses:**
- **Success:** `✅ Language set to [language name].` (in the new language)
- **Invalid code:** Error message with list of valid codes
- **No code provided:** List of available codes with usage example

**Storage:** Language preference is stored in-memory per session. In production, persisted to user database.

---

### `/help`

**Description:** Display help information and command list.

**Usage:** `/help`

**Response:** Formatted help message in user's configured language, including:
- All available commands with descriptions
- Language codes reference
- Contact information

---

## Error Handling

All commands implement consistent error handling:

| Error Type | Response |
|------------|----------|
| API timeout | Generic error message, suggest retry |
| No data available | Informational empty-state message |
| Translation failure | Error note, attempt English fallback |
| Invalid arguments | Usage guidance with examples |

---

## Rate Limits

The bot does not implement its own rate limiting beyond Telegram's built-in limits:
- 30 messages per second globally
- 20 messages per minute per group
- No documented per-user limit for private chats

The upstream ReliefWeb API does not require authentication and has generous rate limits for small-scale usage.

---

## Data Sources

| Source | Endpoint | Update Frequency |
|--------|----------|-----------------|
| ReliefWeb | `https://api.reliefweb.int/v1/reports` | Real-time |
| OCHA (via ReliefWeb) | Same endpoint, source filter | Real-time |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | Bot token from @BotFather |
| `ANTHROPIC_API_KEY` | ⬜ Optional | Claude API key for translation |

---

## Internal Module API

### `src/scraper/reliefweb.fetch_reports()`

```python
def fetch_reports(
    countries: list[str] = ["Iran", "Lebanon"],
    hours_back: int = 24,
    limit: int = 10,
    extra_filters: Optional[list[dict]] = None,
) -> list[dict[str, Any]]
```

Returns: `[{title, summary, date, source, url}, ...]`

### `src/translator/translate.translate_bulletin()`

```python
def translate_bulletin(
    english_text: str,
    target_languages: list[str],
    backend: Optional[TranslationBackend] = None,
    glossary_path: Path = DEFAULT_GLOSSARY_PATH,
    source_url: str = "",
    report_date: str = "",
) -> str
```

Returns: Markdown-formatted multilingual bulletin string.

### `src/translator/quality_check.quality_check()`

```python
def quality_check(
    translated_text: str,
    language: str,
    glossary_path: Path = DEFAULT_GLOSSARY_PATH,
    max_words: int = 200,
) -> QualityReport
```

Returns: `QualityReport` with `.passed`, `.checks`, `.to_markdown()`.
