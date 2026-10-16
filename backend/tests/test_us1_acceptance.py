"""User Story 1: Register Vehicle Profile — one test per acceptance criterion."""
from __future__ import annotations

import datetime as dt
import unittest

from autocare.accounts import Accounts, Invalid
from autocare.service import VehicleProfileRequired
from fixtures import TEST_SETTINGS, build


class Story1(unittest.TestCase):
    def setUp(self):
        self.svc, _, self.db = build()
        self.acc = Accounts(self.db, TEST_SETTINGS)
        self.u = self.acc.register_owner("Ali Owner", "ali@example.com", "password123")["user_id"]

    def test_ac1_profile_saved_and_scopes_answers(self):
        v = self.acc.add_vehicle(self.u, "toyota-corolla-2018-xli", 82000, registration_year=2018,
                                 usage_profile="city")
        self.assertEqual((v["model"], v["variant"], v["year"], v["current_mileage"]), ("Corolla", "XLi", 2018, 82000))
        self.assertEqual((v["registration_year"], v["usage_profile"]), (2018, "city"))
        r = self.svc.diagnose(v["user_vehicle_id"], "grinding noise when braking")
        self.assertEqual(r.vehicle.year, 2018)
        self.assertTrue(all("Civic" not in c.document_name for c in r.citations))

    def test_ac2_unsupported_shown_and_refused(self):
        cat = self.acc.catalog()
        civic = [r for r in cat if r["model"] == "Civic"]
        self.assertTrue(civic and not any(r["supported"] for r in civic))   # visible, greyed out
        swift = [r for r in cat if r["model"] == "Swift"]                   # planned model, no DB rows
        self.assertTrue(swift and all(r["vehicle_id"] is None and not r["supported"] for r in swift))
        self.assertFalse(next(r for r in cat if r["vehicle_id"] == "toyota-corolla-2012-xli")["supported"])
        for vid in ("toyota-corolla-2012-xli", "honda-civic-2018-base", None, "made-up"):
            with self.assertRaises(Invalid):
                self.acc.add_vehicle(self.u, vid, 1000)

    def test_ac3_update_mileage_only(self):
        v = self.acc.add_vehicle(self.u, "toyota-corolla-2018-xli", 82000, registration_year=2019,
                                 usage_profile="mixed")
        w = self.acc.update_vehicle(self.u, v["user_vehicle_id"], mileage=83500)
        self.assertEqual(w["current_mileage"], 83500)
        self.assertEqual(w["last_reading_date"], dt.date.today().isoformat())
        self.assertEqual({k: w[k] for k in ("vehicle_id", "registration_year", "usage_profile")},
                         {"vehicle_id": "toyota-corolla-2018-xli", "registration_year": 2019, "usage_profile": "mixed"})
        with self.assertRaises(Invalid):     # odometers don't go backwards...
            self.acc.update_vehicle(self.u, v["user_vehicle_id"], mileage=8350)
        fixed = self.acc.update_vehicle(self.u, v["user_vehicle_id"], mileage=8350, correction=True)
        self.assertEqual(fixed["current_mileage"], 8350)   # ...unless it's a typo correction
        self.assertEqual(self.acc.update_vehicle(self.u, v["user_vehicle_id"], usage_profile="highway")["usage_profile"], "highway")

    def test_ac4_two_cars_keep_separate_history(self):
        a = self.acc.add_vehicle(self.u, "toyota-corolla-2018-xli", 82000)["user_vehicle_id"]
        b = self.acc.add_vehicle(self.u, "toyota-corolla-2018-xli", 15000)["user_vehicle_id"]
        self.svc.diagnose(a, "grinding noise when braking")
        self.svc.diagnose(b, "engine overheats")
        self.svc.diagnose(b, "P0301")
        cases = self.acc.my_cases(self.u)
        self.assertEqual(sorted(c["user_vehicle_id"] for c in cases), sorted([a, b, b]))
        self.assertEqual([c["question"] for c in cases if c["user_vehicle_id"] == a], ["grinding noise when braking"])

    def test_ac5_no_profile_prompts_registration(self):
        with self.assertRaises(VehicleProfileRequired) as ctx:
            self.svc.diagnose(None, "brake se awaz aati hai")
        self.assertIn("register", ctx.exception.message.lower())

    def test_registration_year_and_usage_validated(self):
        with self.assertRaises(Invalid):
            self.acc.add_vehicle(self.u, "toyota-corolla-2018-xli", 1000, registration_year=2010)
        with self.assertRaises(Invalid):
            self.acc.add_vehicle(self.u, "toyota-corolla-2018-xli", 1000, usage_profile="racing")


if __name__ == "__main__":
    unittest.main()
