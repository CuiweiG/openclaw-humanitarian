"""
gateway.py — SMS delivery gateway with HMAC source verification.

In adversarial environments, governments send mass SMS messages to
citizens warning against accessing foreign services.  Unverified SMS
from CrisisBridge could be confused with — or used as cover for —
government intimidation messages.

This module implements:
  1. HMAC-SHA256 short codes appended to each SMS, allowing recipients
     to verify the message originated from CrisisBridge.
  2. Brand identifier prefix for visual recognition.
  3. Region-based pause protocol: SMS delivery to Iran (+98) is
     suspended until a secure verification workflow is established.

Status: SCAFFOLD — interface and security protocol defined, no
  carrier integration yet.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# SMS character limit (GSM 7-bit single segment)
SMS_MAX_CHARS = 160

# Brand prefix included in every outbound SMS
BRAND_PREFIX = "[CrisisBridge]"

# Country codes where SMS delivery is PAUSED due to security risks
PAUSED_REGIONS: set[str] = {
    "+98",   # Iran — government SMS intimidation campaigns active
}


@dataclass
class SMSMessage:
    """Outbound SMS with HMAC verification tag."""
    recipient: str          # E.164 phone number
    body: str               # Message content (before signing)
    language: str           # Target language code
    hmac_tag: str = ""      # 8-char hex HMAC short code


def _compute_hmac(body: str, secret: bytes) -> str:
    """
    Compute an 8-character HMAC-SHA256 short code for SMS verification.

    Recipients can verify authenticity by checking this code against
    the published daily key on CrisisBridge's verified channels.
    """
    digest = hmac.new(secret, body.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:8]


def is_region_paused(phone_number: str) -> bool:
    """Check whether SMS delivery is paused for this phone's region."""
    for prefix in PAUSED_REGIONS:
        if phone_number.startswith(prefix):
            return True
    return False


def prepare_sms(body: str, recipient: str, language: str = "en") -> SMSMessage | None:
    """
    Prepare an SMS message with brand prefix and HMAC tag.

    Returns None if the recipient is in a paused region.

    Args:
        body: Raw bulletin text (will be truncated to fit SMS limit).
        recipient: E.164 phone number.
        language: Language code for the message content.

    Returns:
        SMSMessage ready for dispatch, or None if region is paused.
    """
    if is_region_paused(recipient):
        logger.warning(
            "SMS to %s blocked — region paused for security. "
            "See docs/sms-security.md for protocol.",
            recipient[:6] + "***"
        )
        return None

    secret = os.getenv("SMS_HMAC_SECRET", "").encode("utf-8")
    if not secret:
        logger.error("SMS_HMAC_SECRET not configured — cannot sign messages.")
        return None

    # Reserve space for prefix + HMAC tag + separators
    # Format: "[CrisisBridge] <body> [v:abcd1234]"
    overhead = len(BRAND_PREFIX) + len(" ") + len(" [v:12345678]")
    max_body = SMS_MAX_CHARS - overhead
    truncated = body[:max_body]

    full_body = f"{BRAND_PREFIX} {truncated}"
    tag = _compute_hmac(full_body, secret)
    signed_body = f"{full_body} [v:{tag}]"

    return SMSMessage(
        recipient=recipient,
        body=signed_body,
        language=language,
        hmac_tag=tag,
    )
