"""User Story 4: fault category + repair-urgency level (M2) — acceptance criteria.

The classifier here is trained on the STARTER set with the lite embedder, so these
tests check behaviour and wiring, not accuracy.
"""
from __future__ import annotations

import csv
import unittest

import numpy as np

from autocare.accounts import Accounts
from autocare.service import DiagnoseService
from autocare.triage import (CATEGORIES, URGENCIES, URGENCY_ACTION, TriageClassifier, TriageModel,
                             read_labels, sae_category, train)
from autocare.ml import HashingEmbedder
from fixtures import STARTER_LABELS, TEST_SETTINGS, build, triage_model

CRITICAL_TEXT = "Stop driving immediately — seek assistance; do not continue the journey"


class StubModel(TriageModel):
    """Fixed probabilities, real decision rule."""
    def __init__(self, cat, urg, threshold=0.25):
        super().__init__(None, None, None, threshold, "stub", 1, {"data_fingerprint": "stub", "trained_at": "x"})
        self._cat, self._urg = np.array(cat, float), np.array(urg, float)

    def predict_proba(self, texts, embedder):
        n = len(texts)
        return np.tile(self._cat, (n, 1)), np.tile(self._urg, (n, 1))


def cat(**kw):
    v = np.zeros(len(CATEGORIES))
    for k, p in kw.items():
        v[CATEGORIES.index(k)] = p
    return v


def urg(low=0, moderate=0, high=0, critical=0):
    return [low, moderate, high, critical]


class Story4Service(unittest.TestCase):
    def setUp(self):
        self.svc, _, self.db = build(triage=True)

    def test_ac1_one_category_and_one_urgency_saved_with_case(self):
        r = self.svc.diagnose("uv-corolla", "grinding noise when braking")
        self.assertEqual(r.status, "answered")
        t = r.triage
        self.assertIn(t.category, CATEGORIES)
        self.assertIn(t.urgency, URGENCIES)
        self.assertFalse(t.withheld)
        row = self.db.query("SELECT predicted_category, predicted_urgency, confidence FROM diagnosticcase "
                            "WHERE case_id = :c", {"c": r.case_id})[0]
        self.assertEqual((row["predicted_category"], row["predicted_urgency"]), (t.category, t.urgency))
        self.assertAlmostEqual(row["confidence"], t.category_probability)

    def test_ac2_critical_shows_stop_driving_text(self):
        r = self.svc.diagnose("uv-corolla", "red brake warning light came on while driving")
        self.assertEqual(r.status, "answered")
        self.assertEqual(r.triage.urgency, "critical")
        self.assertEqual(r.triage.action, CRITICAL_TEXT)

    def test_ac3_low_is_calm(self):
        t = TriageClassifier(StubModel(cat(engine=0.9, general=0.1), urg(low=0.8, moderate=0.2)), None)
        out = DiagnoseService._triage_out(t.classify("when is my oil change due"), "en", withheld=False)
        self.assertEqual(out.urgency, "low")
        self.assertEqual(out.action, "Schedule this at your next convenient service.")
        for alarming in ("stop", "immediately", "danger", "urgent"):
            self.assertNotIn(alarming, out.action.lower())

    def test_abstained_answer_withholds_label(self):
        r = self.svc.diagnose("uv-corolla", "how do I pair my bluetooth phone")
        self.assertEqual(r.status, "abstained")
        self.assertTrue(r.triage is None or r.triage.withheld)

    def test_history_hides_labels_of_abstained_cases(self):
        acc = Accounts(self.db, TEST_SETTINGS)
        u = acc.register_owner("A", "a@example.com", "password123")["user_id"]
        v = acc.add_vehicle(u, "toyota-corolla-2018-xli", 1000)["user_vehicle_id"]
        self.svc.diagnose(v, "grinding noise when braking")
        self.svc.diagnose(v, "how do I pair my bluetooth phone")
        by_q = {c["question"]: c for c in acc.my_cases(u)}
        self.assertIsNotNone(by_q["grinding noise when braking"]["urgency"])
        self.assertIsNone(by_q["how do I pair my bluetooth phone"]["urgency"])


class Story4Rules(unittest.TestCase):
    def test_ac4_ambiguous_means_lower_confidence_and_alternatives(self):
        clear = TriageClassifier(StubModel(cat(braking=0.9, engine=0.1), urg(high=1)), None).classify("x")
        vague = TriageClassifier(StubModel(cat(braking=0.42, suspension_steering=0.38, tyres_wheels=0.2),
                                           urg(moderate=1)), None).classify("x")
        self.assertFalse(clear.uncertain)
        self.assertTrue(vague.uncertain)
        self.assertLess(vague.category_probability, clear.category_probability)
        self.assertEqual(vague.alternatives[0][0], "suspension_steering")

    def test_critical_first_rule(self):
        # Critical is not the most likely class, but is above the tuned threshold.
        t = TriageClassifier(StubModel(cat(cooling=1), urg(moderate=0.45, high=0.25, critical=0.30), 0.25), None)
        self.assertEqual(t.classify("x").urgency, "critical")
        t = TriageClassifier(StubModel(cat(cooling=1), urg(moderate=0.45, high=0.35, critical=0.20), 0.25), None)
        self.assertEqual(t.classify("x").urgency, "moderate")

    def test_safety_rules_only_raise(self):
        low = StubModel(cat(general=0.6, braking=0.4), urg(low=1))
        for text in ("my brakes failed on the motorway", "brake fail ho gaye", "بریک فیل ہو گئے",
                     "smoke coming from under the bonnet", "petrol ki boo aa rahi hai",
                     "gaari garam ho rahi hai aur engine se smoke", "tyre burst on the highway"):
            r = TriageClassifier(low, None).classify(text)
            self.assertEqual(r.urgency, "critical", text)
            self.assertTrue(r.safety_flags, text)
            self.assertNotEqual(r.category, "general", text)
        crit = StubModel(cat(engine=1), urg(critical=1))
        self.assertEqual(TriageClassifier(crit, None).classify("strange noise").urgency, "critical")

    def test_no_false_alarm_words(self):
        # "misfire" contains "fire"; "aage" contains "aag"; exhaust smoke is not a bonnet fire.
        low = StubModel(cat(engine=1), urg(moderate=1))
        for text in ("engine misfire at idle", "gaari aage nahi barhti", "blue smoke from the exhaust"):
            self.assertEqual(TriageClassifier(low, None).classify(text).safety_flags, [], text)

    def test_code_reference_decides_category_and_severity_floor(self):
        m = StubModel(cat(general=0.5, electrical=0.5), urg(low=1))
        r = TriageClassifier(m, None).classify("P0301", codes=[
            {"code": "P0301", "description": "Cylinder 1 Misfire Detected", "system": "Ignition", "severity": "high"}])
        self.assertEqual(r.category, "engine")
        self.assertEqual(r.urgency, "high")
        self.assertEqual(sae_category("P0730"), "transmission")
        self.assertIsNone(sae_category("C0035"))   # chassis is ambiguous: no guess

    def test_unrecognised_code_lowers_confidence(self):
        svc, _, _ = build(triage=True)
        known = svc.diagnose("uv-corolla", "P0301 rough idle").triage
        unknown = svc.diagnose("uv-corolla", "P0399 rough idle").triage
        self.assertIsNotNone(unknown)
        self.assertTrue(unknown.uncertain)
        self.assertTrue(any("not in the reference" in b for b in unknown.basis))
        self.assertLessEqual(unknown.category_probability, known.category_probability)


class Story4Languages(unittest.TestCase):
    def test_ac5_same_symptom_same_labels_across_languages(self):
        """With the English rendering available (LLM pivot), all three phrasings agree."""
        rows = read_labels(STARTER_LABELS)
        groups: dict[str, dict] = {}
        for r in rows:
            groups.setdefault(r["group_id"], {})[r["language"]] = r["text"]
        tc = TriageClassifier(triage_model(), HashingEmbedder())
        agree = 0
        sample = list(groups.values())[::4]
        for g in sample:
            en = g["en"]
            got = {(t.category, t.urgency) for t in
                   (tc.classify(en), tc.classify(g["roman_ur"], english=en), tc.classify(g["ur"], english=en))}
            agree += len(got) == 1
        self.assertGreaterEqual(agree / len(sample), 0.8)

    def test_training_report_has_required_metrics(self):
        rows = read_labels(STARTER_LABELS)
        _, rep = train(rows, HashingEmbedder(), "lite", folds=3)
        for key in ("critical_false_negative_rate", "by_language", "cross_language_consistency", "urgency", "category"):
            self.assertIn(key, rep)
        self.assertEqual(set(rep["by_language"]), {"en", "roman_ur", "ur"})
        self.assertGreaterEqual(rep["critical_threshold"], 0.15)   # never "stop driving" for everything

    def test_threshold_prefers_critical_recall(self):
        from autocare.triage import tune_critical_threshold
        oof = np.array([[0, 0, .6, .4], [0, 0, .7, .3], [.9, .1, 0, 0], [.6, .2, .2, 0]])
        y = ["critical", "critical", "low", "high"]
        self.assertEqual(tune_critical_threshold(oof, y, 0.95), 0.3)   # catches both criticals

    def test_starter_set_is_flagged_synthesised(self):
        with open(STARTER_LABELS, encoding="utf-8") as f:
            self.assertTrue(all(r["synthesised"] == "yes" and r["reviewed"] == "no" for r in csv.DictReader(f)))


if __name__ == "__main__":
    unittest.main()
