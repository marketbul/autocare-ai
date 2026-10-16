"""Tokenisation and diagnostic-trouble-code (DTC) handling."""
from __future__ import annotations

import re

# SAE J2012 format: system letter (P/B/C/U), then 0-3, then three hex digits.
DTC_RE = re.compile(r"(?<![A-Za-z0-9])([PBCUpbcu][0-3][0-9A-Fa-f]{3})(?![A-Za-z0-9])")
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)

EN_STOPWORDS = frozenset(
    """a an the and or but if of to in on at by for with from as is are was were be been being
    it its this that these those my your our their i you we they he she me him her them do does
    did doing have has had what why how when where which who whom can could should would will
    shall may might must not no so than too very just also there here about into over under
    then once again any some such only own same few more most other each both all up down out off
    am""".split()
)

# Roman-Urdu function words: dropped from keyword matching (they carry no
# technical meaning), but used by language detection.
ROMAN_URDU_STOPWORDS = frozenset(
    """hai hain hay he ha tha thi thay the nahi nahin nai na kya kia kyun kyon kyu kese kaise
    kaisay mera meri mere meray mujhe mujhy humari hamari ap aap apni apna apne ka ki ke ko se sy
    say mein mai mn raha rahi rahe rha rhi rhe ho hota hoti hotay hoti hogaya hogyi hogayi
    gaya gayi gai gya gyi wala wali walay aur or bhi jab tab ab abhi phir pehle baad liye lye
    kuch sab bohat bahut buhat zyada ziada kam par pe yeh ye woh wo is us isko usko kar karta
    karti karte karna karein kiya lagta lagti lag lagay aa aata aati ata ati jata jati deta deti
    rahta rahti waqt waqat dafa""".split()
)

STOPWORDS = EN_STOPWORDS | ROMAN_URDU_STOPWORDS


def extract_dtcs(text: str) -> list[str]:
    seen: list[str] = []
    for m in DTC_RE.finditer(text or ""):
        code = m.group(1).upper()
        if code not in seen:
            seen.append(code)
    return seen


def raw_tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def _light_stem(tok: str) -> str:
    # Plural-s only; keeps DTCs and short tokens intact.
    if len(tok) > 4 and tok.endswith("s") and not tok.endswith("ss") and not DTC_RE.fullmatch(tok):
        return tok[:-1]
    return tok


def tokenize(text: str) -> list[str]:
    """Keyword tokens for BM25. DTCs survive as single tokens ("p0301")."""
    return [_light_stem(t) for t in raw_tokens(text) if t not in STOPWORDS and len(t) > 1]
