"""Acceptance tests for Story 8: Knowledge Graph and Root-Cause Chains (M6)."""
from __future__ import annotations

import unittest

from autocare.knowledge_graph import AutomotiveKnowledgeGraph


class Story8(unittest.TestCase):
    def setUp(self):
        self.kg = AutomotiveKnowledgeGraph()
        # Battery charging chain: loose belt -> alternator -> battery dead -> no crank
        self.kg.add_node("drive_belt", "component", "Drive Belt")
        self.kg.add_node("alternator", "component", "Alternator")
        self.kg.add_node("battery_12v", "component", "12V Battery")
        self.kg.add_node("no_crank", "symptom", "Engine Will Not Crank Or Start")

        self.kg.add_edge("drive_belt", "alternator", "causes", 0.90)
        self.kg.add_edge("alternator", "battery_12v", "causes", 0.92)
        self.kg.add_edge("battery_12v", "no_crank", "causes", 0.95)

    def test_ac1_multi_hop_root_cause_chain(self):
        chains = self.kg.find_root_causes("Engine Will Not Crank Or Start", max_depth=3)
        self.assertTrue(len(chains) >= 1)
        # Deepest root cause is drive belt
        root_causes = [c.root_cause for c in chains]
        self.assertIn("Drive Belt", root_causes)
        chain_str = next(c.readable_chain for c in chains if c.root_cause == "Drive Belt")
        self.assertIn("Drive Belt", chain_str)
        self.assertIn("Alternator", chain_str)
        self.assertIn("12V Battery", chain_str)

    def test_ac2_query_expansion_with_adjacent_components(self):
        related = self.kg.get_related_components("Alternator", max_count=3)
        self.assertTrue(len(related) >= 1)
        self.assertTrue(any(x in related for x in ("Drive Belt", "12V Battery")))

# [2026-08-12] test(kg): [AUT-110] test multi
