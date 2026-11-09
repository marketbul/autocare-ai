"""Data Normalizer and Language Detector for AI Auto Pakistan.

Standardizes multilingual automotive vernacular:
- English, Urdu, Roman Urdu, Punjabi
- Mechanical term normalization (e.g. kangi -> steering rack, chimta -> control arm)
- Sanity checks on costs and manufacturing years.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

_ARABIC_URDU_SCRIPT = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
_PUNJABI_SPECIFIC = frozenset([
    "kiddan", "changa", "aape", "tusi", "asi", "hor", "pya", "karan", "dasso",
    "kithon", "chheti", "painda", "shuru", "veere", "paaji", "gaadi", "chhad"
])
_ROMAN_URDU_SPECIFIC = frozenset([
    "hai", "hain", "nahi", "nahin", "kya", "kia", "kyun", "kaise", "mera", "meri",
    "mere", "mujhe", "apni", "apna", "apne", "ka", "ki", "ke", "ko", "se", "mein",
    "raha", "rahi", "rahe", "hota", "hoti", "gaya", "gayi", "aur", "bhi", "bohat",
    "zyada", "yeh", "woh", "isko", "usko", "karta", "karein", "awaz", "gaari", "garam",
    "dhuan", "batti", "tel", "pani", "jhatka", "kharab", "khatkhat", "seeti", "rukti"
])

# Terminology Normalization Map: (Colloquial Term -> Standardized Automotive Concept)
AUTOMOTIVE_TERM_MAPPING = {
    r"\bgadi\b": "gaari",
    r"\bgaadi\b": "gaari",
    r"\binjan\b": "engine",
    r"\bbreak\b": "brake",
    r"\bbreake\b": "brake",
    r"\bchimta\b": "lower control arm (chimta)",
    r"\bchimte\b": "lower control arms (chimte)",
    r"\bkangi\b": "steering rack (kangi)",
    r"\bchamber\b": "oil pan / sump (chamber)",
    r"\bshocks\b": "shock absorbers",
    r"\bshocker\b": "shock absorber",
    r"\bdilter\b": "filter",
    r"\bself\b": "starter motor (self)",
    r"\bcat\b": "catalytic converter",
    r"\bsilencer\b": "exhaust / silencer",
    r"\btair\b": "tire",
    r"\btyre\b": "tire",
}


def detect_language(text: str) -> str:
    """Detects if text is English, Urdu (script), Roman Urdu, or Punjabi."""
    if not text or not text.strip():
        return "en"

    # 1. Check Urdu Arabic script
    if _ARABIC_URDU_SCRIPT.search(text):
        return "ur"

    words = [w.strip().lower() for w in re.findall(r"\b[A-Za-z]+\b", text)]
    if not words:
        return "en"

    punjabi_matches = sum(1 for w in words if w in _PUNJABI_SPECIFIC)
    roman_ur_matches = sum(1 for w in words if w in _ROMAN_URDU_SPECIFIC)

    if punjabi_matches >= 2:
        return "punjabi"
    if roman_ur_matches >= 2 or (len(words) > 0 and (roman_ur_matches / len(words)) >= 0.15):
        return "roman_ur"

    return "en"


def normalize_automotive_text(text: str) -> str:
    """Standardizes colloquial mechanics terms and spelling variants in text."""
    if not text:
        return ""
    normalized = text
    for pattern, replacement in AUTOMOTIVE_TERM_MAPPING.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    # Collapse excess whitespace
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def validate_price_sanity(price_pkr: Optional[float]) -> Tuple[bool, Optional[str]]:
    """Sanity checks repair cost in Pakistani Rupees (PKR)."""
    if price_pkr is None:
        return True, None
    if price_pkr < 0:
        return False, "Cost cannot be negative"
    if price_pkr == 0:
        return False, "Cost is zero (unspecified or invalid bill)"
    if price_pkr > 15_000_000:
        return False, f"Cost of {price_pkr:,} PKR exceeds passenger vehicle limit (15M PKR)"
    return True, None


def validate_year_sanity(year: Optional[int]) -> Tuple[bool, Optional[str]]:
    """Sanity checks vehicle manufacturing year."""
    if year is None:
        return True, None
    if year < 1960 or year > 2027:
        return False, f"Year {year} is outside valid automotive fleet boundary (1960-2027)"
    return True, None
