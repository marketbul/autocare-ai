"""User Story 2 orchestration: profile guard -> L2 retrieval -> generation ->
citation validation -> abstention -> persisted DiagnosticCase.

Pure Python (no web framework) so every acceptance criterion is unit-testable.
"""
from __future__ import annotations

import logging
import time
import uuid

from .config import Settings, is_supported, supported_label
from .generation import ExtractiveGenerator, Generator
from .language import LANG_EN, detect_language, expansion_terms
from .messages import (CODE_NOT_FOUND, DISCLAIMER, NO_EVIDENCE, REGISTER_FIRST,
                       UNSUPPORTED_VEHICLE, msg)
from .ml import Reranker
from .repository import Repository, VehicleProfile
from .retrieval import Evidence, RetrievalResult, Retriever
from .schemas import (Abstention, Alternative, Citation, Claim, DiagnoseResponse,
                      RetrievedPassage, TriageOut, VehicleOut)
from .triage import (CATEGORY_LABEL, URGENCY_ACTION, URGENCY_LABEL, Triage, TriageClassifier)
from .text import extract_dtcs
from .validation import validate_claims

log = logging.getLogger("autocare.diagnose")
EXCERPT_CHARS = 280


class DiagnoseError(Exception):
    code = "error"

    def __init__(self, message: str, language: str):
        super().__init__(message)
        self.message, self.language = message, language


class VehicleProfileRequired(DiagnoseError):   # AC0
    code = "vehicle_profile_required"


class UnsupportedVehicle(DiagnoseError):
    code = "unsupported_vehicle"


class GenerationFailed(DiagnoseError):
    code = "generation_failed"


def time_ordered_id() -> str:
    """UUIDv7-style id: the first 48 bits are the creation time in ms, so case ids
    sort by time and the date can be read back (DiagnosticCase has no date column)."""
    ms = int(time.time() * 1000)
    rnd = uuid.uuid4().int & ((1 << 80) - 1)
    value = (ms << 80) | (0x7 << 76) | rnd
    h = f"{value:032x}"
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


def id_timestamp_ms(case_id: str) -> int | None:
    try:
        h = case_id.replace("-", "")
        return int(h[:12], 16) if h[12] == "7" else None
    except (ValueError, IndexError):
        return None


def _excerpt(text: str) -> str:
    t = " ".join(text.split())
    return t if len(t) <= EXCERPT_CHARS else t[: EXCERPT_CHARS - 1].rstrip() + "…"


class DiagnoseService:
    def __init__(self, repo: Repository, retriever: Retriever, generator: Generator,
                 reranker: Reranker, settings: Settings, triage: TriageClassifier | None = None):
        self.repo, self.retriever, self.generator = repo, retriever, generator
        self.reranker, self.s, self.triage = reranker, settings, triage

    def diagnose(self, user_vehicle_id: str | None, query: str,
                 code_source: str = "typed") -> DiagnoseResponse:
        query = (query or "").strip()
        if not query:
            raise ValueError("query must not be empty")
        query = query[: self.s.max_query_chars]
        lang = detect_language(query)

        # -- AC0: no active profile -> cannot scope retrieval ----------------------
        vehicle = self.repo.get_vehicle_profile(user_vehicle_id) if user_vehicle_id else None
        if vehicle is None:
            raise VehicleProfileRequired(msg(REGISTER_FIRST, lang), lang)
        if not is_supported(self.s, vehicle.manufacturer, vehicle.model, vehicle.year):
            raise UnsupportedVehicle(
                msg(UNSUPPORTED_VEHICLE, lang, supported=supported_label(self.s)), lang)

        # -- L2 retrieval ------------------------------------------------------------
        dtcs = extract_dtcs(query)
        expansion = expansion_terms(query, lang)
        english = self._english_search_query(query, lang, dtcs)
        if english:
            # Cross-lingual pivot: the corpus and the reranker work best in English.
            # The ANSWER is still generated in the user's language (below).
            retrieval_query = f"{english} {expansion}".strip()
        else:
            retrieval_query = f"{query} {expansion}".strip()
        result = self.retriever.retrieve(vehicle, retrieval_query, dtcs)
        result.signals["retrieval_query"] = retrieval_query
        if dtcs:
            result.signals["code_source"] = code_source

        missing_codes = [c for c in dtcs if not result.codes_in_corpus.get(c)]
        # -- Story 4 / M2: fault category + urgency --------------------------------
        triage = self._classify(query, english, dtcs, missing_codes)
        notices: list[str] = []
        if missing_codes and result.evidence:
            notices.append(msg(CODE_NOT_FOUND, lang, codes=", ".join(missing_codes)))

        # -- AC5: nothing strong enough -> abstain, do NOT call the LLM ---------------
        if not result.evidence:
            reason, table = (("code_not_found", CODE_NOT_FOUND) if missing_codes
                             else ("no_strong_match", NO_EVIDENCE))
            return self._abstain(vehicle, query, lang, dtcs, result, reason,
                                 msg(table, lang, codes=", ".join(missing_codes)), notices=[],
                                 triage=triage)

        # -- generation + AC2 citation validation -----------------------------------
        try:
            raw = self.generator.generate(query, lang, vehicle, result.evidence)
        except Exception as exc:  # network / provider errors
            log.exception("generation failed")
            raise GenerationFailed(f"Answer generation failed: {exc}", lang) from exc

        kept, dropped = validate_claims(raw, result.evidence, self.reranker,
                                        self.s.min_claim_support)
        if not kept:
            return self._abstain(vehicle, query, lang, dtcs, result, "no_supported_claims",
                                 msg(NO_EVIDENCE, lang), notices, dropped=len(dropped), triage=triage)

        # Number citations in order of first use; only passages a kept claim relies on.
        numbers: dict[str, int] = {}
        cited: list[Evidence] = []
        claims: list[Claim] = []
        for vc in kept:
            nums = []
            for e in vc.evidence:
                if e.chunk.chunk_id not in numbers:
                    numbers[e.chunk.chunk_id] = len(numbers) + 1
                    cited.append(e)
                nums.append(numbers[e.chunk.chunk_id])
            claims.append(Claim(text=vc.text, citations=nums))

        citations = [
            Citation(number=numbers[e.chunk.chunk_id], chunk_id=e.chunk.chunk_id,
                     document_id=e.chunk.document_id, document_name=e.chunk.document_name,
                     document_type=e.chunk.document_type, section=e.chunk.section,
                     page_number=e.chunk.page_number, excerpt=_excerpt(e.chunk.text))
            for e in cited
        ]
        answer_lang = getattr(self.generator, "language", None) or lang
        signals = dict(result.signals)
        signals["citation_pass_rate"] = round(len(kept) / (len(kept) + len(dropped)), 4)
        signals["codes_in_reference_table"] = sorted(self.repo.existing_codes(dtcs)) if dtcs else []
        if isinstance(self.generator, ExtractiveGenerator) and lang != LANG_EN:
            notices.append("Extractive mode: answer shown in English (manual language). "
                           "Set AUTOCARE_GENERATION_MODE=llm for Urdu / Roman Urdu answers.")

        case_id = self._persist(vehicle, query, lang, dtcs, [c.chunk_id for c in citations], triage)
        return DiagnoseResponse(
            case_id=case_id, status="answered", query_language=lang, answer_language=answer_lang,
            vehicle=self._vehicle_out(vehicle), detected_codes=dtcs,
            codes_found={c: bool(result.codes_in_corpus.get(c)) for c in dtcs},
            claims=claims, citations=citations, abstention=None,
            retrieved_but_insufficient=[], notices=notices,
            dropped_claim_count=len(dropped), signals=signals,
            triage=self._triage_out(triage, lang, withheld=False), disclaimer=msg(DISCLAIMER, lang),
        )

    # -- helpers ---------------------------------------------------------------
    def _english_search_query(self, query: str, lang: str, dtcs: list[str]) -> str | None:
        """Urdu / Roman Urdu -> English search query via the LLM. None = use glossary only."""
        if lang == LANG_EN or not hasattr(self.generator, "translate_query"):
            return None
        try:
            english = (self.generator.translate_query(query, lang) or "").strip()
        except Exception:
            log.warning("query translation failed; falling back to glossary expansion",
                        exc_info=True)
            return None
        if not english:
            return None
        missing = [c for c in dtcs if c not in english.upper()]   # never lose a fault code
        return " ".join([english, *missing])

    def _abstain(self, vehicle: VehicleProfile, query: str, lang: str, dtcs: list[str],
                 result: RetrievalResult, reason: str, message: str, notices: list[str],
                 dropped: int = 0, triage: Triage | None = None) -> DiagnoseResponse:
        # Show what WAS retrieved (architecture L4: "shows what was retrieved"),
        # clearly labelled as insufficient — never as an answer.
        shown = (result.weak_candidates if reason != "no_supported_claims"
                 else result.evidence[:3])
        case_id = self._persist(vehicle, query, lang, dtcs, [], triage)
        return DiagnoseResponse(
            case_id=case_id, status="abstained", query_language=lang, answer_language=lang,
            vehicle=self._vehicle_out(vehicle), detected_codes=dtcs,
            codes_found={c: bool(result.codes_in_corpus.get(c)) for c in dtcs},
            claims=[], citations=[], abstention=Abstention(reason=reason, message=message),
            retrieved_but_insufficient=[
                RetrievedPassage(document_name=e.chunk.document_name, section=e.chunk.section,
                                 page_number=e.chunk.page_number, excerpt=_excerpt(e.chunk.text),
                                 score=round(e.rerank_score, 4))
                for e in shown
            ],
            notices=notices, dropped_claim_count=dropped, signals=dict(result.signals),
            triage=self._triage_out(triage, lang, withheld=True), disclaimer=msg(DISCLAIMER, lang),
        )

    def _classify(self, query: str, english: str | None, dtcs: list[str],
                  missing_codes: list[str]) -> Triage | None:
        if self.triage is None:
            return None
        try:
            t = self.triage.classify(query, english=english, codes=self.repo.get_codes(dtcs))
        except Exception:   # classification must never block the answer
            log.exception("triage failed")
            return None
        if missing_codes:   # Story 3 AC4: an unrecognised code lowers confidence
            t.category_probability = round(t.category_probability * 0.7, 3)
            t.uncertain = True
            t.basis.append(f"code {', '.join(missing_codes)} not in the reference: confidence lowered")
        return t

    @staticmethod
    def _triage_out(t: Triage | None, lang: str, withheld: bool) -> TriageOut | None:
        if t is None:
            return None
        lab = lambda table, key: table[key].get(lang, table[key]["en"])   # noqa: E731
        return TriageOut(
            category=t.category, category_label=lab(CATEGORY_LABEL, t.category),
            urgency=t.urgency, urgency_label=lab(URGENCY_LABEL, t.urgency) if t.urgency else None,
            action=lab(URGENCY_ACTION, t.urgency) if t.urgency else None,
            category_probability=t.category_probability, urgency_probability=t.urgency_probability,
            uncertain=t.uncertain,
            alternatives=[Alternative(category=c, label=lab(CATEGORY_LABEL, c), probability=p)
                          for c, p in t.alternatives],
            basis=t.basis, safety_flags=t.safety_flags, is_fault=t.is_fault, withheld=withheld,
            model_version=t.model_version,
        )

    def _persist(self, vehicle: VehicleProfile, query: str, lang: str, dtcs: list[str],
                 chunk_ids: list[str], triage: Triage | None = None) -> str | None:
        case_id = time_ordered_id()
        try:
            known = self.repo.existing_codes(dtcs[:1]) if dtcs else set()
            self.repo.insert_diagnostic_case(
                case_id=case_id, user_vehicle_id=vehicle.user_vehicle_id, symptom_text=query,
                language=lang, code=next(iter(known), None),  # FK -> diagnosticcode.code
                evidence_refs=chunk_ids,
                predicted_category=triage.category if triage else None,
                component_group=triage.category if triage else None,
                predicted_urgency=triage.urgency if triage else None,
                confidence=triage.category_probability if triage else None,
            )
            return case_id
        except Exception:  # logging a case must never block the answer
            log.exception("could not persist DiagnosticCase")
            return None

    @staticmethod
    def _vehicle_out(v: VehicleProfile) -> VehicleOut:
        return VehicleOut(user_vehicle_id=v.user_vehicle_id, manufacturer=v.manufacturer,
                          model=v.model, variant=v.variant, year=v.year)
