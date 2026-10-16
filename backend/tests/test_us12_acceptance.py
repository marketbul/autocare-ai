"""User Story 12: damage photos -> severity + body area (M10), with an interim assessor.

The real assessor is a vision model (or later the team's CNN); here a scripted stand-in
returns fixed model replies so the rules around it can be tested."""
from __future__ import annotations

import base64
import json
import unittest
from pathlib import Path

from autocare.accounts import Accounts
from autocare.damage import (OUT_OF_SCOPE, DamageService, PhotoAssessment, VisionDamageAssessor,
                             asks_out_of_scope, combine_damage_reads, combine_photos)
from autocare.scan import ImageRejected, combine_vision_reads, friendly_provider_error
from fixtures import TEST_SETTINGS, build

PHOTO = "data:image/jpeg;base64," + base64.b64encode((Path(__file__).parent / "assets" / "car_panel.jpg").read_bytes()).decode()


def reads(sev_a, loc_a, sev_b, loc_b, clear=True, side="left"):
    a = json.dumps({"is_vehicle_exterior": True, "visible_damage": True, "image_clear": clear,
                    "severity": sev_a, "location": loc_a, "side": side})
    b = json.dumps({"car_visible": True, "damage_visible": True, "can_judge": clear, "part": loc_b, "grade": sev_b})
    return a, b


class Scripted:
    """Stands in for the vision model: replays (reply_A, reply_B) per photo."""
    def __init__(self, *pairs):
        self.replies = [r for p in pairs for r in p]

    def __call__(self, prompt, data_url, json_mode):
        return self.replies.pop(0)


class Story12(unittest.TestCase):
    def setUp(self):
        self.svc, _, self.db = build()
        self.acc = Accounts(self.db, TEST_SETTINGS)
        self.u = self.acc.register_owner("A", "a@example.com", "password123")["user_id"]
        self.v = self.acc.add_vehicle(self.u, "toyota-corolla-2018-xli", 50000)["user_vehicle_id"]

    def run_photos(self, *pairs, note="", n=None):
        ds = DamageService(self.db, self.svc.repo, VisionDamageAssessor(Scripted(*pairs)), 6_000_000)
        return ds.assess(self.v, [PHOTO] * (n or len(pairs)), note)

    def test_ac1_severity_and_body_area(self):
        out = self.run_photos(reads("moderate", "front_bumper", "moderate", "front_bumper"))
        self.assertEqual(out["status"], "assessed")
        self.assertEqual(out["severity"], "moderate")
        self.assertEqual(out["severity_label"], "Moderate")
        self.assertEqual(out["locations"], [{"location": "front_bumper", "label": "Front bumper", "side": "left"}])
        rows = self.db.query("SELECT * FROM damageimage WHERE case_id = :c", {"c": out["case_id"]})
        self.assertEqual((rows[0]["predicted_severity"], rows[0]["predicted_location"]), ("moderate", "front_bumper"))
        self.assertIsNone(rows[0]["file_ref"])           # photo not stored
        self.assertEqual(rows[0]["label_source"], "model:vision")

    def test_ac1_several_photos_worst_severity_all_areas(self):
        out = self.run_photos(reads("minor", "rear_door", "minor", "rear_door"),
                              reads("severe", "rear_quarter_panel", "severe", "rear_quarter_panel"))
        self.assertEqual(out["severity"], "severe")
        self.assertEqual([l["location"] for l in out["locations"]], ["rear_door", "rear_quarter_panel"])

    def test_ac3_inspection_statement_always_present(self):
        for pair in (reads("minor", "bonnet", "minor", "bonnet"), reads("minor", "bonnet", "severe", "roof")):
            out = self.run_photos(pair)
            self.assertIn("physical inspection", out["inspection_note"])

    def test_ac4_unclear_photo_is_inconclusive_not_a_label(self):
        for pair in (reads("minor", "bonnet", "severe", "bonnet"),            # reads disagree
                     reads("moderate", "bonnet", "moderate", "bonnet", clear=False)):
            out = self.run_photos(pair)
            self.assertEqual(out["status"], "inconclusive")
            self.assertIsNone(out["severity"]); self.assertIsNone(out["severity_label"])
            self.assertTrue(any("weren't clear enough" in n for n in out["notices"]))
            self.assertLess(out["confidence"], 0.7)

    def test_ac5_declines_cost_and_fault(self):
        for note in ("how much will this cost to fix?", "who is at fault?", "kitne paise lagenge",
                     "ghalti kis ki hai", "مرمت کا خرچ کتنا ہوگا"):
            self.assertTrue(asks_out_of_scope(note), note)
        self.assertFalse(asks_out_of_scope("scratched it on a gate yesterday"))
        out = self.run_photos(reads("minor", "front_door", "minor", "front_door"), note="How much will it cost?")
        self.assertIn(OUT_OF_SCOPE["en"], out["notices"])
        self.assertNotIn("cost", json.dumps({k: v for k, v in out.items() if k != "notices"}).lower())

    def test_not_a_car_and_no_damage(self):
        not_car = (json.dumps({"is_vehicle_exterior": False}), json.dumps({"car_visible": False}))
        clean = (json.dumps({"is_vehicle_exterior": True, "visible_damage": False}),
                 json.dumps({"car_visible": True, "damage_visible": False}))
        self.assertEqual(self.run_photos(not_car)["status"], "not_vehicle")
        self.assertEqual(self.run_photos(clean)["status"], "no_damage")

    def test_history_shows_damage_check(self):
        self.run_photos(reads("severe", "bonnet", "severe", "bonnet"))
        cases = self.acc.my_cases(self.u)
        self.assertEqual((cases[0]["kind"], cases[0]["severity"]), ("damage", "severe"))
        stats = self.acc.stats()
        self.assertEqual(stats["questions"], 0)          # photo checks aren't counted as questions
        self.assertEqual(stats["damage_photos"], {"severe": 1})

    def test_rejects_bad_uploads(self):
        ds = DamageService(self.db, self.svc.repo, VisionDamageAssessor(Scripted()), 6_000_000)
        with self.assertRaises(ImageRejected):
            ds.assess(self.v, ["data:text/plain;base64,aGVsbG8="])
        with self.assertRaises(ValueError):
            ds.assess(self.v, [PHOTO] * 5)
        with self.assertRaises(ValueError):
            ds.assess(self.v, [])

    def test_combine_rules(self):
        self.assertEqual(combine_damage_reads(*reads("minor", "roof", "minor", "bonnet")).status, "assessed")  # same severity
        self.assertEqual(combine_damage_reads(*reads("minor", "roof", "minor", "flux_capacitor")).status, "inconclusive")
        status, *_ = combine_photos([PhotoAssessment("inconclusive", confidence=0.4), PhotoAssessment("no_damage", confidence=0.9)])
        self.assertEqual(status, "inconclusive")


class ScannerPhotoExtras(unittest.TestCase):
    def test_damage_photo_sent_to_code_reader(self):
        r = combine_vision_reads('{"is_scanner_screen": false, "codes": []}', "a white car with a dent")
        self.assertIn("not a scanner screen", r.notes)

    def test_friendly_errors_hide_provider_details(self):
        msg = friendly_provider_error(RuntimeError('Vision model returned 401: {"error": {"code": "invalid_api_key"}}'))
        self.assertIn("API key", msg); self.assertNotIn("{", msg)


if __name__ == "__main__":
    unittest.main()
