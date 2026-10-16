"""Structure-aware chunking keeps section path + page (needed for AC2 citations)."""
from __future__ import annotations

import os
import tempfile
import unittest

from ingest.pdf_ingest import chunk_pdf, parse_years


def make_pdf(path: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4

    def page(lines, number):
        y = h - 90
        for size, text in lines:
            c.setFont("Helvetica", size)
            c.drawString(60, y, text)
            y -= size + 8
        c.setFont("Helvetica", 9)
        c.drawString(w / 2, 20, str(number))     # printed page number in the footer band
        c.showPage()

    body = "The disc brake pads have wear indicators that make a grinding noise when worn."
    page([(20, "Maintenance and care"), (14, "Brake pad wear indicator"),
          (10, body), (10, "Have the pads checked by your dealer if you hear this noise."),
          (10, "WARNING"), (10, "Driving with worn pads increases stopping distance."),
          (10, "Replace worn pads promptly to keep braking performance.")], 400)
    page([(20, "When trouble arises"), (14, "If the engine overheats"),
          (10, "1. Stop the vehicle in a safe place and turn off the air conditioning."),
          (10, "2. Check for steam or smoke from the engine compartment."),
          (10, "3. Check the coolant level after the engine has cooled down.")], 401)
    c.save()


class PdfChunking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.path = os.path.join(cls.tmp, "manual.pdf")
        make_pdf(cls.path)
        cls.chunks = chunk_pdf(cls.path, page_offset=-399)   # physical 1 -> printed 400

    def find(self, needle):
        return next(c for c in self.chunks if needle in c.text)

    def test_section_path_and_printed_page(self):
        c = self.find("grinding noise")
        self.assertEqual(c.section, "Maintenance and care > Brake pad wear indicator")
        self.assertEqual(c.page_number, 400)
        self.assertEqual(self.find("coolant level").page_number, 401)

    def test_warning_is_its_own_chunk(self):
        w = self.find("stopping distance")
        self.assertEqual(w.chunk_type, "warning")
        self.assertNotIn("stopping distance", self.find("grinding noise").text)

    def test_numbered_steps_are_procedure(self):
        self.assertEqual(self.find("steam or smoke").chunk_type, "procedure")
        self.assertEqual(self.find("steam or smoke").section,
                         "When trouble arises > If the engine overheats")

    def test_footer_dropped(self):
        for c in self.chunks:
            self.assertNotIn("\n400", c.text)
            self.assertNotEqual(c.text.strip(), "400")

    def test_year_ranges(self):
        self.assertEqual(parse_years("2014-2016"), [2014, 2015, 2016])
        self.assertEqual(parse_years("2018"), [2018])


if __name__ == "__main__":
    unittest.main()
