"""User Story 12 / module M10: severity and location of VISIBLE exterior damage from photos.

What it does and doesn't do (proposal §7.13, kept on purpose):
* predicts a severity (Minor / Moderate / Severe) and the body area for visible damage;
* never estimates repair cost, never decides fault or liability, never diagnoses
  fluid leaks or the engine bay;
* always says that a physical inspection can find damage a photo can't show;
* low-confidence photos are reported as inconclusive, not given a confident label.

Assessors (AUTOCARE_DAMAGE_ASSESSOR):
* "vision" – the vision model on the LLM endpoint, used as an INTERIM, zero-shot
  assessor until the team's fine-tuned CNN exists. Each photo is assessed twice with
  two differently worded instructions; a label is only trusted when both agree.
  Report it as a baseline, not as the M10 model.
* the M10 CNN (ResNet / EfficientNet fine-tuned by the ML lead) plugs in by
  implementing `assess(image, mime) -> PhotoAssessment`.

Photos are not stored (damageimage.file_ref stays NULL): they can show number plates
and people, and the proposal's consent process for keeping them isn't in place yet.
"""
from __future__ import annotations

import base64
import json
import re
import uuid
from dataclasses import dataclass, field

SEVERITIES = ("minor", "moderate", "severe")
LOCATIONS = ("front_bumper", "rear_bumper", "bonnet", "boot_lid", "roof", "windscreen", "rear_window",
             "front_door", "rear_door", "front_fender", "rear_quarter_panel", "headlamp", "tail_lamp",
             "side_mirror", "wheel_rim", "side_skirt", "other")
SIDES = ("left", "right", "centre", "unknown")
TRUST_THRESHOLD = 0.70
MAX_PHOTOS = 4

SEVERITY_LABEL = {
    "minor": {"en": "Minor", "roman_ur": "Maamooli", "ur": "معمولی"},
    "moderate": {"en": "Moderate", "roman_ur": "Darmiyana", "ur": "درمیانہ"},
    "severe": {"en": "Severe", "roman_ur": "Shadeed", "ur": "شدید"},
}
LOCATION_LABEL = {
    "front_bumper": "Front bumper", "rear_bumper": "Rear bumper", "bonnet": "Bonnet", "boot_lid": "Boot lid",
    "roof": "Roof", "windscreen": "Windscreen", "rear_window": "Rear window", "front_door": "Front door",
    "rear_door": "Rear door", "front_fender": "Front fender", "rear_quarter_panel": "Rear quarter panel",
    "headlamp": "Headlamp", "tail_lamp": "Tail lamp", "side_mirror": "Side mirror", "wheel_rim": "Wheel / rim",
    "side_skirt": "Side skirt", "other": "Other body part",
}

# Labelling protocol (docs/damage_labelling_protocol.md). The same definitions go to the
# vision model and to the people labelling the M10 training set, so both mean the same thing.
SEVERITY_PROTOCOL = (
    "minor = scratches, scuffs, paint chips or small dents; panel shape intact; no part broken or loose. "
    "moderate = clear dents or creases, a cracked or partly detached bumper cover, a broken lamp lens or "
    "mirror, damage across more than one panel; parts likely need repair or replacement but the body "
    "shape is intact. "
    "severe = crushed, torn or folded panels, deformed structure, doors or bonnet out of line, shattered "
    "glass, deployed airbags, or a wheel visibly pushed out of position."
)

PROMPT_A = (
    "You assess VISIBLE exterior damage on a car photo for a car owner. Do not estimate cost, do not "
    "say who is at fault, and do not judge anything you cannot see. Severity scale: " + SEVERITY_PROTOCOL +
    " Body areas: " + ", ".join(LOCATIONS) + ". Sides: left, right, centre, unknown (driver's left/right "
    "when facing forward; unknown if you can't tell). Reply only with JSON: "
    '{"is_vehicle_exterior": true, "visible_damage": true, "image_clear": true, '
    '"severity": "minor|moderate|severe", "location": "<one body area>", "side": "<side>"}. '
    "If the photo is too dark, blurred, too far away or too close to judge, set image_clear to false."
)
PROMPT_B = (
    "Look at this photo. Which single part of the car's body is the most damaged, and how badly? "
    "Choose the part from: " + ", ".join(LOCATIONS) + ". Grade it using exactly these definitions: " +
    SEVERITY_PROTOCOL + " If there is no car, no visible damage, or you can't judge it from this photo, say "
    'so. Reply only with JSON: {"car_visible": true, "damage_visible": true, "can_judge": true, '
    '"part": "<part>", "grade": "minor|moderate|severe"}'
)


@dataclass
class PhotoAssessment:
    status: str                    # assessed | inconclusive | no_damage | not_vehicle
    severity: str | None = None
    location: str | None = None
    side: str = "unknown"
    confidence: float = 0.0
    method: str = "vision"
    notes: list[str] = field(default_factory=list)


def _json(text: str) -> dict:
    try:
        m = re.search(r"\{.*\}", text or "", re.S)
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


def _norm(v, allowed) -> str | None:
    v = str(v or "").strip().lower().replace(" ", "_").replace("-", "_")
    return v if v in allowed else None


def combine_damage_reads(raw_a: str, raw_b: str) -> PhotoAssessment:
    """Trust a label only when two independently worded reads agree."""
    a, b = _json(raw_a), _json(raw_b)
    if a.get("is_vehicle_exterior") is False and b.get("car_visible") is False:
        return PhotoAssessment("not_vehicle", confidence=0.9, notes=["no car exterior in the photo"])
    if a.get("visible_damage") is False and b.get("damage_visible") is False:
        return PhotoAssessment("no_damage", confidence=0.85, notes=["no visible damage"])
    sev_a, sev_b = _norm(a.get("severity"), SEVERITIES), _norm(b.get("grade"), SEVERITIES)
    loc_a, loc_b = _norm(a.get("location"), LOCATIONS), _norm(b.get("part"), LOCATIONS)
    side = _norm(a.get("side"), SIDES) or "unknown"
    notes: list[str] = []
    if not (sev_a and sev_b and loc_a and loc_b):
        return PhotoAssessment("inconclusive", sev_a or sev_b, loc_a or loc_b, side, 0.3,
                               notes=["the model could not give a complete answer"])
    if sev_a == sev_b and loc_a == loc_b:
        conf = 0.9; notes.append("two independent reads agree")
    elif sev_a == sev_b:
        conf = 0.75; notes.append("same severity; the reads named different body areas")
    else:
        conf = 0.4; notes.append(f"the reads disagree on severity ({sev_a} vs {sev_b})")
    if a.get("image_clear") is False or b.get("can_judge") is False:
        conf = min(conf, 0.45); notes.append("photo unclear")
    # On disagreement keep the MORE severe reading as the candidate, but don't trust it.
    severity = sev_a if sev_a == sev_b else max(sev_a, sev_b, key=SEVERITIES.index)
    status = "assessed" if conf >= TRUST_THRESHOLD else "inconclusive"
    return PhotoAssessment(status, severity, loc_a, side, round(conf, 3), notes=notes)


class VisionDamageAssessor:
    method = "vision"

    def __init__(self, chat):
        """`chat(prompt, data_url, json_mode) -> str`; e.g. VisionCodeReader._ask."""
        self.chat = chat

    def assess(self, image: bytes, mime: str) -> PhotoAssessment:
        data_url = f"data:{mime};base64,{base64.b64encode(image).decode()}"
        return combine_damage_reads(self.chat(PROMPT_A, data_url, True), self.chat(PROMPT_B, data_url, True))


def build_damage_assessor(settings):
    from .scan import VisionCodeReader
    if getattr(settings, "damage_assessor", "vision") == "off":
        return None
    if not settings.llm_api_key and "localhost" not in settings.llm_base_url:
        return None
    reader = VisionCodeReader(settings.llm_base_url, settings.llm_api_key, settings.vision_model,
                              settings.llm_timeout_s)
    return VisionDamageAssessor(reader._ask)


# ------------------------------------------------------------------ messages
INSPECTION_NOTE = {
    "en": ("This only describes damage you can see in the photos. A physical inspection can reveal internal "
           "or structural damage that a photo can't show."),
    "roman_ur": ("Yeh sirf photo mein nazar aane wale nuqsan ke baare mein hai. Gaari ka muaina andar ka ya "
                 "dhanche ka woh nuqsan bhi dikha sakta hai jo photo mein nazar nahi aata."),
    "ur": ("یہ صرف تصویروں میں نظر آنے والے نقصان کے بارے میں ہے۔ گاڑی کا معائنہ اندرونی یا ڈھانچے کا وہ "
           "نقصان بھی ظاہر کر سکتا ہے جو تصویر میں نظر نہیں آتا۔"),
}
INCONCLUSIVE = {
    "en": ("The photos weren't clear enough for a reliable assessment, so I won't give a severity. Take the "
           "photo in daylight, about 1–2 metres from the damage, with the whole panel in the frame."),
    "roman_ur": ("Photos itni saaf nahi thin ke yaqeeni andaza lagaya ja sake, is liye main severity nahi "
                 "bataunga. Din ki roshni mein, nuqsan se 1–2 meter door se, poora panel frame mein le kar photo lein."),
    "ur": ("تصویریں اتنی واضح نہیں تھیں کہ قابلِ اعتماد اندازہ لگایا جا سکے، اس لیے میں شدت نہیں بتاؤں گا۔ "
           "دن کی روشنی میں، نقصان سے 1–2 میٹر دور سے، پورا پینل فریم میں لے کر تصویر لیں۔"),
}
OUT_OF_SCOPE = {
    "en": ("I can't estimate repair cost or decide who was at fault from photos. This check only says how "
           "severe the visible damage looks and where it is."),
    "roman_ur": ("Main photos se marammat ka kharcha ya ghalti kis ki thi, yeh nahi bata sakta. Yeh check sirf "
                 "nazar aane wale nuqsan ki shiddat aur jagah batata hai."),
    "ur": ("میں تصویروں سے مرمت کا خرچ یا غلطی کس کی تھی، یہ نہیں بتا سکتا۔ یہ چیک صرف نظر آنے والے نقصان "
           "کی شدت اور جگہ بتاتا ہے۔"),
}
_OUT_OF_SCOPE_RE = re.compile(
    r"\b(cost|price|how much|estimate|quote|rupees|rs\.?|pkr|kharch\w*|kitne paise|qeemat|"
    r"fault|liab\w*|blame|insurance claim|who (hit|is responsible)|ghalti|qasoor)\b|"
    r"خرچ|قیمت|کتنے پیسے|غلطی|قصور", re.I)


def asks_out_of_scope(note: str) -> bool:
    return bool(_OUT_OF_SCOPE_RE.search(note or ""))


@dataclass
class DamageResult:
    case_id: str | None
    status: str                     # assessed | inconclusive | no_damage | not_vehicle
    severity: str | None
    locations: list[dict]
    confidence: float
    photos: list[dict]
    notices: list[str]
    method: str

    def as_dict(self, lang: str) -> dict:
        lab = lambda t, k: t[k].get(lang, t[k]["en"])   # noqa: E731
        return {
            "case_id": self.case_id, "status": self.status, "severity": self.severity,
            "severity_label": lab(SEVERITY_LABEL, self.severity) if self.severity and self.status == "assessed" else None,
            "locations": self.locations, "confidence": self.confidence, "photos": self.photos,
            "notices": self.notices, "method": self.method, "calibrated": False,
            "inspection_note": INSPECTION_NOTE.get(lang, INSPECTION_NOTE["en"]),
        }


def combine_photos(assessments: list[PhotoAssessment]) -> tuple[str, str | None, list[dict], float]:
    trusted = [a for a in assessments if a.status == "assessed"]
    if trusted:
        severity = max((a.severity for a in trusted), key=SEVERITIES.index)
        seen, locations = set(), []
        for a in trusted:
            key = (a.location, a.side)
            if key not in seen:
                seen.add(key)
                locations.append({"location": a.location, "label": LOCATION_LABEL[a.location], "side": a.side})
        return "assessed", severity, locations, round(min(a.confidence for a in trusted), 3)
    if assessments and all(a.status == "not_vehicle" for a in assessments):
        return "not_vehicle", None, [], 0.0
    if assessments and all(a.status in ("no_damage", "not_vehicle") for a in assessments):
        return "no_damage", None, [], round(min(a.confidence for a in assessments), 3)
    return "inconclusive", None, [], round(max((a.confidence for a in assessments), default=0.0), 3)


class DamageService:
    def __init__(self, db, repo, assessor, max_bytes: int):
        self.db, self.repo, self.assessor, self.max_bytes = db, repo, assessor, max_bytes

    def assess(self, user_vehicle_id: str, images: list[str], note: str = "", lang: str = "en") -> dict:
        from .scan import decode_data_url
        from .service import time_ordered_id
        if not images:
            raise ValueError("Add at least one photo.")
        if len(images) > MAX_PHOTOS:
            raise ValueError(f"Add at most {MAX_PHOTOS} photos.")
        vehicle = self.repo.get_vehicle_profile(user_vehicle_id)
        if vehicle is None:
            raise LookupError("vehicle")
        decoded = [decode_data_url(i, self.max_bytes) for i in images]   # validate all before any model call
        notices = [OUT_OF_SCOPE.get(lang, OUT_OF_SCOPE["en"])] if asks_out_of_scope(note) else []

        results = [self.assessor.assess(raw, mime) for raw, mime in decoded]
        status, severity, locations, conf = combine_photos(results)
        if status == "inconclusive":
            notices.append(INCONCLUSIVE.get(lang, INCONCLUSIVE["en"]))

        case_id = time_ordered_id()
        self.repo.insert_diagnostic_case(
            case_id=case_id, user_vehicle_id=vehicle.user_vehicle_id,
            symptom_text=(note or "").strip()[:1000] or f"Damage photo check ({len(images)} photo{'s' if len(images) > 1 else ''})",
            language=lang, code=None, evidence_refs=[], provenance="real",
            predicted_category="body_damage" if status == "assessed" else None,
            confidence=conf if status == "assessed" else None)
        photos = []
        for i, a in enumerate(results):
            self.db.execute("""INSERT INTO damageimage (image_id, case_id, vehicle_id, file_ref, predicted_severity,
                                   predicted_location, model_confidence, label_source, reviewed)
                               VALUES (:i, :c, :v, NULL, :s, :l, :m, :src, :r)""",
                            {"i": str(uuid.uuid4()), "c": case_id, "v": vehicle.vehicle_id,
                             "s": a.severity if a.status == "assessed" else None,
                             "l": a.location if a.status == "assessed" else None,
                             "m": a.confidence, "src": f"model:{a.method}", "r": False})
            photos.append({"index": i + 1, "status": a.status,
                           "severity": a.severity if a.status == "assessed" else None,
                           "location": a.location if a.status == "assessed" else None,
                           "location_label": LOCATION_LABEL.get(a.location) if a.status == "assessed" else None,
                           "side": a.side, "confidence": a.confidence, "notes": a.notes})
        method = results[0].method if results else "none"
        return DamageResult(case_id, status, severity if status == "assessed" else None, locations, conf,
                            photos, notices, method).as_dict(lang)
