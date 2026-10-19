"""API request/response contract for POST /api/v1/diagnose/query."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Lang = Literal["en", "ur", "roman_ur"]


class DiagnoseRequest(BaseModel):
    user_vehicle_id: Optional[str] = Field(None, description="Active vehicle profile (Story 1).")
    query: str = Field(..., min_length=1, max_length=1000)
    code_source: Literal["typed", "photo"] = "typed"   # Story 3: code read from a scanner photo


class VehicleOut(BaseModel):
    user_vehicle_id: str
    manufacturer: str
    model: str
    variant: Optional[str]
    year: int


class Citation(BaseModel):
    number: int                          # [1], [2] ... as shown in the UI
    chunk_id: str
    document_id: str
    document_name: str
    document_type: str
    section: Optional[str]
    page_number: Optional[int]
    excerpt: str


class Claim(BaseModel):
    text: str
    citations: list[int] = Field(..., min_length=1)   # AC2: never empty


class RetrievedPassage(BaseModel):
    document_name: str
    section: Optional[str]
    page_number: Optional[int]
    excerpt: str
    score: float


class Abstention(BaseModel):
    reason: Literal["no_strong_match", "code_not_found", "no_supported_claims"]
    message: str


class Alternative(BaseModel):
    category: str
    label: str
    probability: float


class TriageOut(BaseModel):
    """Story 4 / M2. `withheld` = the answer abstained, so no label is presented as
    reliable (Story 5); only a safety warning from a hazard rule may still be shown."""
    category: str
    category_label: str
    urgency: Optional[Literal["low", "moderate", "high", "critical"]]
    urgency_label: Optional[str]
    action: Optional[str]
    category_probability: float
    urgency_probability: Optional[float]
    uncertain: bool
    alternatives: list[Alternative]
    basis: list[str]
    safety_flags: list[str]
    is_fault: bool
    withheld: bool
    model_version: Optional[str]
    calibrated: bool = False


class DiagnoseResponse(BaseModel):
    case_id: Optional[str]
    status: Literal["answered", "abstained"]
    query_language: Lang
    answer_language: Lang
    vehicle: VehicleOut
    detected_codes: list[str]
    codes_found: dict[str, bool]
    claims: list[Claim]
    citations: list[Citation]
    abstention: Optional[Abstention]
    retrieved_but_insufficient: list[RetrievedPassage]
    notices: list[str]
    dropped_claim_count: int
    signals: dict                         # retrieval-strength inputs for M3
    triage: Optional[TriageOut] = None    # Story 4
    disclaimer: str


class ErrorResponse(BaseModel):
    error: Literal["vehicle_profile_required", "unsupported_vehicle", "generation_failed"]
    message: str
    language: Lang


# Story 6 / M4: Explanation Trace
class ExplanationTrace(BaseModel):
    extracted_symptoms: list[str]
    detected_codes: list[str]
    citations_used: list[dict]
    knowledge_graph_relations: list[str] = Field(default_factory=list)
    classifier_contribution: dict = Field(default_factory=dict)
    calibrated_confidence: float
    abstention_gate_decision: str


# Story 7 / M5: Repair Verifier
class VerifyRepairRequest(BaseModel):
    user_vehicle_id: Optional[str] = None
    proposed_repair: str
    symptoms: str
    code: Optional[str] = None
    damage_location: Optional[str] = None


class VerifyRepairResponse(BaseModel):
    proposed_repair: str
    verdict: Literal["supported", "partially_supported", "unsupported"]
    confidence: float
    graph_path_found: bool
    causal_path: list[str]
    supporting_evidence: list[str]
    indicated_alternatives: list[str]
    explanation: str
    physical_inspection_disclaimer: str


# Story 8 / M6: Knowledge Graph Root Cause
class RootCauseRequest(BaseModel):
    symptom: str
    max_depth: int = 3


class CausalStepOut(BaseModel):
    from_label: str
    relation: str
    to_label: str
    confidence: float


class CausalChainOut(BaseModel):
    symptom: str
    root_cause: str
    readable_chain: str
    total_confidence: float
    steps: list[CausalStepOut]


class RootCauseResponse(BaseModel):
    symptom: str
    chains: list[CausalChainOut]


# Story 9 / M8: Similar Cases
class SimilarCasesRequest(BaseModel):
    user_vehicle_id: Optional[str] = None
    symptom: str
    code: Optional[str] = None
    top_k: int = 3


class SimilarCaseOut(BaseModel):
    case_id: str
    vehicle_model: str
    vehicle_year: Optional[int]
    symptom_text: str
    code: Optional[str]
    category: Optional[str]
    urgency: Optional[str]
    resolution: str
    provenance: str
    similarity: float


class SimilarCasesResponse(BaseModel):
    cases: list[SimilarCaseOut]


# Story 10 & 11 / M7: Health Index & Maintenance Prediction
class GroupHealthOut(BaseModel):
    group: str
    score: float
    status: str
    last_serviced_mileage: Optional[int]
    last_serviced_date: Optional[str]
    mileage_since_service: int
    open_faults_count: int
    recommendation: str


class HealthIndexResponse(BaseModel):
    user_vehicle_id: str
    composite_score: float
    status: str
    groups: dict[str, GroupHealthOut]
    data_completeness: str
    disclaimer: str


class NextServiceResponse(BaseModel):
    user_vehicle_id: str
    next_item: str
    target_mileage: int
    mileage_window: tuple[int, int]
    estimated_due_date: str
    days_remaining: int
    urgency: str
    rationale: str


# [2026-05-31] fix(ocr): [AUT-106B] enhance contrast and binarization for low-light scanner screens
# [2026-07-08] feat(trace): [AUT-111] assemble transparent multi-hop explanation traces (M4)
