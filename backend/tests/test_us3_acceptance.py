"""User Story 3: enter a diagnostic trouble code, or read it from a scanner photo."""
from __future__ import annotations

import base64
import shutil
import unittest
from pathlib import Path

from autocare.scan import (ImageRejected, Reading, TesseractCodeReader, codes_in_text,
                           combine_vision_reads, decode_data_url, read_codes)
from fixtures import build

ASSETS = Path(__file__).parent / "assets"
LIMIT = 6_000_000


def data_url(name: str) -> str:
    return "data:image/jpeg;base64," + base64.b64encode((ASSETS / name).read_bytes()).decode()


class FixedReader:
    """Stands in for the vision model / OCR."""
    def __init__(self, reading: Reading):
        self.reading, self.calls = reading, 0

    def read(self, image, mime):
        self.calls += 1
        return self.reading


class Story3(unittest.TestCase):
    def setUp(self):
        self.svc, _, self.db = build(triage=True)

    def test_ac1_typed_code_returns_reference_entry_with_citation(self):
        r = self.svc.diagnose("uv-corolla", "P0301")
        self.assertEqual(r.status, "answered")
        self.assertTrue(any(c.document_type == "dtc_reference" and c.section == "P0301" for c in r.citations))
        self.assertFalse(any(c.section == "P0302" for c in r.citations))
        self.assertEqual(r.signals["code_source"], "typed")

    def test_ac2_photo_code_gets_the_same_lookup(self):
        reader = FixedReader(Reading(["P0301"], 0.95, "vision", ["two independent reads agree"]))
        out = read_codes(reader, self.svc.repo, data_url("scanner_p0301.jpg"), LIMIT)
        self.assertEqual(out["status"], "read")
        self.assertEqual(out["codes"], [{"code": "P0301", "known": True, "description": "Cylinder 1 Misfire Detected"}])
        typed = self.svc.diagnose("uv-corolla", "P0301")
        photo = self.svc.diagnose("uv-corolla", out["codes"][0]["code"], code_source="photo")
        self.assertEqual([c.chunk_id for c in photo.citations], [c.chunk_id for c in typed.citations])
        self.assertEqual((photo.triage.category, photo.triage.urgency), (typed.triage.category, typed.triage.urgency))
        self.assertEqual(photo.signals["code_source"], "photo")

    def test_ac3_unclear_photo_asks_to_retype_and_returns_no_guess(self):
        for reading in (Reading(["P0301"], 0.3, "vision", ["the two reads disagree"]),
                        Reading([], 0.0, "tesseract", ["no text found"])):
            out = read_codes(FixedReader(reading), self.svc.repo, data_url("scanner_blurry.jpg"), LIMIT)
            self.assertEqual(out["status"], "unclear")
            self.assertEqual(out["codes"], [])
            self.assertIn("type the code", out["message"].lower())

    def test_ac4_unrecognised_code_is_reported_and_lowers_confidence(self):
        out = read_codes(FixedReader(Reading(["P0999"], 0.95, "vision")), self.svc.repo,
                         data_url("scanner_p0301.jpg"), LIMIT)
        self.assertEqual(out["codes"][0]["known"], False)
        r = self.svc.diagnose("uv-corolla", "P0999", code_source="photo")
        self.assertEqual(r.status, "abstained")
        self.assertEqual(r.abstention.reason, "code_not_found")
        self.assertIn("P0999", r.abstention.message)
        r2 = self.svc.diagnose("uv-corolla", "P0999 engine shaking at idle")
        if r2.status == "answered":
            self.assertTrue(any("P0999" in n for n in r2.notices))
        self.assertTrue(r2.triage.uncertain)

    def test_messages_in_the_owners_language(self):
        out = read_codes(FixedReader(Reading([], 0.1, "vision")), self.svc.repo, data_url("scanner_blurry.jpg"),
                         LIMIT, lang="roman_ur")
        self.assertIn("type karein", out["message"])


class VisionAgreement(unittest.TestCase):
    def test_two_reads_agree(self):
        r = combine_vision_reads('{"codes": ["P0301"], "readable": true}', "STORED DTCs\nP0301\nCyl 1 misfire")
        self.assertEqual(r.codes, ["P0301"]); self.assertGreaterEqual(r.confidence, 0.9)

    def test_reads_disagree_or_unclear(self):
        self.assertLess(combine_vision_reads('{"codes": ["P0301"]}', "P0381").confidence, 0.8)
        self.assertLess(combine_vision_reads('{"codes": ["P0301"], "readable": false}', "P0301").confidence, 0.8)
        self.assertLess(combine_vision_reads('{"codes": ["P0301"]}', "P03[unclear]1 P0301").confidence, 0.8)

    def test_letter_for_digit_lowers_confidence(self):
        r = combine_vision_reads('{"codes": ["PO301"]}', "PO301")
        self.assertEqual(r.codes, ["P0301"]); self.assertLess(r.confidence, 0.95)

    def test_no_code_on_screen(self):
        r = combine_vision_reads('{"codes": [], "readable": true}', "No codes stored")
        self.assertEqual(r.codes, []); self.assertGreaterEqual(r.confidence, 0.8)

    def test_ocr_text_parsing(self):
        self.assertEqual(codes_in_text("1) P0171 2) p0420")[0], ["P0171", "P0420"])
        self.assertEqual(codes_in_text("BOOST CLOSE PUMP1")[0], [])   # never invent codes from words


class Upload(unittest.TestCase):
    def test_rejects_non_images_and_oversize(self):
        with self.assertRaises(ImageRejected):
            decode_data_url("data:application/pdf;base64,AAAA", LIMIT)
        with self.assertRaises(ImageRejected):
            decode_data_url("not a data url", LIMIT)
        with self.assertRaises(ImageRejected):
            decode_data_url(data_url("scanner_p0301.jpg"), 1000)


@unittest.skipUnless(shutil.which("tesseract"), "Tesseract not installed")
class TesseractPhotos(unittest.TestCase):
    """Real OCR on generated scanner screens (tests/assets)."""
    def setUp(self):
        self.svc, _, _ = build()

    def read(self, name):
        return read_codes(TesseractCodeReader(), self.svc.repo, data_url(name), LIMIT)

    def test_clear_photo(self):
        out = self.read("scanner_p0301.jpg")
        self.assertEqual(out["status"], "read")
        self.assertEqual([c["code"] for c in out["codes"]], ["P0301"])

    def test_two_codes_light_screen(self):
        self.assertEqual([c["code"] for c in self.read("scanner_two_codes.jpg")["codes"]], ["P0171", "P0420"])

    def test_blurry_photo_is_unclear(self):
        self.assertEqual(self.read("scanner_blurry.jpg")["status"], "unclear")

    def test_screen_without_code(self):
        self.assertEqual(self.read("scanner_no_code.jpg")["status"], "no_code")


if __name__ == "__main__":
    unittest.main()
