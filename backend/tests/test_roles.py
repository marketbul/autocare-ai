"""Accounts, roles, owner garage/history, mechanic submissions, admin review."""
from __future__ import annotations

import time
import unittest

from autocare.accounts import Accounts, Invalid, NotFound
from autocare.auth import make_token, read_token
from autocare.ml import HashingEmbedder
from autocare.service import id_timestamp_ms, time_ordered_id
from fixtures import TEST_SETTINGS, build

KEY = b"test-key"


class Tokens(unittest.TestCase):
    def test_roundtrip_and_tamper(self):
        t = make_token("u1", "owner", KEY)
        self.assertEqual(read_token(t, KEY)["sub"], "u1")
        self.assertIsNone(read_token(t, b"other-key"))
        payload, sig = t.split(".")
        forged = make_token("u1", "admin", b"attacker").split(".")[0] + "." + sig
        self.assertIsNone(read_token(forged, KEY))

    def test_expired(self):
        self.assertIsNone(read_token(make_token("u1", "owner", KEY, ttl_s=-1), KEY))

    def test_time_ordered_ids(self):
        a = time_ordered_id(); time.sleep(0.002); b = time_ordered_id()
        self.assertLess(a, b)
        self.assertAlmostEqual(id_timestamp_ms(b) / 1000, time.time(), delta=5)


class Roles(unittest.TestCase):
    def setUp(self):
        self.svc, self.llm, self.db = build()
        self.acc = Accounts(self.db, TEST_SETTINGS)
        self.owner = self.acc.register_owner("Ali Owner", "ali@example.com", "password123")
        self.other = self.acc.register_owner("Sara Owner", "sara@example.com", "password123")
        self.mech = self.acc.create_user("Ustad A", "mech@example.com", "password123", "mechanic")
        self.admin = self.acc.create_user("Admin", "admin@example.com", "password123", "admin")

    # -- accounts
    def test_signup_is_always_owner_and_login_works(self):
        self.assertEqual(self.owner["role"], "owner")
        self.assertEqual(self.acc.authenticate("ALI@example.com ", "password123")["user_id"], self.owner["user_id"])
        self.assertIsNone(self.acc.authenticate("ali@example.com", "wrong-pass"))
        with self.assertRaises(Invalid):
            self.acc.register_owner("Dup", "ali@example.com", "password123")
        with self.assertRaises(Invalid):
            self.acc.register_owner("Short", "x@example.com", "short")
        self.assertNotIn("password_hash", self.owner)

    def test_admin_cannot_demote_self(self):
        with self.assertRaises(Invalid):
            self.acc.set_role(self.admin["user_id"], self.admin["user_id"], "owner")
        self.assertEqual(self.acc.set_role(self.admin["user_id"], self.owner["user_id"], "mechanic")["role"], "mechanic")

    # -- Story 1 garage
    def test_catalog_flags_unsupported(self):
        cat = {c["vehicle_id"]: c["supported"] for c in self.acc.catalog()}
        self.assertTrue(cat["toyota-corolla-2018-xli"])
        self.assertFalse(cat["toyota-corolla-2012-xli"])
        self.assertFalse(cat["honda-civic-2018-base"])

    def test_add_vehicle_and_update_mileage(self):
        with self.assertRaises(Invalid):
            self.acc.add_vehicle(self.owner["user_id"], "honda-civic-2018-base", 1000)
        v = self.acc.add_vehicle(self.owner["user_id"], "toyota-corolla-2018-xli", 82000)
        self.assertTrue(v["has_manual"])
        self.assertEqual(self.acc.update_mileage(self.owner["user_id"], v["user_vehicle_id"], 83500)["current_mileage"], 83500)
        with self.assertRaises(NotFound):   # someone else's car
            self.acc.update_mileage(self.other["user_id"], v["user_vehicle_id"], 1)
        self.assertEqual(self.acc.my_vehicles(self.other["user_id"]), [])

    def test_history_is_per_user_and_newest_first(self):
        mine = self.acc.add_vehicle(self.owner["user_id"], "toyota-corolla-2018-xli", 1)
        theirs = self.acc.add_vehicle(self.other["user_id"], "toyota-corolla-2018-xli", 1)
        self.svc.diagnose(mine["user_vehicle_id"], "grinding noise when braking")
        time.sleep(0.002)
        self.svc.diagnose(mine["user_vehicle_id"], "how do I pair bluetooth")
        self.svc.diagnose(theirs["user_vehicle_id"], "P0301")
        h = self.acc.my_cases(self.owner["user_id"])
        self.assertEqual([c["question"] for c in h], ["how do I pair bluetooth", "grinding noise when braking"])
        self.assertEqual([c["status"] for c in h], ["abstained", "answered"])
        self.assertTrue(all(c["asked_at_ms"] for c in h))

    # -- mechanic notes
    def _submit(self, **kw):
        args = dict(topic="Grinding when braking", manufacturer="Toyota", model="Corolla", years="2018",
                    advice="Grinding when braking usually means pads worn to metal; check the rotors too.",
                    experience_years="18", workshop="Independent", city="Lahore", consent=True)
        args.update(kw)
        return self.acc.submit_note(self.mech, **args)

    def test_note_requires_consent(self):
        with self.assertRaises(Invalid):
            self._submit(consent=False)

    def test_pending_note_is_not_used_until_approved(self):
        g = self._submit()
        self.assertEqual(g["status"], "pending")
        self.assertEqual(self.acc.my_notes(self.mech["user_id"])[0]["group_id"], g["group_id"])
        scope = self.svc.retriever.index_for(self.svc.repo.get_vehicle_profile("uv-corolla"))
        self.assertFalse(any("rotors too" in c.text for c in scope.chunks))

        self.acc.approve_note(g["group_id"], HashingEmbedder())
        self.svc.retriever.invalidate()
        r = self.svc.diagnose("uv-corolla", "grinding when braking pads worn rotors")
        mech = [c for c in r.citations if c.document_type == "mechanic_note"]
        self.assertTrue(mech)
        self.assertIn("Ustad A", mech[0].document_name)
        self.assertEqual(self.acc.my_notes(self.mech["user_id"])[0]["status"], "approved")

    def test_reject_removes_note(self):
        g = self._submit()
        self.acc.reject_note(g["group_id"])
        self.assertEqual(self.acc.my_notes(self.mech["user_id"]), [])
        with self.assertRaises(NotFound):
            self.acc.reject_note(g["group_id"])

    def test_year_range_and_bad_vehicle(self):
        with self.assertRaises(Invalid):
            self._submit(years="2016")          # no 2016 vehicle row in fixtures
        with self.assertRaises(Invalid):
            self._submit(years="")              # model without years
        g = self._submit(model="", manufacturer="", years="", topic="Battery terminals",
                         advice="Clean white corrosion off the battery terminals before replacing the battery.")
        self.assertIsNone(g["vehicle"])

    # -- admin
    def test_stats_and_documents(self):
        self.svc.diagnose("uv-corolla", "grinding noise when braking")
        self.svc.diagnose("uv-corolla", "mera bluetooth phone connect nahi ho raha")
        self._submit()
        s = self.acc.stats()
        self.assertEqual(s["by_language"]["en"]["answered"], 1)
        self.assertEqual(s["by_language"]["roman_ur"]["abstained"], 1)
        self.assertEqual(s["pending_notes"], 1)
        self.assertEqual(s["users_by_role"], {"owner": 2, "mechanic": 1, "admin": 1})
        names = [d["document_name"] for d in self.acc.documents()]
        self.assertIn("Corolla 2018 Owner's Manual", names)
        self.assertFalse(any(n.startswith("Mechanic note") for n in names))  # pending hidden


if __name__ == "__main__":
    unittest.main()
