"""User Story 4 / module M2: fault category + repair urgency from a symptom description.

Three parts, each visible in the result's `basis` so the trace says what decided:

1. Trained classifier: two logistic-regression heads (category, urgency) over
   [character TF-IDF of the text | sentence embedding of the text]. The embedding
   is the same BGE-M3 model retrieval uses, so Urdu, Roman Urdu and English
   phrasings of one symptom land close together. When the question was not in
   English, the LLM's English search query is classified too and the two
   probability vectors are averaged (consistency across languages, AC5).
2. Critical-first decision rule (proposal §7.1): Critical is chosen whenever
   P(critical) >= a threshold tuned on out-of-fold predictions for high Critical
   recall, not only when it is the most likely class.
3. Safety rules: a short, reviewed list of hazard phrases (brake failure,
   smoke, fuel leak, overheating, oil pressure, steering lock, tyre burst) in
   all three languages. They can only RAISE urgency, never lower it.
   A diagnostic code's `severity` in the reference table is a floor too.

Probabilities here are raw classifier outputs. Calibration (temperature / Platt
scaling) and the abstention gate belong to M3 / Story 5.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import logging
import pickle
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

log = logging.getLogger("autocare.triage")

CATEGORIES = ("engine", "transmission", "braking", "electrical", "cooling",
              "suspension_steering", "tyres_wheels", "general")
URGENCIES = ("low", "moderate", "high", "critical")
NOT_A_FAULT = "general"

CATEGORY_LABEL = {
    "engine": {"en": "Engine and combustion", "roman_ur": "Engine aur combustion", "ur": "انجن اور کمبسچن"},
    "transmission": {"en": "Transmission", "roman_ur": "Transmission (gear system)", "ur": "ٹرانسمیشن (گیئر سسٹم)"},
    "braking": {"en": "Braking system", "roman_ur": "Brake system", "ur": "بریک سسٹم"},
    "electrical": {"en": "Electrical", "roman_ur": "Electrical system", "ur": "الیکٹریکل سسٹم"},
    "cooling": {"en": "Cooling system", "roman_ur": "Cooling system", "ur": "کولنگ سسٹم"},
    "suspension_steering": {"en": "Suspension and steering", "roman_ur": "Suspension aur steering", "ur": "سسپنشن اور اسٹیئرنگ"},
    "tyres_wheels": {"en": "Tyres and wheels", "roman_ur": "Tyres aur pahiye", "ur": "ٹائر اور پہیے"},
    "general": {"en": "General question", "roman_ur": "Aam sawal", "ur": "عام سوال"},
}
URGENCY_LABEL = {
    "low": {"en": "Low", "roman_ur": "Kam", "ur": "کم"},
    "moderate": {"en": "Moderate", "roman_ur": "Darmiyana", "ur": "درمیانہ"},
    "high": {"en": "High", "roman_ur": "Zyada", "ur": "زیادہ"},
    "critical": {"en": "Critical", "roman_ur": "Intehai sangeen", "ur": "انتہائی سنگین"},
}
# Proposal Table 5. The Critical text is fixed by Story 4 AC2.
URGENCY_ACTION = {
    "low": {"en": "Schedule this at your next convenient service.",
            "roman_ur": "Isay agli munasib service par karwa lein.",
            "ur": "اسے اگلی مناسب سروس پر کروا لیں۔"},
    "moderate": {"en": "Have it inspected soon, within the next two weeks.",
                 "roman_ur": "Jald muaina karwayen, agle do hafton ke andar.",
                 "ur": "جلد معائنہ کروائیں، اگلے دو ہفتوں کے اندر۔"},
    "high": {"en": "Limit driving and arrange an inspection promptly.",
             "roman_ur": "Gaari kam chalayen aur foran muaina karwayen.",
             "ur": "گاڑی کم چلائیں اور فوراً معائنہ کروائیں۔"},
    "critical": {"en": "Stop driving immediately — seek assistance; do not continue the journey",
                 "roman_ur": "Foran gaari rok dein — madad hasil karein; safar jaari na rakhein.",
                 "ur": "فوراً گاڑی روک دیں — مدد حاصل کریں؛ سفر جاری نہ رکھیں۔"},
}

# Thresholds for showing uncertainty (AC4). Untuned; set with Story 5.
UNCERTAIN_TOP = 0.55
UNCERTAIN_MARGIN = 0.20
ALTERNATIVE_MIN = 0.15


# ---------------------------------------------------------------- safety rules
@dataclass(frozen=True)
class SafetyRule:
    name: str
    pattern: re.Pattern
    urgency: str
    category: str
    reason: str


def _rx(*parts: str) -> re.Pattern:
    return re.compile("|".join(parts), re.IGNORECASE)


# Reviewed by: (fill in — mechanic / team). Keep this list short and specific:
# each rule must describe an immediate hazard, in all three languages.
SAFETY_RULES: tuple[SafetyRule, ...] = (
    SafetyRule("brake_failure", _rx(
        r"\bbrakes?\b.{0,20}\b(fail(ed|ure)?|not working|don'?t work|stopped working|gone)\b",
        r"pedal.{0,30}(to|touches) the floor", r"\b(car|vehicle) (does not|doesn'?t|won'?t|will not) stop\b",
        r"\bbrake\b.{0,15}\b(fail|nahi lag|kaam nahi)", r"gaa?ri nahi ruk",
        r"بریک.{0,15}(فیل|کام نہیں|نہیں لگ)", r"گاڑی نہیں رک"),
        "critical", "braking", "brake failure"),
    SafetyRule("red_brake_light", _rx(
        r"\b(red|lal|laal)\b.{0,25}\bbrake\b.{0,15}\b(light|lamp|warning)",
        r"\bbrake\b.{0,10}\b(warning )?(light|lamp)\b.{0,25}\b(red|lal|laal)\b",
        r"(سرخ|لال).{0,25}بریک", r"بریک.{0,25}(سرخ|لال)"),
        "critical", "braking", "red brake warning light"),
    SafetyRule("smoke_or_fire", _rx(
        r"\b(fire|flames?|aag)\b",
        r"\b(smoke|dhuan|dhuwan|dhuaan)\b.{0,30}\b(bonnet|hood|engine bay|under|dashboard|neeche)\b",
        r"\b(bonnet|hood|dashboard)\b.{0,30}\b(smoke|dhuan|dhuwan)\b",
        r"\bengine\b.{0,12}\b(se|from)\b.{0,6}\b(smoke|dhuan|dhuwan)\b",
        r"آگ|شعلے", r"(بونٹ|ڈیش ?بورڈ).{0,30}دھواں"),
        "critical", "engine", "smoke or fire under the bonnet"),
    SafetyRule("electrical_burning", _rx(
        r"\b(burning|jalne)\b.{0,25}\b(plastic|wires?|wiring)\b",
        r"\b(plastic|wiring|wire)\b.{0,25}\b(burning|jalne|jal rahi)\b",
        r"(پلاسٹک|وائرنگ|تار).{0,25}جل"),
        "critical", "electrical", "burning wiring smell"),
    SafetyRule("fuel_leak", _rx(
        r"\b(petrol|fuel|gasoline|gas)\b.{0,30}\b(leak|leaking|smell|boo)\b",
        r"\b(smell|boo)\b.{0,15}\b(of )?(petrol|fuel|gasoline)\b",
        r"پیٹرول.{0,30}(لیک|بو)", r"بو.{0,10}پیٹرول"),
        "critical", "engine", "fuel leak or fuel smell"),
    SafetyRule("oil_pressure", _rx(r"\boil pressure\b", r"آئل پریشر"),
        "critical", "engine", "oil pressure warning"),
    SafetyRule("overheating", _rx(
        r"\boverheat", r"\btemp(erature)?\b.{0,30}\b(red|lal|laal)\b",
        r"\b(steam|bhaap|bhap)\b", r"\bengine\b.{0,20}\bgaram\b", r"\bgaa?ri\b.{0,12}\bgaram\b",
        r"بھاپ", r"(ٹمپریچر|درجہ حرارت).{0,30}(سرخ|لال)", r"انجن.{0,20}گرم"),
        "critical", "cooling", "engine overheating"),
    SafetyRule("steering_lock", _rx(
        r"\bsteering\b.{0,30}\b(lock(ed)?|jam(med)?|won'?t turn|will not turn|cannot steer|ghoom nahi)\b",
        r"\bcan'?t steer\b", r"اسٹیئرنگ.{0,30}(لاک|جام|گھوم نہیں)"),
        "critical", "suspension_steering", "loss of steering"),
    SafetyRule("tyre_or_wheel", _rx(
        r"\b(tyre|tire)\b.{0,20}\b(burst|blew|blow ?out|phat)", r"\bwheel\b.{0,30}\b(loose|wobbl\w*|coming off)\b",
        r"\b(wheel )?nuts?\b.{0,15}\b(loose|dheel\w*)\b", r"\bpahiya\b.{0,20}\bhil",
        r"ٹائر.{0,20}پھٹ", r"پہیہ.{0,20}ہل", r"نٹ.{0,15}ڈھیل"),
        "critical", "tyres_wheels", "tyre burst or loose wheel"),
)


def safety_matches(text: str) -> list[SafetyRule]:
    return [r for r in SAFETY_RULES if r.pattern.search(text or "")]


# ----------------------------------------------------------- code priors
# SAE J2012 structure: letter = system; for P0/P2 codes the 3rd character is the subgroup.
def sae_category(code: str) -> str | None:
    code = (code or "").upper()
    if len(code) != 5:
        return None
    letter, sub = code[0], code[2]
    if letter == "P":
        if sub in "012345":   # fuel/air metering, ignition/misfire, emissions, idle/speed
            return "engine"
        if sub == "6":
            return "electrical"   # computer / output circuits
        if sub in "789":
            return "transmission"
        return None
    if letter in "BU":        # body, network
        return "electrical"
    return None               # C = chassis: brakes OR steering OR suspension — ambiguous


_SYSTEM_WORDS = (
    ("braking", ("brake", "abs")), ("transmission", ("transmission", "gear", "clutch", "cvt")),
    ("cooling", ("cooling", "coolant", "radiator", "thermostat")),
    ("suspension_steering", ("steering", "suspension", "eps")),
    ("tyres_wheels", ("tire", "tyre", "wheel", "tpms")),
    ("electrical", ("electrical", "battery", "charging", "network", "body", "computer", "can bus")),
    ("engine", ("engine", "ignition", "misfire", "fuel", "emission", "air", "idle", "oxygen", "catalyst")),
)


def system_category(system: str | None) -> str | None:
    s = (system or "").lower()
    for cat, words in _SYSTEM_WORDS:
        if any(w in s for w in words):
            return cat
    return None


# ------------------------------------------------------------------ model
def _norm(text: str) -> str:
    return " ".join((text or "").lower().split())


@dataclass
class TriageModel:
    vectorizer: object
    category_clf: object
    urgency_clf: object
    critical_threshold: float
    embedding_model: str
    embedding_dim: int
    meta: dict = field(default_factory=dict)
    dense_weight: float = 1.0

    def _features(self, texts: list[str], embedder):
        from scipy.sparse import csr_matrix, hstack
        sparse = self.vectorizer.transform([_norm(t) for t in texts])
        dense = np.asarray(embedder.encode(list(texts)), dtype=np.float64) * self.dense_weight
        return hstack([sparse, csr_matrix(dense)]).tocsr()

    def predict_proba(self, texts: list[str], embedder) -> tuple[np.ndarray, np.ndarray]:
        X = self._features(texts, embedder)
        cat = _full_proba(self.category_clf, X, CATEGORIES)
        urg = _full_proba(self.urgency_clf, X, URGENCIES)
        return cat, urg

    def decide_urgency(self, urg_probs: np.ndarray) -> int:
        crit = URGENCIES.index("critical")
        if urg_probs[crit] >= self.critical_threshold:
            return crit
        rest = urg_probs.copy()
        rest[crit] = -1.0
        return int(np.argmax(rest))

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: str | Path) -> "TriageModel":
        with open(path, "rb") as f:
            return pickle.load(f)


def _full_proba(clf, X, classes: tuple[str, ...]) -> np.ndarray:
    """predict_proba re-indexed to the fixed class order (missing classes -> 0)."""
    p = clf.predict_proba(X)
    out = np.zeros((X.shape[0], len(classes)))
    for j, c in enumerate(clf.classes_):
        out[:, classes.index(c)] = p[:, j]
    return out


# -------------------------------------------------------------- training
def read_labels(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("text") or "").strip()]
    bad = [r for r in rows if r["category"] not in CATEGORIES or r["urgency"] not in URGENCIES]
    if bad:
        raise ValueError(f"{len(bad)} rows have an unknown category/urgency, e.g. {bad[0]}")
    for r in rows:
        r.setdefault("group_id", r.get("example_id") or r["text"])
    return rows


def data_fingerprint(rows: list[dict]) -> str:
    h = hashlib.sha256()
    for r in rows:
        h.update(f"{r['text']}|{r['category']}|{r['urgency']}\n".encode("utf-8"))
    return h.hexdigest()[:16]


def _fit(texts, cats, urgs, embedder, embedding_model, *, critical_weight: float, C: float):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1, sublinear_tf=True)
    vec.fit([_norm(t) for t in texts])
    model = TriageModel(vec, None, None, 0.5, embedding_model, int(embedder.dim))
    X = model._features(texts, embedder)
    model.category_clf = LogisticRegression(C=C, max_iter=3000, class_weight="balanced").fit(X, cats)
    # Asymmetric cost (proposal §7.1): a missed Critical is the costliest error.
    w = np.array([critical_weight if u == "critical" else 1.0 for u in urgs])
    counts = {u: urgs.count(u) for u in set(urgs)}
    w = w * np.array([len(urgs) / (len(counts) * counts[u]) for u in urgs])   # balanced
    model.urgency_clf = LogisticRegression(C=C, max_iter=3000).fit(X, urgs, sample_weight=w)
    return model


class _CachedEmbedder:
    def __init__(self, inner, texts: list[str]):
        self.inner, self.dim = inner, int(inner.dim)
        uniq = list(dict.fromkeys(texts))
        self.cache = dict(zip(uniq, np.asarray(inner.encode(uniq))))

    def encode(self, texts: list[str]) -> np.ndarray:
        missing = [t for t in dict.fromkeys(texts) if t not in self.cache]
        if missing:
            self.cache.update(zip(missing, np.asarray(self.inner.encode(missing))))
        return np.stack([self.cache[t] for t in texts])


def train(rows: list[dict], embedder, embedding_model: str, *, folds: int = 5,
          critical_recall_target: float = 0.95, critical_weight: float = 2.0,
          C: float = 4.0) -> tuple[TriageModel, dict]:
    """Fit on all rows; tune the Critical threshold on grouped out-of-fold predictions.

    Folds are grouped by `group_id`, so the Urdu / Roman Urdu / English versions of
    one symptom are never split between training and validation."""
    from sklearn.model_selection import GroupKFold

    texts = [r["text"] for r in rows]
    embedder = _CachedEmbedder(embedder, texts)   # embed each text once, not once per fold
    cats = [r["category"] for r in rows]
    urgs = [r["urgency"] for r in rows]
    groups = [r["group_id"] for r in rows]
    n_groups = len(set(groups))
    k = max(2, min(folds, n_groups))

    oof_cat = np.zeros((len(rows), len(CATEGORIES)))
    oof_urg = np.zeros((len(rows), len(URGENCIES)))
    for tr, te in GroupKFold(n_splits=k).split(texts, cats, groups):
        m = _fit([texts[i] for i in tr], [cats[i] for i in tr], [urgs[i] for i in tr], embedder,
                 embedding_model, critical_weight=critical_weight, C=C)
        c, u = m.predict_proba([texts[i] for i in te], embedder)
        oof_cat[te], oof_urg[te] = c, u

    threshold = tune_critical_threshold(oof_urg, urgs, critical_recall_target)
    model = _fit(texts, cats, urgs, embedder, embedding_model, critical_weight=critical_weight, C=C)
    model.critical_threshold = threshold
    embedder = embedder.inner
    report = evaluate(oof_cat, oof_urg, rows, threshold)
    model.meta = {
        "trained_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "examples": len(rows), "groups": n_groups, "folds": k,
        "data_fingerprint": data_fingerprint(rows),
        "synthesised_share": round(sum(1 for r in rows if (r.get("synthesised") or "").lower() == "yes")
                                   / max(1, len(rows)), 3),
        "critical_recall_target": critical_recall_target, "critical_weight": critical_weight, "C": C,
        "cv": report,
    }
    return model, report


def tune_critical_threshold(oof_urg: np.ndarray, urgs: list[str], target: float,
                            miss_cost: float = 5.0, floor: float = 0.15) -> float:
    """Pick the Critical threshold on out-of-fold predictions.

    Highest threshold that meets the Critical-recall target; if none does, the
    threshold with the lowest cost when a missed Critical costs `miss_cost` false
    alarms. Never below `floor`, so a weak model can't turn every answer into
    "stop driving" (alarm fatigue is a safety problem too)."""
    crit = URGENCIES.index("critical")
    is_crit = np.array([u == "critical" for u in urgs])
    if not is_crit.any():
        return 0.5
    p = oof_urg[:, crit]
    grid = np.round(np.arange(0.60, floor - 1e-9, -0.01), 2)
    for t in grid:
        if (p[is_crit] >= t).mean() >= target:
            return float(t)
    costs = [(miss_cost * (p[is_crit] < t).sum() + (p[~is_crit] >= t).sum(), -t) for t in grid]
    return float(-min(costs)[1])


def evaluate(cat_p: np.ndarray, urg_p: np.ndarray, rows: list[dict], threshold: float) -> dict:
    from sklearn.metrics import precision_recall_fscore_support

    def decide(p):
        crit = URGENCIES.index("critical")
        if p[crit] >= threshold:
            return "critical"
        q = p.copy(); q[crit] = -1
        return URGENCIES[int(np.argmax(q))]

    pc = [CATEGORIES[int(np.argmax(p))] for p in cat_p]
    pu = [decide(p) for p in urg_p]
    yc = [r["category"] for r in rows]
    yu = [r["urgency"] for r in rows]

    def per_class(y, yhat, labels):
        p, r, f, s = precision_recall_fscore_support(y, yhat, labels=list(labels), zero_division=0)
        return {l: {"precision": round(float(a), 3), "recall": round(float(b), 3), "f1": round(float(c), 3),
                    "support": int(d)} for l, a, b, c, d in zip(labels, p, r, f, s)}

    crit_idx = [i for i, y in enumerate(yu) if y == "critical"]
    by_lang: dict[str, dict] = {}
    for lang in sorted({r.get("language", "?") for r in rows}):
        idx = [i for i, r in enumerate(rows) if r.get("language", "?") == lang]
        by_lang[lang] = {"n": len(idx),
                         "category_accuracy": round(sum(pc[i] == yc[i] for i in idx) / len(idx), 3),
                         "urgency_accuracy": round(sum(pu[i] == yu[i] for i in idx) / len(idx), 3)}
    groups: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        groups.setdefault(r["group_id"], []).append(i)
    multi = [g for g in groups.values() if len(g) > 1]
    consistent = sum(1 for g in multi if len({pc[i] for i in g}) == 1 and len({pu[i] for i in g}) == 1)
    return {
        "category_accuracy": round(sum(a == b for a, b in zip(pc, yc)) / len(rows), 3),
        "urgency_accuracy": round(sum(a == b for a, b in zip(pu, yu)) / len(rows), 3),
        "category": per_class(yc, pc, CATEGORIES),
        "urgency": per_class(yu, pu, URGENCIES),
        "critical_false_negative_rate": round(sum(pu[i] != "critical" for i in crit_idx) / len(crit_idx), 3)
        if crit_idx else None,
        "critical_predicted_low": sum(pu[i] == "low" for i in crit_idx),
        "critical_threshold": threshold,
        "by_language": by_lang,
        "cross_language_consistency": round(consistent / len(multi), 3) if multi else None,
    }


# ------------------------------------------------------------ inference
@dataclass
class Triage:
    category: str
    urgency: str | None
    category_probability: float
    urgency_probability: float | None
    alternatives: list[tuple[str, float]]
    uncertain: bool
    basis: list[str]
    safety_flags: list[str]
    model_version: str | None

    @property
    def is_fault(self) -> bool:
        return self.category != NOT_A_FAULT or bool(self.safety_flags)


class TriageClassifier:
    def __init__(self, model: TriageModel | None, embedder):
        self.model, self.embedder = model, embedder

    def classify(self, text: str, *, english: str | None = None,
                 codes: list[dict] | None = None) -> Triage:
        """`english`: the LLM's English rendering of a non-English question.
        `codes`: DiagnosticCode rows found for codes in the question."""
        basis: list[str] = []
        codes = codes or []
        code_only = bool(codes) and len(re.sub(r"[PBCUpbcu][0-3][0-9A-Fa-f]{3}", " ", text).split()) <= 2

        # The text that describes the problem: a bare code is described by its reference entry.
        texts = [text]
        if english and english.strip().lower() != text.strip().lower():
            texts.append(english)
        if code_only:
            texts = [". ".join(x for x in (c.get("description"), c.get("symptoms")) if x)
                     for c in codes if c.get("description")] or texts

        if self.model is not None:
            cat_p, urg_p = self.model.predict_proba(texts, self.embedder)
            cat_p, urg_p = cat_p.mean(axis=0), urg_p.mean(axis=0)
            basis.append("classifier" + (" (question + English rendering)" if len(texts) > 1 and not code_only else ""))
        else:
            cat_p = np.full(len(CATEGORIES), 1.0 / len(CATEGORIES))
            urg_p = np.full(len(URGENCIES), 1.0 / len(URGENCIES))
            basis.append("no trained classifier loaded")

        # Diagnostic-code reference: the code's system decides the category for a bare code.
        for c in codes:
            cat = system_category(c.get("system")) or sae_category(c.get("code", ""))
            if cat and code_only:
                boost = np.zeros(len(CATEGORIES)); boost[CATEGORIES.index(cat)] = 1.0
                cat_p = 0.3 * cat_p + 0.7 * boost
                basis.append(f"code {c['code']}: {'system' if system_category(c.get('system')) else 'SAE code group'} → {cat}")

        order = np.argsort(-cat_p)
        category = CATEGORIES[int(order[0])]
        top, second = float(cat_p[order[0]]), float(cat_p[order[1]])
        uncertain = top < UNCERTAIN_TOP or (top - second) < UNCERTAIN_MARGIN
        alternatives = [(CATEGORIES[int(i)], round(float(cat_p[i]), 3)) for i in order[1:3]
                        if cat_p[i] >= ALTERNATIVE_MIN]

        u_idx = self.model.decide_urgency(urg_p) if self.model is not None else URGENCIES.index("moderate")
        urgency = URGENCIES[u_idx]
        urgency_p = float(urg_p[u_idx])
        if self.model is not None and urgency == "critical" and urg_p[u_idx] < max(urg_p):
            basis.append(f"critical-first rule (P(critical)={urg_p[u_idx]:.2f} ≥ {self.model.critical_threshold:.2f})")

        # Floors: code severity and safety rules can only raise urgency.
        for c in codes:
            sev = (c.get("severity") or "").strip().lower()
            if sev in URGENCIES and URGENCIES.index(sev) > URGENCIES.index(urgency):
                urgency = sev
                basis.append(f"code {c['code']} severity in reference: {sev}")
        if code_only and not any((c.get("severity") or "").strip().lower() in URGENCIES for c in codes):
            uncertain = True   # urgency rests on the code's short description only
            basis.append("code has no severity in the reference: urgency from its description")
        flags = []
        for rule in safety_matches(" ".join([text, english or ""])):
            flags.append(rule.reason)
            if URGENCIES.index(rule.urgency) > URGENCIES.index(urgency):
                urgency = rule.urgency
                basis.append(f"safety rule: {rule.reason}")
            if category == NOT_A_FAULT or uncertain:
                if category != rule.category:
                    basis.append(f"category from safety rule: {rule.category}")
                category = rule.category

        if category == NOT_A_FAULT and not flags:
            return Triage(category, None, round(top, 3), None, alternatives, uncertain, basis, [],
                          self.version)
        return Triage(category, urgency, round(top, 3), round(urgency_p, 3), alternatives, uncertain,
                      basis, flags, self.version)

    @property
    def version(self) -> str | None:
        if self.model is None:
            return None
        m = self.model.meta
        return f"triage-{m.get('data_fingerprint', '?')}-{m.get('trained_at', '?')[:10]}"


def load_or_train(model_path: str | Path, data_path: str | Path, embedder, embedding_model: str
                  ) -> TriageModel | None:
    """Use the saved model if it was trained with this embedding model on this data;
    otherwise train now (a few hundred rows: seconds to a minute) and save it."""
    path, data = Path(model_path), Path(data_path)
    if not data.exists():
        log.warning("No triage training data at %s; urgency classification disabled.", data)
        return None
    rows = read_labels(data)
    if path.exists():
        try:
            m = TriageModel.load(path)
            if (m.embedding_model == embedding_model and m.embedding_dim == int(embedder.dim)
                    and m.meta.get("file_fingerprint") == data_fingerprint(rows)):
                return m
            log.info("Triage model is stale (embedder or data changed); retraining.")
        except Exception:
            log.warning("Could not load %s; retraining.", path, exc_info=True)
    log.info("Training triage classifier on %d examples...", len(rows))
    model, report = train(rows, embedder, embedding_model)
    model.meta["file_fingerprint"] = data_fingerprint(rows)
    log.info("Triage CV: category acc %.2f, urgency acc %.2f, critical FN rate %s",
             report["category_accuracy"], report["urgency_accuracy"], report["critical_false_negative_rate"])
    try:
        model.save(path)
    except OSError:
        log.warning("Could not save triage model to %s", path, exc_info=True)
    return model
