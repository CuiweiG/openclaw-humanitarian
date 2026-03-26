"""
Mental Health Referral Engine
Routes users to appropriate support based on assessed urgency.

IMPORTANT: This is NOT a clinical tool. It provides information only.
For emergencies, always direct to emergency services (112/911/999).
"""

import re
from typing import Optional
from .helplines import get_helplines

URGENCY_SIGNALS = {
    "crisis": [
        r"suicid", r"kill.*myself", r"want.*to.*die", r"end.*my.*life",
        r"خودکشی", r"می‌خواهم بمیرم",  # Persian
        r"انتحار", r"أريد أن أموت",  # Arabic
    ],
    "high": [
        r"can'?t.*go.*on", r"hopeless", r"no.*reason.*to.*live",
        r"panic", r"severe.*anxiety", r"can'?t.*breathe",
        r"ناامید", r"وحشت",  # Persian
    ],
    "moderate": [
        r"anxious", r"depressed", r"scared", r"can'?t.*sleep",
        r"nightmare", r"flashback", r"stress",
        r"اضطراب", r"افسردگی",  # Persian
    ],
    "low": [
        r"worried", r"sad", r"lonely", r"miss.*family",
        r"tired", r"overwhelmed",
    ],
}


class ReferralEngine:
    """Routes users to appropriate mental health support."""

    def assess_urgency(self, message: str) -> str:
        """Assess urgency from user message.

        Returns: crisis / high / moderate / low

        WARNING: This is keyword-based, not clinical assessment.
        Always err on the side of caution.
        """
        message_lower = message.lower()

        for level in ["crisis", "high", "moderate", "low"]:
            for pattern in URGENCY_SIGNALS[level]:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return level

        return "low"

    def get_referral(self, urgency: str, country: str = "", language: str = "en") -> dict:
        """Get appropriate referral based on urgency level.

        Returns:
            {urgency, action, resources, disclaimer}
        """
        helplines = get_helplines(country, language)

        if urgency == "crisis":
            return {
                "urgency": "crisis",
                "action": "IMMEDIATE: Please contact a crisis helpline NOW.",
                "resources": helplines[:3] if helplines else [{"name": "Emergency", "number": "112"}],
                "disclaimer": "If you or someone you know is in immediate danger, please call emergency services (112/911/999).",
            }
        elif urgency == "high":
            return {
                "urgency": "high",
                "action": "Please reach out to a helpline or counselor today.",
                "resources": helplines,
                "disclaimer": "You are not alone. Professional support is available.",
            }
        elif urgency == "moderate":
            return {
                "urgency": "moderate",
                "action": "Here are some self-help resources and support contacts.",
                "resources": helplines,
                "disclaimer": "It's normal to feel this way during a crisis. Support is available.",
            }
        else:
            return {
                "urgency": "low",
                "action": "Here are some resources that may help.",
                "resources": helplines[:2] if helplines else [],
                "disclaimer": "Taking care of your mental health is important.",
            }
