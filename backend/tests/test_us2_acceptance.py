"""User Story 2 — one test class per acceptance criterion.

Run from backend/:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import unittest

from autocare.generation import ExtractiveGenerator
from autocare.language import detect_language, expansion_terms
from autocare.schemas import DiagnoseResponse
from autocare.service import UnsupportedVehicle, VehicleProfileRequired
from autocare.text import extract_dtcs, tokenize
from fixtures import FakeLLM, build


def cited_chunk_ids(resp: DiagnoseResponse) -> set[str]:
    return {c.chunk_id for c in resp.citations}


class AC0_ProfileRequired(unittest.TestCase):
    """Given no active vehicle profile, the query is refused with a register prompt."""

    def setUp(self):
        self.svc, self.llm, _ = build()

    def test_missing_profile_id(self):
        with self.assertRaises(VehicleProfileRequired) as cm:
            self.svc.diagnose(None, "grinding noise when braking")
        self.assertEqual(cm.exception.language, "en")
        self.assertIn("register", cm.exception.message.lower())
        self.assertEqual(self.llm.calls, [])

    def test_unknown_profile_id_answers_in_query_language(self):
        with self.assertRaises(VehicleProfileRequired) as cm:
            self.svc.diagnose("does-not-exist", "meri gaari ki brake se awaz aati hai")
        self.assertEqual(cm.exception.language, "roman_ur")
        self.assertIn("register karein", cm.exception.message)

    def test_unsupported_year_and_model(self):
        for uv in ("uv-old-corolla", "uv-civic"):
            with self.subTest(uv=uv), self.assertRaises(UnsupportedVehicle):
                self.svc.diagnose(uv, "grinding noise when braking")


class AC1_RetrieveAndAnswerInSameLanguage(unittest.TestCase):
    def setUp(self):
        self.svc, self.llm, _ = build()

    def test_english(self):
        r = self.svc.diagnose("uv-corolla", "I hear a grinding noise when braking")
        self.assertEqual(r.status, "answered")
        self.assertEqual(r.query_language, "en")
        self.assertEqual(self.llm.calls[-1]["language"], "en")
        self.assertIn("c-brake-pads", cited_chunk_ids(r))

    def test_roman_urdu(self):
        r = self.svc.diagnose("uv-corolla", "brake lagate waqt grinding ki awaz aati hai")
        self.assertEqual(r.query_language, "roman_ur")
        self.assertEqual(self.llm.calls[-1]["language"], "roman_ur")
        self.assertEqual(r.answer_language, "roman_ur")
        self.assertIn("c-brake-pads", cited_chunk_ids(r))

    def test_urdu_script(self):
        r = self.svc.diagnose("uv-corolla", "بریک لگاتے وقت آواز آتی ہے")
        self.assertEqual(r.query_language, "ur")
        self.assertEqual(self.llm.calls[-1]["language"], "ur")
        self.assertEqual(r.status, "answered")
        self.assertTrue(cited_chunk_ids(r) & {"c-brake-pads", "c-brake-light"})
        self.assertIn("مکینک", r.disclaimer)

    def test_vehicle_filter_blocks_other_models(self):
        """The Civic manual says almost the same thing; it must never be retrieved."""
        r = self.svc.diagnose("uv-corolla", "grinding noise when braking brake pads")
        self.assertNotIn("c-civic-brakes", cited_chunk_ids(r))
        for call in self.llm.calls:
            self.assertNotIn("c-civic-brakes", [e.chunk.chunk_id for e in call["evidence"]])
        scope = self.svc.retriever.index_for(self.svc.repo.get_vehicle_profile("uv-corolla"))
        self.assertNotIn("c-civic-brakes", [c.chunk_id for c in scope.chunks])
        self.assertIn("c-p0301", [c.chunk_id for c in scope.chunks])  # generic reference stays in

    def test_extractive_mode_reports_english_honestly(self):
        svc, _, _ = build(generator=ExtractiveGenerator())
        r = svc.diagnose("uv-corolla", "brake lagate waqt grinding ki awaz aati hai")
        self.assertEqual(r.answer_language, "en")
        self.assertTrue(any("Extractive mode" in n for n in r.notices))


class AC2_EveryClaimCited(unittest.TestCase):
    def test_uncited_and_unsupported_claims_are_removed(self):
        def script(q, lang, ev):
            first = ev[0]
            return [
                {"text": first.chunk.text.split(". ")[0], "evidence_ids": [first.label]},
                {"text": "Replace the timing belt every 10,000 km.", "evidence_ids": []},
                {"text": "Brake pads are worn.", "evidence_ids": ["E99"]},
                {"text": "Replace the timing belt every 10,000 km.", "evidence_ids": [first.label]},
            ]

        svc, _, _ = build(generator=FakeLLM(script))
        r = svc.diagnose("uv-corolla", "grinding noise when braking")
        self.assertEqual(r.status, "answered")
        self.assertEqual(len(r.claims), 1)
        self.assertEqual(r.dropped_claim_count, 3)
        self.assertNotIn("timing belt", " ".join(c.text for c in r.claims))
        numbers = {c.number for c in r.citations}
        for claim in r.claims:
            self.assertTrue(claim.citations)
            self.assertTrue(set(claim.citations) <= numbers)
        for cit in r.citations:
            self.assertTrue(cit.document_name and cit.section and cit.page_number)

    def test_all_claims_rejected_means_abstain(self):
        svc, _, _ = build(generator=FakeLLM(lambda q, l, ev: [
            {"text": "Your gearbox needs a full rebuild.", "evidence_ids": ["E1"]}]))
        r = svc.diagnose("uv-corolla", "grinding noise when braking")
        self.assertEqual(r.status, "abstained")
        self.assertEqual(r.abstention.reason, "no_supported_claims")
        self.assertEqual(r.claims, [])
        self.assertEqual(r.citations, [])

    def test_llm_returns_garbage(self):
        svc, _, _ = build(generator=FakeLLM(lambda q, l, ev: []))
        r = svc.diagnose("uv-corolla", "grinding noise when braking")
        self.assertEqual(r.status, "abstained")


class AC3_ExactCodeMatch(unittest.TestCase):
    def setUp(self):
        self.svc, self.llm, self.db = build()

    def test_exact_code_wins_and_neighbouring_code_is_excluded(self):
        r = self.svc.diagnose("uv-corolla", "P0301")
        self.assertEqual(r.status, "answered")
        self.assertEqual(r.detected_codes, ["P0301"])
        self.assertEqual(r.codes_found, {"P0301": True})
        self.assertEqual(r.citations[0].chunk_id, "c-p0301")
        evidence_ids = [e.chunk.chunk_id for e in self.llm.calls[-1]["evidence"]]
        self.assertEqual(evidence_ids[0], "c-p0301")
        self.assertNotIn("c-p0302", evidence_ids)

    def test_code_inside_roman_urdu_sentence(self):
        r = self.svc.diagnose("uv-corolla", "meri car mein p0301 code aa raha hai, engine hil raha hai")
        self.assertEqual(r.detected_codes, ["P0301"])
        self.assertEqual(r.citations[0].chunk_id, "c-p0301")

    def test_unknown_code_abstains_without_substituting(self):
        r = self.svc.diagnose("uv-corolla", "P0399")
        self.assertEqual(r.status, "abstained")
        self.assertEqual(r.abstention.reason, "code_not_found")
        self.assertIn("P0399", r.abstention.message)
        self.assertEqual(self.llm.calls, [])

    def test_case_logged_with_code_fk(self):
        r = self.svc.diagnose("uv-corolla", "P0301")
        row = self.db.query("SELECT * FROM diagnosticcase WHERE case_id = :id", {"id": r.case_id})[0]
        self.assertEqual(row["code"], "P0301")
        self.assertEqual(row["language"], "en")
        self.assertEqual(json.loads(row["evidence_refs"]), [c.chunk_id for c in r.citations])
        self.assertEqual(row["provenance"], "real")
        self.assertIsNone(row["predicted_urgency"])   # M2's job, not this story's


class AC4_MixedRomanUrduEnglish(unittest.TestCase):
    def test_mixed_query_needs_no_rephrasing(self):
        svc, _, _ = build()
        cases = {
            "gaari garam ho rahi hai aur engine se smoke": "c-overheat",
            "check engine light on hai, flash kar rahi hai": "c-mil",
            "brake warning light on ho gayi hai driving ke dauran": "c-brake-light",
        }
        for q, expected in cases.items():
            with self.subTest(q=q):
                r = svc.diagnose("uv-corolla", q)
                self.assertEqual(r.query_language, "roman_ur")
                self.assertEqual(r.status, "answered")
                self.assertIn(expected, cited_chunk_ids(r))


class AC5_AbstainWithoutEvidence(unittest.TestCase):
    def test_out_of_corpus_question(self):
        svc, llm, _ = build()
        r = svc.diagnose("uv-corolla", "how do I pair my bluetooth phone with the stereo")
        self.assertEqual(r.status, "abstained")
        self.assertEqual(r.abstention.reason, "no_strong_match")
        self.assertEqual(r.claims, [])
        self.assertEqual(llm.calls, [])            # never asks the LLM to improvise
        self.assertTrue(r.disclaimer)

    def test_abstain_message_in_roman_urdu(self):
        svc, _, _ = build()
        r = svc.diagnose("uv-corolla", "mera bluetooth phone connect nahi ho raha")
        self.assertEqual(r.status, "abstained")
        self.assertIn("mustanad", r.abstention.message)


class Units(unittest.TestCase):
    def test_language_detection(self):
        self.assertEqual(detect_language("Grinding noise when braking"), "en")
        self.assertEqual(detect_language("P0301"), "en")
        self.assertEqual(detect_language("main road par brake fail"), "en")
        self.assertEqual(detect_language("gaari garam ho rahi hai"), "roman_ur")
        self.assertEqual(detect_language("brake se awaz"), "roman_ur")
        self.assertEqual(detect_language("گاڑی گرم ہو رہی ہے"), "ur")
        self.assertEqual(detect_language("میری car کا engine گرم ہو رہا ہے"), "ur")

    def test_expansion(self):
        self.assertIn("noise", expansion_terms("brake se awaz aati hai", "roman_ur"))
        self.assertIn("overheating", expansion_terms("انجن گرم ہو رہا ہے", "ur"))
        self.assertEqual(expansion_terms("grinding noise", "en"), "")

    def test_dtc_tokens(self):
        self.assertEqual(extract_dtcs("codes p0301, P0171 and U0100; not XP03011"),
                         ["P0301", "P0171", "U0100"])
        self.assertIn("p0301", tokenize("Code P0301 detected"))

    def test_response_serialises(self):
        svc, _, _ = build()
        r = svc.diagnose("uv-corolla", "P0301")
        DiagnoseResponse.model_validate_json(r.model_dump_json())


if __name__ == "__main__":
    unittest.main()


class CrossLingualPivot(unittest.TestCase):
    """Urdu / Roman-Urdu questions are rewritten to English for search + rerank;
    the answer language stays the user's."""

    class TranslatingLLM(FakeLLM):
        def __init__(self, english, fail=False):
            super().__init__()
            self.english, self.fail, self.translated = english, fail, []

        def translate_query(self, question, language):
            self.translated.append((question, language))
            if self.fail:
                raise RuntimeError("provider down")
            return self.english

    QUERY = "mera paara upar ja raha hai kya karoon"   # no glossary words at all

    def test_without_pivot_this_query_abstains(self):
        svc, _, _ = build()
        self.assertEqual(svc.diagnose("uv-corolla", self.QUERY).status, "abstained")

    def test_pivot_finds_evidence_and_keeps_user_language(self):
        llm = self.TranslatingLLM("engine overheats temperature gauge red zone what to do")
        svc, _, _ = build(generator=llm)
        r = svc.diagnose("uv-corolla", self.QUERY)
        self.assertEqual(r.status, "answered")
        self.assertIn("c-overheat", cited_chunk_ids(r))
        self.assertEqual(r.query_language, "roman_ur")
        self.assertEqual(llm.calls[-1]["language"], "roman_ur")        # answer language
        self.assertEqual(llm.calls[-1]["question"], self.QUERY)        # original question
        self.assertIn("overheats", r.signals["retrieval_query"])

    def test_english_queries_are_not_translated(self):
        llm = self.TranslatingLLM("unused")
        svc, _, _ = build(generator=llm)
        svc.diagnose("uv-corolla", "grinding noise when braking")
        self.assertEqual(llm.translated, [])

    def test_translation_failure_falls_back_to_glossary(self):
        llm = self.TranslatingLLM("x", fail=True)
        svc, _, _ = build(generator=llm)
        r = svc.diagnose("uv-corolla", "brake lagate waqt grinding ki awaz aati hai")
        self.assertEqual(r.status, "answered")

    def test_fault_code_survives_translation(self):
        llm = self.TranslatingLLM("engine is shaking")          # translator dropped the code
        svc, _, _ = build(generator=llm)
        r = svc.diagnose("uv-corolla", "meri car mein P0301 aa raha hai, engine hil raha hai")
        self.assertIn("P0301", r.signals["retrieval_query"])
        self.assertEqual(r.citations[0].chunk_id, "c-p0301")


class ClaimCheckUsesEnglishRendering(unittest.TestCase):
    def test_roman_urdu_claim_verified_via_text_en(self):
        def script(q, lang, ev):
            e = next(x for x in ev if x.chunk.chunk_id == "c-brake-pads")
            return [{"text": "Pads ghis jayen to brake lagate waqt cheekhne ki awaz aati hai.",
                     "text_en": e.chunk.text.split(". ")[0], "evidence_ids": [e.label]}]
        svc, _, _ = build(generator=FakeLLM(script))
        r = svc.diagnose("uv-corolla", "brake lagate waqt grinding ki awaz aati hai")
        self.assertEqual(r.status, "answered")
        self.assertTrue(r.claims[0].text.startswith("Pads ghis"))   # user sees Roman Urdu

    def test_text_en_cannot_smuggle_unsupported_claim(self):
        svc, _, _ = build(generator=FakeLLM(lambda q, l, ev: [
            {"text": "Gearbox badal dein.", "text_en": "Replace the gearbox.", "evidence_ids": ["E1"]}]))
        r = svc.diagnose("uv-corolla", "brake lagate waqt grinding ki awaz aati hai")
        self.assertEqual(r.status, "abstained")
