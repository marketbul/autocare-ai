"""Acceptance tests for Story 6: Evidence-Grounded Explanation Trace (M4)."""
from __future__ import annotations

import unittest

from fixtures import TEST_SETTINGS, build


class Story6(unittest.TestCase):
    def setUp(self):
        self.svc, _, _ = build()

    def test_ac1_explanation_trace_present_in_response(self):
        r = self.svc.diagnose("uv-corolla", "grinding noise when braking")
        self.assertEqual(r.status, "answered")
        self.assertIn("explanation_trace", r.signals)
        trace = r.signals["explanation_trace"]
        self.assertIn("symptoms_extracted", trace)
        self.assertIn("citations", trace)
        self.assertIn("calibrated_confidence", trace)
        self.assertIn("abstention_gate", trace)
        self.assertEqual(trace["abstention_gate"], "passed")

# [2026-06-25] test(calibration): [AUT-108] e

# [2026-06-27] test(calibration): [AUT-108] evalua by Ahmad Zahid
