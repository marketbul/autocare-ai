"""Acceptance tests for Story 5: Calibrated Confidence and Selective Abstention (M3)."""
from __future__ import annotations

import unittest

from autocare.calibration import CalibrationSignals, ConfidenceCalibrator


class Story5(unittest.TestCase):
    def setUp(self):
        self.calibrator = ConfidenceCalibrator(base_abstention_threshold=0.50, critical_abstention_threshold=0.70)

    def test_ac1_calibrated_confidence_score_attached(self):
        signals = CalibrationSignals(
            classifier_prob=0.85,
            top_evidence_score=0.90,
            citation_support_ratio=1.0,
            code_recognized=True
        )
        res = self.calibrator.evaluate(signals)
        self.assertIsInstance(res.calibrated_confidence, float)
        self.assertTrue(0.0 <= res.calibrated_confidence <= 1.0)
        self.assertFalse(res.should_abstain)

    def test_ac2_selective_abstention_below_threshold(self):
        signals = CalibrationSignals(
            classifier_prob=0.30,
            top_evidence_score=0.15,
            citation_support_ratio=0.5,
            code_recognized=True
        )
        res = self.calibrator.evaluate(signals)
        self.assertTrue(res.should_abstain)
        self.assertIsNotNone(res.abstention_reason)

    def test_ac3_conservative_threshold_on_critical_path(self):
        # Score that passes non-critical (0.50) but fails critical (0.70)
        signals = CalibrationSignals(
            classifier_prob=0.60,
            is_critical_path=True,
            top_evidence_score=0.60,
            citation_support_ratio=0.8,
            code_recognized=True
        )
        res = self.calibrator.evaluate(signals)
        self.assertTrue(res.is_critical)
        self.assertEqual(res.threshold_applied, 0.70)
        self.assertTrue(res.should_abstain)

    def test_ac4_ece_metric_computation(self):
        probs = [0.95, 0.90, 0.85, 0.60, 0.55, 0.40, 0.20, 0.10]
        labels = [1, 1, 1, 1, 0, 0, 0, 0]
        ece = ConfidenceCalibrator.compute_ece(probs, labels, num_bins=5)
        self.assertIsInstance(ece, float)
        self.assertTrue(0.0 <= ece <= 1.0)

# [2026-06-11] test(triage): [AUT-107] add ba

# [2026-06-13] test(triage): [AUT-107] add baselin by Ahmad Zahid
