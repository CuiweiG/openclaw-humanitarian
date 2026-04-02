"""
routing.py — GPS-free geographic routing for offline bulletin delivery.

Iran's government conducts large-scale GPS jamming, causing ~30% packet
loss on satellite connections and rendering GPS-dependent routing
unreliable.  This module provides degraded-mode geolocation using:

  1. Cell Tower ID (MCC/MNC/LAC/CID) → governorate mapping
  2. Manual governorate selection by the user
  3. Static lookup tables (no GPS hardware required)

The routing granularity is deliberately coarse (governorate / province
level) to protect user privacy — we never attempt to locate individuals.

Status: SCAFFOLD — lookup tables defined for Iran (31 provinces),
  Afghanistan, Lebanon, Syria.  No Cell Tower database integration yet.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Region:
    """Coarse geographic region for bulletin routing."""
    country_code: str     # ISO 3166-1 alpha-2
    governorate: str      # Province / governorate name (English)
    local_name: str       # Name in local script
    language_codes: list[str]  # Primary languages spoken in this region


# ──────────────────────────────────────────
# Static region lookup tables
# ──────────────────────────────────────────

IRAN_PROVINCES: dict[str, Region] = {
    "tehran":     Region("IR", "Tehran",     "تهران",      ["fa"]),
    "isfahan":    Region("IR", "Isfahan",    "اصفهان",     ["fa"]),
    "fars":       Region("IR", "Fars",       "فارس",       ["fa"]),
    "khuzestan":  Region("IR", "Khuzestan",  "خوزستان",    ["fa", "ar"]),
    "kurdistan":  Region("IR", "Kurdistan",  "کردستان",    ["fa", "ku"]),
    "kermanshah": Region("IR", "Kermanshah", "کرمانشاه",   ["fa", "ku"]),
    "sistan":     Region("IR", "Sistan-Baluchestan", "سیستان و بلوچستان", ["fa", "ps"]),
    "khorasan_r": Region("IR", "Razavi Khorasan", "خراسان رضوی", ["fa", "dar"]),
    # ... remaining 23 provinces to be added
}

AFGHANISTAN_PROVINCES: dict[str, Region] = {
    "kabul":      Region("AF", "Kabul",      "کابل",       ["dar", "ps"]),
    "herat":      Region("AF", "Herat",      "هرات",       ["dar"]),
    "kandahar":   Region("AF", "Kandahar",   "کندهار",     ["ps"]),
    "nangarhar":  Region("AF", "Nangarhar",  "ننگرهار",    ["ps"]),
    "balkh":      Region("AF", "Balkh",      "بلخ",        ["dar"]),
    # ... remaining provinces to be added
}

LEBANON_GOVERNORATES: dict[str, Region] = {
    "beirut":     Region("LB", "Beirut",     "بيروت",      ["ar"]),
    "south":      Region("LB", "South Lebanon", "الجنوب",   ["ar"]),
    "nabatieh":   Region("LB", "Nabatieh",   "النبطية",    ["ar"]),
    "bekaa":      Region("LB", "Bekaa",      "البقاع",     ["ar"]),
    "mount_leb":  Region("LB", "Mount Lebanon", "جبل لبنان", ["ar"]),
    "north":      Region("LB", "North Lebanon", "الشمال",   ["ar"]),
    "akkar":      Region("LB", "Akkar",      "عكار",       ["ar"]),
    "baalbek":    Region("LB", "Baalbek-Hermel", "بعلبك الهرمل", ["ar"]),
}

SYRIA_GOVERNORATES: dict[str, Region] = {
    "aleppo":     Region("SY", "Aleppo",     "حلب",        ["ar", "ku"]),
    "damascus":   Region("SY", "Damascus",   "دمشق",       ["ar"]),
    "idlib":      Region("SY", "Idlib",      "إدلب",       ["ar"]),
    "hasakah":    Region("SY", "Al-Hasakah", "الحسكة",     ["ar", "ku"]),
    "raqqa":      Region("SY", "Raqqa",      "الرقة",       ["ar"]),
    "deir_ezzor": Region("SY", "Deir ez-Zor","دير الزور",   ["ar"]),
    # ... remaining governorates to be added
}

# Combined lookup
ALL_REGIONS: dict[str, dict[str, Region]] = {
    "IR": IRAN_PROVINCES,
    "AF": AFGHANISTAN_PROVINCES,
    "LB": LEBANON_GOVERNORATES,
    "SY": SYRIA_GOVERNORATES,
}


def resolve_region(
    country_code: str,
    governorate_key: str = "",
    cell_tower_id: str = "",
) -> Region | None:
    """
    Resolve a geographic region without GPS.

    Priority:
      1. Direct governorate key lookup
      2. Cell Tower ID mapping (TODO)
      3. None — require manual selection

    Args:
        country_code: ISO 3166-1 alpha-2.
        governorate_key: Normalized province/governorate key.
        cell_tower_id: MCC-MNC-LAC-CID string (future).

    Returns:
        Region if resolved, None if manual selection needed.
    """
    country_regions = ALL_REGIONS.get(country_code.upper())
    if not country_regions:
        logger.warning("No region data for country: %s", country_code)
        return None

    if governorate_key:
        region = country_regions.get(governorate_key.lower())
        if region:
            return region
        logger.info("Unknown governorate '%s' in %s", governorate_key, country_code)

    if cell_tower_id:
        # TODO: implement Cell Tower ID → governorate mapping
        # This requires a MCC/MNC database (e.g. OpenCellID)
        logger.info("Cell tower routing not yet implemented: %s", cell_tower_id)

    return None
