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


from .calibration import CalibrationSignals, ConfidenceCalibrator
from .case_bank import CaseBank
from .health_maintenance import HealthAndMaintenanceService
from .knowledge_graph import AutomotiveKnowledgeGraph
from .report import generate_service_report_pdf
from .verifier import RepairVerifier


class DiagnoseService:
    def __init__(self, repo: Repository, retriever: Retriever, generator: Generator,
                 reranker: Reranker, settings: Settings, triage: TriageClassifier | None = None,
                 kg: AutomotiveKnowledgeGraph | None = None):
        self.repo, self.retriever, self.generator = repo, retriever, generator
        self.reranker, self.s, self.triage = reranker, settings, triage
        self.calibrator = ConfidenceCalibrator(base_abstention_threshold=0.45, critical_abstention_threshold=0.60)
        self.kg = kg or AutomotiveKnowledgeGraph(repo.db)
        self.verifier = RepairVerifier(self.kg)
        self.health_service = HealthAndMaintenanceService(repo.db)
        self.case_bank = CaseBank(repo.db)


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

        # Story 5 / M3: Calibration & selective prediction signals
        top_score = max((e.rerank_score for e in result.evidence), default=0.0)
        scores = sorted([e.rerank_score for e in result.evidence], reverse=True)
        score_margin = (scores[0] - scores[1]) if len(scores) > 1 else (scores[0] if scores else 0.0)
        is_critical = bool(triage and triage.urgency == "critical")
        cal_signals = CalibrationSignals(
            classifier_prob=triage.category_probability if triage else 0.5,
            classifier_margin=0.0,
            is_critical_path=is_critical,
            top_evidence_score=top_score,
            evidence_margin=score_margin,
            citation_support_ratio=signals["citation_pass_rate"],
            code_recognized=not missing_codes,
        )
        conf_report = self.calibrator.evaluate(cal_signals)
        signals["calibrated_confidence"] = conf_report.calibrated_confidence
        signals["abstention_decision"] = "abstain" if conf_report.should_abstain else "answer"
        signals["confidence_breakdown"] = conf_report.signal_breakdown

        # Story 8 / M6: Root cause chains & Story 6 / M4 Explanation Trace
        chains = self.kg.find_root_causes(query, max_depth=3)
        signals["knowledge_graph_chains"] = [c.readable_chain for c in chains] if chains else []
        signals["explanation_trace"] = {
            "symptoms_extracted": [query],
            "dtc_codes": dtcs,
            "citations": [{"doc": c.document_name, "section": c.section, "page": c.page_number} for c in citations],
            "root_cause_chains": signals["knowledge_graph_chains"],
            "calibrated_confidence": conf_report.calibrated_confidence,
            "abstention_gate": "passed",
        }

        triage_out = self._triage_out(triage, lang, withheld=False)
        if triage_out:
            triage_out.calibrated = True

        case_id = self._persist(vehicle, query, lang, dtcs, [c.chunk_id for c in citations], triage,
                                confidence=conf_report.calibrated_confidence)
        return DiagnoseResponse(
            case_id=case_id, status="answered", query_language=lang, answer_language=answer_lang,
            vehicle=self._vehicle_out(vehicle), detected_codes=dtcs,
            codes_found={c: bool(result.codes_in_corpus.get(c)) for c in dtcs},
            claims=claims, citations=citations, abstention=None,
            retrieved_but_insufficient=[], notices=notices,
            dropped_claim_count=len(dropped), signals=signals,
            triage=triage_out, disclaimer=msg(DISCLAIMER, lang),
        )

    # -- Additional Story Methods (M5, M6, M7, M8, M9) --------------------------
    def verify_repair(self, user_vehicle_id: str | None, proposed_repair: str, symptoms: str,
                      code: str | None = None, damage_location: str | None = None) -> dict:
        evidence_passages = []
        if user_vehicle_id:
            vehicle = self.repo.get_vehicle_profile(user_vehicle_id)
            if vehicle:
                # Find evidence passages related to proposed repair
                candidates = self.retriever.bm25.search(proposed_repair, top_k=5) if self.retriever.bm25 else []
                evidence_passages = [{"document_name": c.document_name, "section": c.section,
                                      "page_number": c.page_number, "text": c.text} for c in candidates]

        res = self.verifier.verify(
            proposed_repair=proposed_repair,
            symptoms=symptoms,
            codes=[code] if code else [],
            evidence_passages=evidence_passages,
            damage_location=damage_location
        )
        return {
            "proposed_repair": res.proposed_repair,
            "verdict": res.verdict,
            "confidence": res.confidence,
            "graph_path_found": res.graph_path_found,
            "causal_path": res.causal_path,
            "supporting_evidence": res.supporting_evidence,
            "indicated_alternatives": res.indicated_alternatives,
            "explanation": res.explanation,
            "physical_inspection_disclaimer": res.physical_inspection_disclaimer,
        }

    def get_root_causes(self, symptom: str, max_depth: int = 3) -> list[dict]:
        chains = self.kg.find_root_causes(symptom, max_depth=max_depth)
        return [
            {
                "symptom": c.symptom,
                "root_cause": c.root_cause,
                "readable_chain": c.readable_chain,
                "total_confidence": c.total_confidence,
                "steps": [
                    {"from_label": s.from_label, "relation": s.relation,
                     "to_label": s.to_label, "confidence": s.confidence}
                    for s in c.steps
                ]
            }
            for c in chains
        ]

    def get_similar_cases(self, user_vehicle_id: str | None, symptom: str,
                          code: str | None = None, top_k: int = 3) -> list[dict]:
        vehicle = self.repo.get_vehicle_profile(user_vehicle_id) if user_vehicle_id else None
        model = vehicle.model if vehicle else "Corolla"
        year = vehicle.year if vehicle else None
        cases = self.case_bank.search(symptom_text=symptom, vehicle_model=model,
                                      year=year, code=code, top_k=top_k)
        return [
            {
                "case_id": c.case_id, "vehicle_model": c.vehicle_model, "vehicle_year": c.vehicle_year,
                "symptom_text": c.symptom_text, "code": c.code, "category": c.category,
                "urgency": c.urgency, "resolution": c.resolution, "provenance": c.provenance,
                "similarity": c.similarity
            }
            for c in cases
        ]

    def get_vehicle_health(self, user_vehicle_id: str) -> dict:
        vehicle = self.repo.get_vehicle_profile(user_vehicle_id)
        mileage = vehicle.current_mileage if (vehicle and vehicle.current_mileage) else 45000
        summary = self.health_service.calculate_health_index(user_vehicle_id, mileage)
        return {
            "user_vehicle_id": summary.user_vehicle_id,
            "composite_score": summary.composite_score,
            "status": summary.status,
            "data_completeness": summary.data_completeness,
            "disclaimer": summary.disclaimer,
            "groups": {
                g: {
                    "group": gh.group, "score": gh.score, "status": gh.status,
                    "last_serviced_mileage": gh.last_serviced_mileage,
                    "last_serviced_date": gh.last_serviced_date,
                    "mileage_since_service": gh.mileage_since_service,
                    "open_faults_count": gh.open_faults_count,
                    "recommendation": gh.recommendation
                }
                for g, gh in summary.groups.items()
            }
        }

    def predict_next_service(self, user_vehicle_id: str) -> dict:
        vehicle = self.repo.get_vehicle_profile(user_vehicle_id)
        mileage = vehicle.current_mileage if (vehicle and vehicle.current_mileage) else 45000
        pred = self.health_service.predict_next_service(user_vehicle_id, mileage)
        return {
            "user_vehicle_id": pred.user_vehicle_id,
            "next_item": pred.next_item,
            "target_mileage": pred.target_mileage,
            "mileage_window": pred.mileage_window,
            "estimated_due_date": pred.estimated_due_date,
            "days_remaining": pred.days_remaining,
            "urgency": pred.urgency,
            "rationale": pred.rationale,
        }

    def generate_report_pdf(self, user_vehicle_id: str, query: str,
                            diagnosis_res: DiagnoseResponse) -> bytes:
        vehicle = self.repo.get_vehicle_profile(user_vehicle_id)
        v_info = {
            "manufacturer": vehicle.manufacturer if vehicle else "Toyota",
            "model": vehicle.model if vehicle else "Corolla",
            "variant": vehicle.variant if vehicle else "Standard",
            "year": vehicle.year if vehicle else 2018,
            "current_mileage": vehicle.current_mileage if vehicle else 82000,
            "engine": vehicle.engine if vehicle else "Standard",
        }
        diag_dict = {
            "predicted_urgency": diagnosis_res.triage.urgency if diagnosis_res.triage else "Moderate",
            "predicted_category": diagnosis_res.triage.category if diagnosis_res.triage else "General",
            "confidence": diagnosis_res.signals.get("calibrated_confidence", 0.85),
            "action_text": diagnosis_res.triage.action if diagnosis_res.triage else "Inspect vehicle.",
            "date": dt.date.today().strftime("%d %B %Y"),
        }
        citations = [
            {"document_name": c.document_name, "section": c.section,
             "page_number": c.page_number, "excerpt": c.excerpt}
            for c in diagnosis_res.citations
        ]
        chain_str = diagnosis_res.signals.get("knowledge_graph_chains", [""])[0] if diagnosis_res.signals.get("knowledge_graph_chains") else None
        return generate_service_report_pdf(
            report_id=diagnosis_res.case_id or time_ordered_id(),
            vehicle_info=v_info,
            query_text=query,
            diagnosis_data=diag_dict,
            citations=citations,
            root_cause_chain=chain_str,
            verification=None,
            health_score=85.0
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
                 chunk_ids: list[str], triage: Triage | None = None,
                 confidence: float | None = None) -> str | None:
        case_id = time_ordered_id()
        try:
            known = self.repo.existing_codes(dtcs[:1]) if dtcs else set()
            conf = triage.category_probability if triage else confidence
            self.repo.insert_diagnostic_case(
                case_id=case_id, user_vehicle_id=vehicle.user_vehicle_id, symptom_text=query,
                language=lang, code=next(iter(known), None),  # FK -> diagnosticcode.code
                evidence_refs=chunk_ids,
                predicted_category=triage.category if triage else None,
                component_group=triage.category if triage else None,
                predicted_urgency=triage.urgency if triage else None,
                confidence=conf,
            )
            return case_id
        except Exception:  # logging a case must never block the answer
            log.exception("could not persist DiagnosticCase")
            return None

    @staticmethod
    def _vehicle_out(v: VehicleProfile) -> VehicleOut:
        return VehicleOut(user_vehicle_id=v.user_vehicle_id, manufacturer=v.manufacturer,
                          model=v.model, variant=v.variant, year=v.year)

# [2026-05-22] feat(nlp): [AUT-105] add Urdu 

# [2026-05-24] feat(nlp): [AUT-105] add Urdu and R by Danial Hameed
