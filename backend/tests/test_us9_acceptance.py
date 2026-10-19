"""Acceptance tests for Story 9: Similar-Case Retrieval (M8)."""
from __future__ import annotations

import unittest

from autocare.case_bank import CaseBank
from autocare.db import Database


class Story9(unittest.TestCase):
    def setUp(self):
        self.db = Database("sqlite:///:memory:")
        self.db.create_schema()
        # Seed DTC code first to satisfy foreign key
        self.db.execute("""
            INSERT INTO diagnosticcode (code, description, system, severity)
            VALUES ('P0301', 'Cylinder 1 Misfire Detected', 'Powertrain', 'High')
        """)
        # Seed test cases
        self.db.execute("""
            INSERT INTO diagnosticcase (case_id, symptom_text, code, predicted_category,
                                        predicted_urgency, outcome, provenance)
            VALUES ('c1', 'Grinding noise when braking and stopping', NULL, 'braking',
                    'high', 'Replaced front brake pads and rotors', 'seeded'),
                   ('c2', 'Engine misfire with code P0301', 'P0301', 'engine',
                    'high', 'Replaced cylinder 1 coil pack', 'real')
        """)
        self.bank = CaseBank(self.db)

    def test_ac1_find_similar_case_and_resolution(self):
        cases = self.bank.search(symptom_text="grinding noise on braking", vehicle_model="Corolla")
        self.assertTrue(len(cases) >= 1)
        top = cases[0]
        self.assertEqual(top.case_id, "c1")
        self.assertIn("brake pads", top.resolution.lower())
        self.assertEqual(top.provenance, "seeded")

    def test_ac2_provenance_distinguishes_real_from_seeded(self):
        cases = self.bank.search(symptom_text="misfire", vehicle_model="Corolla", code="P0301")
        self.assertTrue(len(cases) >= 1)
        self.assertEqual(cases[0].provenance, "real")

# [2026-07-28] test(verifier): [AUT-112] add 

# [2026-07-31] test(verifier): [AUT-112] add faili by Ahmad Zahid
