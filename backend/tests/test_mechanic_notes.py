"""Mechanic notes: consent, vehicle scoping, citation as a separate source type."""
from __future__ import annotations

import csv
import os
import tempfile
import unittest

from autocare.generation import MECHANIC_NOTE, build_messages
from autocare.ml import HashingEmbedder
from fixtures import FakeLLM, build
from ingest.mechanic_notes import load

COLS = ["note_id", "mechanic_name", "experience_years", "workshop", "city", "interview_date",
        "consent", "manufacturer", "model", "years", "topic", "advice"]
ROWS = [  # test fixtures, not real interview content
    ["T1", "Mechanic A", "18", "Independent workshop", "Lahore", "2026-10-20", "yes",
     "Toyota", "Corolla", "2018", "Grinding noise when braking",
     "Grinding when braking usually means the brake pads are worn down to metal; check the rotor surface too."],
    ["T2", "Mechanic A", "18", "Independent workshop", "Lahore", "2026-10-20", "no",
     "Toyota", "Corolla", "2018", "Overheating", "No consent for this one."],
    ["T3", "Mechanic B", "25", "Dealer service bay", "Karachi", "2026-10-21", "yes",
     "Honda", "Civic", "2018", "Grinding noise when braking", "Civic-specific brake advice."],
    ["T4", "Mechanic B", "25", "Dealer service bay", "Karachi", "2026-10-21", "yes",
     "", "", "", "Battery terminals", "Clean white corrosion from battery terminals before suspecting the battery."],
]


class MechanicNotes(unittest.TestCase):
    def setUp(self):
        self.svc, self.llm, self.db = build()
        fd, self.path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(COLS); w.writerows(ROWS)
        self.out = load(self.svc.repo, HashingEmbedder(), self.path)
        self.svc.retriever.invalidate()

    def tearDown(self):
        os.unlink(self.path)

    def test_consent_required(self):
        self.assertIn(("T2", "no consent recorded"), self.out["skipped"])
        rows = self.db.query("SELECT text FROM documentchunk WHERE chunk_type = :t", {"t": MECHANIC_NOTE})
        self.assertFalse(any("No consent" in r["text"] for r in rows))

    def test_scoped_to_vehicle(self):
        scope = self.svc.retriever.index_for(self.svc.repo.get_vehicle_profile("uv-corolla"))
        texts = " ".join(c.text for c in scope.chunks)
        self.assertIn("worn down to metal", texts)        # Corolla 2018 note
        self.assertNotIn("Civic-specific", texts)          # other model never leaks in
        self.assertIn("battery terminals", texts.lower())  # generic note applies to all cars

    def test_cited_as_mechanic_source(self):
        r = self.svc.diagnose("uv-corolla", "grinding noise when braking worn pads rotor")
        types = {c.document_type for c in r.citations}
        self.assertIn(MECHANIC_NOTE, types)
        note = next(c for c in r.citations if c.document_type == MECHANIC_NOTE)
        self.assertIn("Mechanic interview: Mechanic A", note.document_name)
        self.assertIsNone(note.page_number)
        self.assertEqual(note.section, "Grinding noise when braking")

    def test_prompt_labels_source_kinds(self):
        self.svc.diagnose("uv-corolla", "grinding noise when braking worn pads rotor")
        msgs = build_messages("q", "en", self.svc.repo.get_vehicle_profile("uv-corolla"),
                              self.llm.calls[-1]["evidence"])
        self.assertIn("MECHANIC NOTE |", msgs[1]["content"])
        self.assertIn("MANUAL |", msgs[1]["content"])
        self.assertIn("follow the manual", msgs[0]["content"])

    def test_replace_reloads_without_duplicates(self):
        load(self.svc.repo, HashingEmbedder(), self.path, replace=True)
        n = self.db.query("SELECT COUNT(*) AS n FROM documentchunk WHERE chunk_type = :t", {"t": MECHANIC_NOTE})[0]["n"]
        self.assertEqual(n, self.out["notes"])


if __name__ == "__main__":
    unittest.main()
