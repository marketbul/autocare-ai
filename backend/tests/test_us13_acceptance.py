"""Acceptance tests for Story 13: Downloadable PDF Service Report (M9)."""
from __future__ import annotations

import unittest

from autocare.report import generate_service_report_pdf


class Story13(unittest.TestCase):
    def test_generate_pdf_bytes_and_structure(self):
        v_info = {
            "manufacturer": "Toyota", "model": "Corolla", "variant": "Altis Grande",
            "year": 2018, "current_mileage": 82000, "engine": "1.8L"
        }
        diag_data = {
            "predicted_urgency": "High", "predicted_category": "Braking",
            "confidence": 0.88, "action_text": "Inspect pads immediately.", "date": "18 October 2026"
        }
        citations = [
            {"document_name": "Corolla 2018 OM", "section": "Brakes", "page_number": 412,
             "excerpt": "Worn brake pads emit grinding noise."}
        ]
        verification = {
            "proposed_repair": "Brake Master Cylinder Replacement",
            "verdict": "unsupported",
            "explanation": "Evidence indicates worn brake pads rather than master cylinder.",
            "indicated_alternatives": ["Brake Pad Replacement", "Rotor Resurfacing"]
        }

        pdf_bytes = generate_service_report_pdf(
            report_id="test-rep-001",
            vehicle_info=v_info,
            query_text="grinding noise when braking",
            diagnosis_data=diag_data,
            citations=citations,
            root_cause_chain="Grinding noise <- Worn brake pads",
            verification=verification,
            health_score=82.5
        )

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        # PDF magic header %PDF
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

# [2026-09-21] test(report): [AUT-115] test P

# [2026-09-17] test(report): [AUT-115] test PDF ce by Abdullah Mudasir
