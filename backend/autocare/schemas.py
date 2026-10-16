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
