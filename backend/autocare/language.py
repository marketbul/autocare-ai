"""Query language detection (en / ur / roman_ur) and cross-lingual query expansion.

Detection is rule-based on purpose: Urdu script is unambiguous, and Roman Urdu
is recognised by function words that do not occur in English sentences.
Mixed Roman-Urdu/English queries (AC4) are classified as roman_ur, so the
answer comes back in the register the owner actually typed.

Expansion appends English equivalents of common Urdu / Roman-Urdu automotive
words to the retrieval query. The corpus (owner manuals, SAE J2012 list) is in
English, so BM25 cannot match "awaz" to "noise" on its own; the multilingual
embedding model handles meaning, this handles the keyword side.
"""
from __future__ import annotations

import re

from .text import raw_tokens

LANG_EN, LANG_UR, LANG_ROMAN_UR = "en", "ur", "roman_ur"
LANGUAGE_NAMES = {LANG_EN: "English", LANG_UR: "Urdu", LANG_ROMAN_UR: "Roman Urdu"}

_ARABIC_SCRIPT = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
_LETTER = re.compile(r"[^\W\d_]", re.UNICODE)

# Words that mark Roman Urdu and essentially never appear in English text.
ROMAN_URDU_MARKERS = frozenset(
    """hai hain nahi nahin nai kya kia kyun kyon kyu kese kaise kaisay mera meri mere meray
    mujhe mujhy humari hamari aap apni apna apne ka ki ke ko se sy mein mai raha rahi rahe rha
    rhi rhe hota hoti hotay hogaya hogyi hogayi gaya gayi gai gya gyi wala wali walay aur bhi
    jab tab abhi phir pehle baad liye lye kuch bohat bahut buhat zyada ziada yeh woh isko usko
    karta karti karte karna karein kiya lagta lagti lagay aata aati jata jati deta deti rahta
    rahti waqt waqat dafa awaz aawaz gaari gari gaadi gadi garam garm dhuan dhuwan batti tel
    pani jhatka jhatkay jhatke kharab kharabi theek thik chalate chalatay chalane chalti rukti
    khatkhat seeti tapak dabane dabata dabati""".split()
)

# Roman Urdu token -> English retrieval terms.
ROMAN_GLOSSARY: dict[str, str] = {
    "awaz": "noise sound", "aawaz": "noise sound", "awaaz": "noise sound",
    "gaari": "vehicle", "gari": "vehicle", "gaadi": "vehicle", "gadi": "vehicle",
    "garam": "overheat overheating hot temperature", "garm": "overheat overheating hot temperature",
    "thanda": "cold", "thandi": "cold",
    "dhuan": "smoke exhaust", "dhuwan": "smoke exhaust", "dhuaan": "smoke exhaust",
    "batti": "light indicator warning", "tel": "oil", "tail": "oil",
    "pani": "coolant water", "jhatka": "jerk vibration shaking", "jhatkay": "jerk vibration shaking",
    "jhatke": "jerk vibration shaking", "dhakka": "jerk", "hilti": "vibration shaking",
    "hil": "vibration shaking", "kampan": "vibration",
    "kharab": "fault malfunction", "kharabi": "fault malfunction",
    "khatkhat": "knocking noise", "khatak": "knocking", "seeti": "whistle squeal",
    "cheekh": "squeal", "tapak": "leak drip", "tapakna": "leak", "rissav": "leak",
    "rukti": "stall", "ruk": "stall stop", "injan": "engine", "silencer": "exhaust muffler",
    "tair": "tire", "tyre": "tire", "pahiya": "wheel", "chabi": "key",
    "dabane": "press pressing", "dabata": "press", "dabati": "press",
    "chalate": "driving", "chalatay": "driving", "chalane": "driving", "chalti": "running",
    "breake": "brake", "break": "brake", "brakes": "brake",
}

# Urdu-script substring -> English retrieval terms.
URDU_GLOSSARY: dict[str, str] = {
    "آواز": "noise sound", "گاڑی": "vehicle", "گرم": "overheat overheating hot temperature",
    "ٹھنڈ": "cold", "دھواں": "smoke exhaust", "بتی": "light indicator warning",
    "لائٹ": "light indicator warning", "تیل": "oil", "آئل": "oil", "پانی": "coolant water",
    "جھٹک": "jerk vibration shaking", "ہلتی": "vibration shaking", "کمپن": "vibration",
    "بریک": "brake", "انجن": "engine", "ٹائر": "tire", "پہی": "wheel", "بیٹری": "battery",
    "اسٹیئرنگ": "steering", "سٹیئرنگ": "steering", "لیک": "leak", "ٹپک": "leak drip",
    "خراب": "fault malfunction", "سٹارٹ": "start", "اسٹارٹ": "start", "گیئر": "gear transmission",
    "کلچ": "clutch", "پٹرول": "fuel petrol", "ایندھن": "fuel", "چیخ": "squeal",
    "سیٹی": "whistle squeal", "ایئر بیگ": "airbag", "ائیر بیگ": "airbag",
    "دھکا": "jerk", "سائلنسر": "exhaust muffler", "اے سی": "air conditioning",
    "ریڈی ایٹر": "radiator coolant", "چابی": "key",
}


def detect_language(text: str) -> str:
    letters = _LETTER.findall(text or "")
    if letters:
        arabic = sum(1 for ch in letters if _ARABIC_SCRIPT.match(ch))
        if arabic / len(letters) >= 0.3:
            return LANG_UR
    words = [t for t in raw_tokens(text) if not t.isdigit()]
    hits = sum(1 for t in words if t in ROMAN_URDU_MARKERS)
    if hits >= 2 or (hits == 1 and len(words) <= 4):
        return LANG_ROMAN_UR
    return LANG_EN


def expansion_terms(text: str, language: str) -> str:
    """English terms to append to the retrieval query ('' for English queries)."""
    terms: list[str] = []
    if language == LANG_UR:
        for key, eng in URDU_GLOSSARY.items():
            if key in text:
                terms.append(eng)
    if language in (LANG_UR, LANG_ROMAN_UR):
        for tok in raw_tokens(text):
            if tok in ROMAN_GLOSSARY:
                terms.append(ROMAN_GLOSSARY[tok])
    seen, out = set(), []
    for word in " ".join(terms).split():
        if word not in seen:
            seen.add(word)
            out.append(word)
    return " ".join(out)
