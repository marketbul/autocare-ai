"""User Story 3: read diagnostic trouble codes from a photo of an OBD-II scanner screen.

The photo is processed in memory and never stored (proposal §9: photos can show
surroundings; scanner photos are not needed after the code is read).

Two readers, chosen with AUTOCARE_CODE_READER:

* "vision"    – the vision model on the same OpenAI-compatible endpoint as the LLM
                (Groq, OpenAI, ...). The photo is read TWICE with two different
                instructions: once "list the codes", once "transcribe the screen".
                Confidence comes from whether the two independent reads agree, not
                from the model saying it is sure.
* "tesseract" – local OCR (needs the Tesseract program + `pip install pytesseract`).
                Confidence is Tesseract's own per-word confidence.

Either way the result is only accepted when confidence >= READ_THRESHOLD; otherwise
the owner is asked to retype or retake the photo (AC3). Nothing is "corrected"
silently: if an O had to be read as 0, confidence drops.
"""
from __future__ import annotations

import base64
import io
import json
import logging
import re
from dataclasses import dataclass, field

from .text import DTC_RE

log = logging.getLogger("autocare.scan")

READ_THRESHOLD = 0.80
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
# Characters OCR often confuses with digits. Only applied in digit positions 2-5,
# and only where the character can't be valid there anyway.
_DIGIT_FIX = {"O": "0", "Q": "0", "D": "0", "I": "1", "L": "1", "|": "1", "S": "5", "Z": "2", "G": "6", "T": "7"}
_HEX = set("0123456789ABCDEF")
_CANDIDATE = re.compile(r"(?<![A-Za-z0-9])([PBCUpbcu][0-9A-Za-z|]{4})(?![A-Za-z0-9])")


class ImageRejected(ValueError):
    pass


@dataclass
class Reading:
    codes: list[str]
    confidence: float
    method: str
    notes: list[str] = field(default_factory=list)


def decode_data_url(data_url: str, max_bytes: int) -> tuple[bytes, str]:
    m = re.match(r"^data:(image/[a-z+.-]+);base64,(.+)$", (data_url or "").strip(), re.S)
    if not m:
        raise ImageRejected("Send the photo as a JPEG, PNG or WebP image.")
    mime = m.group(1).lower()
    if mime not in ALLOWED_TYPES:
        raise ImageRejected("Send the photo as a JPEG, PNG or WebP image.")
    try:
        raw = base64.b64decode(m.group(2), validate=False)
    except ValueError:
        raise ImageRejected("The photo could not be read. Try taking it again.")
    if len(raw) > max_bytes:
        raise ImageRejected(f"The photo is too large (max {max_bytes // 1_000_000} MB).")
    if len(raw) < 100:
        raise ImageRejected("The photo is empty.")
    return raw, mime


def codes_in_text(text: str) -> tuple[list[str], bool]:
    """Codes in OCR text. Returns (codes, any_character_was_fixed)."""
    found: list[str] = []
    fixed = False
    for m in _CANDIDATE.finditer((text or "").upper()):
        tok = m.group(1)
        if DTC_RE.fullmatch(tok):
            code = tok
        else:
            chars, changes = list(tok), 0
            for i in range(1, 5):
                if chars[i] not in _HEX and chars[i] in _DIGIT_FIX:
                    chars[i] = _DIGIT_FIX[chars[i]]
                    changes += 1
            code = "".join(chars)
            # One doubtful character at most; "BOOST" must not become B0057.
            if changes > 1 or not DTC_RE.fullmatch(code):
                continue
            fixed = True
        if code not in found:
            found.append(code)
    return found, fixed


# ------------------------------------------------------------------ readers
LIST_PROMPT = (
    "First decide whether this photo shows the screen of an OBD-II scanner or diagnostic tool "
    "(or a fault code written down). If it does not, reply {\"is_scanner_screen\": false, \"codes\": []}. "
    "Otherwise list every diagnostic trouble code shown "
    "(format: a letter P, B, C or U followed by four characters, e.g. P0301). Copy the "
    "characters exactly as shown. Do not guess, complete or correct a code. If any code is "
    "partly hidden, blurred or unclear, set readable to false. Reply only with JSON: "
    '{"is_scanner_screen": true, "codes": ["..."], "readable": true}'
)
TRANSCRIBE_PROMPT = ("Transcribe all text visible on this screen exactly, line by line. "
                     "Write [unclear] for any character you cannot read. No explanations.")


class VisionCodeReader:
    method = "vision"

    def __init__(self, base_url: str, api_key: str, model: str, timeout_s: float = 60.0):
        self.base_url, self.api_key = base_url.rstrip("/"), api_key
        self.model, self.timeout_s = model, timeout_s

    def _ask(self, prompt: str, data_url: str, json_mode: bool) -> str:
        import httpx
        payload = {"model": self.model, "temperature": 0, "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data_url}}]}]}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        r = httpx.post(f"{self.base_url}/chat/completions", json=payload, headers=headers,
                       timeout=self.timeout_s)
        if r.status_code >= 400:
            raise RuntimeError(f"Vision model returned {r.status_code}: {r.text[:300]}")
        return r.json()["choices"][0]["message"]["content"] or ""

    def read(self, image: bytes, mime: str) -> Reading:
        data_url = f"data:{mime};base64,{base64.b64encode(image).decode()}"
        listed_raw = self._ask(LIST_PROMPT, data_url, json_mode=True)
        transcript = self._ask(TRANSCRIBE_PROMPT, data_url, json_mode=False)
        return combine_vision_reads(listed_raw, transcript)


def combine_vision_reads(listed_raw: str, transcript: str) -> Reading:
    notes: list[str] = []
    try:
        m = re.search(r"\{.*\}", listed_raw or "", re.S)
        obj = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        obj = {}
    listed, fixed_a = codes_in_text(" ".join(str(c) for c in obj.get("codes") or []))
    readable = bool(obj.get("readable", True))
    if obj.get("is_scanner_screen") is False and not listed:
        return Reading([], 0.9, "vision", ["not a scanner screen"])
    seen, fixed_b = codes_in_text(transcript)
    unclear_marks = "[unclear]" in (transcript or "").lower()

    a, b = set(listed), set(seen)
    if not a and not b:
        conf = 0.9 if readable and not unclear_marks else 0.3
        return Reading([], conf, "vision", ["no code visible"])
    if a == b:
        conf = 0.95
        notes.append("two independent reads agree")
    elif a & b:
        conf = 0.5
        notes.append("the two reads only partly agree")
    else:
        conf = 0.3
        notes.append("the two reads disagree")
    if not readable:
        conf = min(conf, 0.4); notes.append("model reported unclear characters")
    if unclear_marks:
        conf = min(conf, 0.5); notes.append("transcript has unclear characters")
    if fixed_a or fixed_b:
        conf *= 0.85; notes.append("a letter had to be read as a digit")
    codes = listed + [c for c in seen if c not in listed] if conf >= READ_THRESHOLD else sorted(a | b)
    return Reading(codes, round(conf, 3), "vision", notes)


def _tesseract_cmd() -> str:
    import os
    import shutil
    env = os.getenv("AUTOCARE_TESSERACT_CMD")
    if env:
        return env
    win = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    return shutil.which("tesseract") or (win if os.path.exists(win) else "tesseract")


def _tesseract_words(img) -> list[tuple[str, float]]:
    """(word, confidence 0-100) via the tesseract program's TSV output."""
    import os
    import subprocess
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        img.save(path)
        out = subprocess.run([_tesseract_cmd(), path, "stdout", "--psm", "6", "tsv"],
                             capture_output=True, text=True, timeout=60, check=True).stdout
    finally:
        os.remove(path)          # the photo is never kept
    words = []
    for line in out.splitlines()[1:]:
        cols = line.split("\t")
        if len(cols) >= 12 and cols[11].strip():
            words.append((cols[11].strip(), float(cols[10])))
    return words


class TesseractCodeReader:
    """Needs the Tesseract program (Windows installer: github.com/UB-Mannheim/tesseract/wiki).
    Set AUTOCARE_TESSERACT_CMD if it isn't on PATH or in the default install folder."""
    method = "tesseract"

    def read(self, image: bytes, mime: str) -> Reading:
        from PIL import Image, ImageOps

        img = ImageOps.exif_transpose(Image.open(io.BytesIO(image))).convert("L")
        if max(img.size) < 1600:
            f = 1600 / max(img.size)
            img = img.resize((int(img.width * f), int(img.height * f)))
        img = ImageOps.autocontrast(img)
        best: Reading | None = None
        for variant in (img, ImageOps.invert(img)):        # dark and light scanner screens
            words = _tesseract_words(variant)
            codes, confs, fixed = [], [], False
            for w, c in words:
                got, fx = codes_in_text(w)
                for code in got:
                    if code not in codes:
                        codes.append(code); confs.append(max(c, 0) / 100.0); fixed |= fx
            if codes:
                conf = min(confs) * (0.85 if fixed else 1.0)
                r = Reading(codes, round(conf, 3), "tesseract",
                            ["a letter had to be read as a digit"] if fixed else [])
            else:
                text_conf = [c for _, c in words if c >= 0]
                conf = (sum(text_conf) / len(text_conf) / 100.0) if text_conf else 0.0
                r = Reading([], round(conf, 3), "tesseract", ["no code visible"])
            if best is None or (r.codes and (not best.codes or r.confidence > best.confidence)):
                best = r
        return best or Reading([], 0.0, "tesseract", ["no text found"])


def build_code_reader(settings):
    if settings.code_reader == "off":
        return None
    if settings.code_reader == "tesseract":
        return TesseractCodeReader()
    if settings.code_reader == "vision":
        if not settings.llm_api_key and "localhost" not in settings.llm_base_url:
            log.warning("AUTOCARE_CODE_READER=vision needs AUTOCARE_LLM_API_KEY; photo reading disabled.")
            return None
        return VisionCodeReader(settings.llm_base_url, settings.llm_api_key, settings.vision_model,
                                settings.llm_timeout_s)
    raise ValueError(f"Unknown AUTOCARE_CODE_READER: {settings.code_reader!r}")


# ------------------------------------------------------------- service
READ_OK = {
    "en": "Read from your photo. Check it matches the screen, then look it up.",
    "roman_ur": "Aap ki photo se parha gaya. Screen se mila lein, phir dekhein.",
    "ur": "آپ کی تصویر سے پڑھا گیا۔ اسکرین سے ملا لیں، پھر دیکھیں۔",
}
READ_UNCLEAR = {
    "en": ("I couldn't read the code reliably from this photo, so I won't guess. Please type the "
           "code, or take a clearer photo: fill the frame with the screen, avoid glare and hold steady."),
    "roman_ur": ("Is photo se code yaqeeni taur par nahi parha ja saka, is liye main andaza nahi "
                 "lagaunga. Code type karein, ya saaf photo lein: screen poori frame mein ho, chamak na ho."),
    "ur": ("اس تصویر سے کوڈ یقینی طور پر نہیں پڑھا جا سکا، اس لیے میں اندازہ نہیں لگاؤں گا۔ "
           "کوڈ ٹائپ کریں، یا صاف تصویر لیں: اسکرین پوری فریم میں ہو اور چمک نہ ہو۔"),
}
NOT_SCANNER = {
    "en": ("This doesn't look like a scanner screen. Take a photo of the scanner's display showing the code. "
           "For a photo of body damage, use Damage check instead."),
    "roman_ur": ("Yeh scanner ki screen nahi lagti. Scanner ki screen ki photo lein jis par code ho. "
                 "Gaari ke nuqsan ki photo ke liye Damage check istemal karein."),
    "ur": ("یہ اسکینر کی اسکرین نہیں لگتی۔ اسکینر کی اسکرین کی تصویر لیں جس پر کوڈ ہو۔ "
           "گاڑی کے نقصان کی تصویر کے لیے ڈیمج چیک استعمال کریں۔"),
}
READ_NONE = {
    "en": "No fault code is visible in this photo. If the scanner shows one, take the photo again or type it.",
    "roman_ur": "Is photo mein koi fault code nazar nahi aa raha. Dobara photo lein ya code type karein.",
    "ur": "اس تصویر میں کوئی فالٹ کوڈ نظر نہیں آ رہا۔ دوبارہ تصویر لیں یا کوڈ ٹائپ کریں۔",
}


def read_codes(reader, repo, data_url: str, max_bytes: int, lang: str = "en") -> dict:
    image, mime = decode_data_url(data_url, max_bytes)
    reading = reader.read(image, mime)
    if "not a scanner screen" in reading.notes:
        status, table = "not_scanner", NOT_SCANNER
    elif reading.codes and reading.confidence >= READ_THRESHOLD:
        status, table = "read", READ_OK
    elif not reading.codes and reading.confidence >= READ_THRESHOLD:
        status, table = "no_code", READ_NONE
    else:
        status, table = "unclear", READ_UNCLEAR
    known = {r["code"]: r for r in repo.get_codes(reading.codes)} if status == "read" else {}
    return {
        "status": status,
        # Codes are only returned when the read is trusted; an unclear read returns none,
        # so the UI can't pre-fill a guess.
        "codes": [{"code": c, "known": c in known, "description": (known.get(c) or {}).get("description")}
                  for c in (reading.codes if status == "read" else [])],
        "confidence": reading.confidence, "method": reading.method, "notes": reading.notes,
        "message": table.get(lang, table["en"]),
    }


def friendly_provider_error(exc: Exception) -> str:
    """Owner-facing text for a vision-provider failure; details stay in the server log."""
    t = str(exc)
    if " 401" in t or "invalid_api_key" in t:
        return "The server's API key is not valid. Ask the admin to check AUTOCARE_LLM_API_KEY."
    if " 404" in t or "model_not_found" in t or "does not exist" in t:
        return "The photo model isn't available. Ask the admin to check AUTOCARE_VISION_MODEL."
    if " 429" in t or "rate" in t.lower():
        return "Too many photo checks right now. Wait a minute and try again."
    if " 413" in t:
        return "The photo is too large. Try a smaller one."
    return "The photo service didn't respond. Try again in a moment."
