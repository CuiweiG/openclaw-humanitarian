"""
trust_scorer.py — Source credibility scoring engine.

Assigns a trust tier and display label to each information source
based on organizational authority, verification history, and known
editorial independence.  Designed to run downstream of the
translation pipeline so every pushed bulletin carries a visible
credibility tag.

Tier definitions (aligned with humanitarian information standards):

  T1  ★★★★  UN agencies / OCHA / UNHCR / official flash updates
  T2  ★★★   ICRC / MSF / established INGOs with field presence
  T3  ★★    Regional journalists / verified local NGOs
  T4  ★     State-affiliated media (labelled, never suppressed)
  T0  —     Unknown / unclassified source

Design choice: state media is *labelled* rather than *blocked* to
maintain transparency and avoid creating an information vacuum that
pushes users toward completely unverified channels.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


class TrustTier(IntEnum):
    """Numeric trust tier — higher is more trusted."""
    UNKNOWN = 0
    STATE_MEDIA = 1
    REGIONAL = 2
    INGO = 3
    UN_OFFICIAL = 4


@dataclass(frozen=True)
class TrustScore:
    """Immutable credibility assessment for a single source."""
    tier: TrustTier
    label: str          # human-readable tag, e.g. "★★★★ UN Official"
    emoji_label: str    # compact version for Telegram / SMS
    source_name: str    # normalized source identifier
    note: str = ""      # optional context, e.g. "state-affiliated"


# ──────────────────────────────────────────
# Pattern-based source classification
# ──────────────────────────────────────────
# Each tuple: (compiled regex, TrustTier, display name, optional note)

_RULES: list[tuple[re.Pattern, TrustTier, str, str]] = [
    # T1 — UN system
    (re.compile(r"ocha|reliefweb|un\s?hcr|unicef|wfp|who\.int|iom\b|unrwa", re.I),
     TrustTier.UN_OFFICIAL, "UN Official", ""),
    # T2 — Established INGOs
    (re.compile(r"icrc|msf|doctors without borders|m[ée]decins sans fronti[èe]res|"
                r"oxfam|save the children|nrc\b|irc\b|acted\b|mercy corps", re.I),
     TrustTier.INGO, "Verified INGO", ""),
    # T4 — Known state-affiliated outlets (labelled, not blocked)
    (re.compile(r"irna\b|press\s?tv|tasnim|fars\s?news|irib|"
                r"sana\b|al-?manar|al-?alam", re.I),
     TrustTier.STATE_MEDIA, "State-Affiliated Media",
     "state-affiliated — verify independently"),
    # T3 — Regional / semi-verified (catch-all for known regional outlets)
    (re.compile(r"al-?jazeera|bbc\s?arabic|france\s?24|reuters|ap\s?news|afp", re.I),
     TrustTier.REGIONAL, "Regional / Wire Service", ""),
]

_TIER_LABELS: dict[TrustTier, str] = {
    TrustTier.UN_OFFICIAL: "📋 ★★★★",
    TrustTier.INGO:        "📋 ★★★",
    TrustTier.REGIONAL:    "📋 ★★",
    TrustTier.STATE_MEDIA: "📋 ★",
    TrustTier.UNKNOWN:     "📋 —",
}


def score_source(source_text: str) -> TrustScore:
    """
    Score a source string and return a TrustScore.

    Args:
        source_text: free-text source identifier — URL, org name, or
                     byline as extracted by the scraper pipeline.

    Returns:
        TrustScore with tier, labels, and optional notes.
    """
    if not source_text:
        return TrustScore(
            tier=TrustTier.UNKNOWN,
            label="Unknown Source",
            emoji_label=_TIER_LABELS[TrustTier.UNKNOWN],
            source_name="unknown",
        )

    for pattern, tier, name, note in _RULES:
        if pattern.search(source_text):
            return TrustScore(
                tier=tier,
                label=f"{_TIER_LABELS[tier]} {name}",
                emoji_label=_TIER_LABELS[tier],
                source_name=name,
                note=note,
            )

    # Fallback — unclassified
    logger.info("Unclassified source: %s", source_text[:80])
    return TrustScore(
        tier=TrustTier.UNKNOWN,
        label=f"{_TIER_LABELS[TrustTier.UNKNOWN]} Unverified",
        emoji_label=_TIER_LABELS[TrustTier.UNKNOWN],
        source_name=source_text[:60],
    )


def format_trust_tag(score: TrustScore, lang: str = "en") -> str:
    """
    Format a human-readable trust tag for inclusion in a bulletin.

    Args:
        score: TrustScore from score_source().
        lang: target language code (for future i18n of labels).

    Returns:
        Single-line trust tag string.
    """
    tag = f"{score.emoji_label} Source: {score.source_name}"
    if score.note:
        tag += f" ({score.note})"
    return tag
