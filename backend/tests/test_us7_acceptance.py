"""Acceptance tests for Story 7: Repair-Recommendation Verifier (M5)."""
from __future__ import annotations

import unittest

from autocare.knowledge_graph import AutomotiveKnowledgeGraph
from autocare.verifier import RepairVerifier


class Story7(unittest.TestCase):
    def setUp(self):
        self.kg = AutomotiveKnowledgeGraph()
        # Seed test components
        self.kg.add_node("brake_pads", "component", "Brake Pads", ["pads", "brake lining"])
        self.kg.add_node("grinding_on_braking", "symptom", "Grinding noise when braking", ["ghisne ki awaz"])
        self.kg.add_node("brake_master_cylinder", "component", "Brake Master Cylinder", ["master pump"])
        self.kg.add_node("spongy_pedal", "symptom", "Spongy brake pedal")

        # Causal edges
        self.kg.add_edge("brake_pads", "grinding_on_braking", "causes", 0.95)
        self.kg.add_edge("brake_master_cylinder", "spongy_pedal", "causes", 0.90)

        self.verifier = RepairVerifier(self.kg)

    def test_ac1_supported_repair_verdict(self):
        evidence = [{"document_name": "Corolla OM", "section": "Brakes", "page_number": 412,
                     "text": "Worn brake pads create a harsh grinding noise when braking."}]
        res = self.verifier.verify(
            proposed_repair="Brake Pads Replacement",
            symptoms="grinding noise when braking",
            evidence_passages=evidence
        )
        self.assertEqual(res.verdict, "supported")
        self.assertTrue(res.graph_path_found)
        self.assertIn("physical inspection", res.physical_inspection_disclaimer.lower())

    def test_ac2_unsupported_repair_shows_alternatives(self):
        res = self.verifier.verify(
            proposed_repair="Brake Master Cylinder Replacement",
            symptoms="grinding noise when braking",
            evidence_passages=[]
        )
        self.assertEqual(res.verdict, "unsupported")
        self.assertFalse(res.graph_path_found)
        self.assertTrue(len(res.indicated_alternatives) >= 1)
        self.assertTrue(any("brake pad" in a.lower() for a in res.indicated_alternatives))

    def test_ac3_photo_damage_location_premise(self):
        # Mechanic claims front bumper replacement, but photo shows only rear damage
        res = self.verifier.verify(
            proposed_repair="Front Bumper Assembly Replacement",
            symptoms="exterior collision damage",
            evidence_passages=[],
            damage_location="Rear Quarter Panel"
        )
        self.assertEqual(res.verdict, "unsupported")

# [2026-07-10] test(trace): [AUT-111B] verify
