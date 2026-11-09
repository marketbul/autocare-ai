"""Normalized Automotive Data Schema for AI Auto Pakistan.

Implements Section 4 of Master Project Prompt:
- Vehicle Information
- Problem Information
- Audio Acoustic Information
- Image and Video Information
- Repair Information
- Cost Information (PKR)
- Source and Quality Provenance
"""
from __future__ import annotations

import datetime as dt
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class VehicleInfo(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    make: str
    model: str
    variant: Optional[str] = None
    manufacturing_year: Optional[int] = None
    engine_cc: Optional[int] = None
    engine_type: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    mileage_km: Optional[int] = None
    vehicle_generation: Optional[str] = None
    market_country: str = "Pakistan"

    @field_validator("manufacturing_year")
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1960 or v > 2027):
            raise ValueError(f"Manufacturing year {v} is outside valid automotive range (1960-2027)")
        return v

    @field_validator("engine_cc")
    @classmethod
    def validate_cc(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 500 or v > 8000):
            raise ValueError(f"Engine CC {v} is outside typical automotive range (500-8000)")
        return v


class ProblemInfo(BaseModel):
    problem_title: str
    problem_description: str
    symptoms: List[str] = Field(default_factory=list)
    fault_category: Optional[str] = None       # e.g., FC-01, Engine
    affected_component: Optional[str] = None   # e.g., Radiator, Alternator, Brake Pads
    suspected_causes: List[str] = Field(default_factory=list)
    confirmed_causes: List[str] = Field(default_factory=list)
    severity: Optional[str] = None             # critical, high, moderate, low
    problem_frequency: Optional[str] = None    # continuous, intermittent, cold_start, acceleration
    driving_conditions: Optional[str] = None   # highway, stop_and_go_city, uphill, idle
    occurrence_conditions: Optional[str] = None
    diagnosis_stage: str = "owner_reported_problem"

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_clean = v.lower().strip()
            if v_clean not in {"critical", "high", "moderate", "low", "unknown"}:
                return "unknown"
            return v_clean
        return None


class AudioInfo(BaseModel):
    audio_file_reference: Optional[str] = None
    audio_type: Optional[str] = None           # engine_idle, revving, driving, under_load
    sound_description: Optional[str] = None
    sound_category: Optional[str] = None       # Engine knocking, Ticking, Rattling, Grinding, Squealing, Belt noise, Exhaust noise, Misfire, Suspension noise, Wheel bearing noise, Starter motor noise
    engine_rpm: Optional[int] = None
    recording_conditions: Optional[str] = None # bonnet_open, cabin, under_chassis, exhaust_tip
    vehicle_stationary_or_moving: Optional[str] = None # stationary, moving
    audio_quality: Optional[str] = None        # high, acceptable, noisy, poor
    human_verified_label: Optional[bool] = None

    @field_validator("engine_rpm")
    @classmethod
    def validate_rpm(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 400 or v > 10000):
            raise ValueError(f"RPM {v} is outside realistic passenger car range (400-10000)")
        return v


class ImageVideoInfo(BaseModel):
    image_reference: Optional[str] = None
    video_reference: Optional[str] = None
    media_type: Optional[str] = None           # image, video_frame, video_clip
    detected_component: Optional[str] = None   # Engine components, Battery, Radiator, Tires, Brakes, Suspension, Exhaust
    visible_damage: Optional[str] = None       # dent, crack, puncture, oil_leakage, coolant_leakage
    dashboard_warning_light: Optional[str] = None # check_engine, abs, battery, oil_pressure, brake, airbag
    smoke_color: Optional[str] = None          # white, black, blue, grey, none
    image_description: Optional[str] = None
    video_timestamp: Optional[str] = None      # e.g., "02:14"
    annotation_status: Optional[str] = None    # unannotated, model_annotated, human_verified

    @field_validator("smoke_color")
    @classmethod
    def validate_smoke(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_clean = v.lower().strip()
            if v_clean not in {"white", "black", "blue", "grey", "none", "unknown"}:
                return "unknown"
            return v_clean
        return None


class RepairInfo(BaseModel):
    recommended_solution: Optional[str] = None
    repair_steps: List[str] = Field(default_factory=list)
    required_parts: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    repair_difficulty: Optional[str] = None    # easy_diy, moderate, advanced, workshop_only
    estimated_repair_time: Optional[str] = None # e.g. "2 hours"
    mechanic_experience: Optional[str] = None  # e.g. "Senior Engine Specialist, 15 yrs"
    repair_success: Optional[bool] = None
    verification_status: str = "unverified"     # unverified, verified_by_mechanic, verified_by_owner


class CostInfo(BaseModel):
    estimated_cost_pkr: Optional[float] = None
    minimum_cost_pkr: Optional[float] = None
    maximum_cost_pkr: Optional[float] = None
    parts_cost_pkr: Optional[float] = None
    labor_cost_pkr: Optional[float] = None
    price_date: Optional[str] = None           # ISO Date YYYY-MM-DD
    city: Optional[str] = None                 # Lahore, Karachi, Rawalpindi, Islamabad, Peshawar, Faisalabad
    price_source: Optional[str] = None         # workshop_bill, mechanic_quote, owner_receipt, market_survey

    @field_validator("estimated_cost_pkr", "minimum_cost_pkr", "maximum_cost_pkr", "parts_cost_pkr", "labor_cost_pkr")
    @classmethod
    def validate_non_negative_cost(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError(f"Cost cannot be negative: {v}")
        return v


class SourceQualityInfo(BaseModel):
    source_platform: str                      # youtube, facebook, pakwheels, mechanic_interview, owner_submission, manuals
    source_url: Optional[str] = None
    source_id: str
    source_author_or_channel: Optional[str] = None
    publication_date: Optional[str] = None
    collection_date: str = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat())
    language: str = "en"                      # en, ur, roman_ur, punjabi
    evidence_reference: Optional[str] = None
    rights_basis: str                         # official_api_metadata, explicit_consent, user_submission, manual_research_synthesis
    permission_status: str = "pending"        # permitted, consent_signed, public_metadata, pending
    confidence_score: float = 0.5             # 0.0 to 1.0
    human_review_status: str = "pending"      # pending, reviewed, approved, rejected
    reviewer_notes: Optional[str] = None


class AutomotiveRecord(BaseModel):
    """Unified Master Automotive Record for AI Auto Pakistan."""
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vehicle: VehicleInfo
    problem: ProblemInfo
    audio: Optional[AudioInfo] = None
    media: Optional[ImageVideoInfo] = None
    repair: Optional[RepairInfo] = None
    cost: Optional[CostInfo] = None
    source: SourceQualityInfo

    def to_flat_dict(self) -> Dict[str, Any]:
        """Flattens nested attributes for tabular export (CSV, Pandas, Excel)."""
        flat: Dict[str, Any] = {
            "record_id": self.record_id,
            # Vehicle
            "make": self.vehicle.make,
            "model": self.vehicle.model,
            "variant": self.vehicle.variant,
            "manufacturing_year": self.vehicle.manufacturing_year,
            "engine_cc": self.vehicle.engine_cc,
            "engine_type": self.vehicle.engine_type,
            "fuel_type": self.vehicle.fuel_type,
            "transmission": self.vehicle.transmission,
            "mileage_km": self.vehicle.mileage_km,
            "market_country": self.vehicle.market_country,
            # Problem
            "problem_title": self.problem.problem_title,
            "problem_description": self.problem.problem_description,
            "symptoms": "; ".join(self.problem.symptoms),
            "fault_category": self.problem.fault_category,
            "affected_component": self.problem.affected_component,
            "suspected_causes": "; ".join(self.problem.suspected_causes),
            "confirmed_causes": "; ".join(self.problem.confirmed_causes),
            "severity": self.problem.severity,
            "diagnosis_stage": self.problem.diagnosis_stage,
            # Audio
            "audio_file_reference": self.audio.audio_file_reference if self.audio else None,
            "sound_category": self.audio.sound_category if self.audio else None,
            "sound_description": self.audio.sound_description if self.audio else None,
            # Media
            "image_reference": self.media.image_reference if self.media else None,
            "video_reference": self.media.video_reference if self.media else None,
            "detected_component": self.media.detected_component if self.media else None,
            "dashboard_warning_light": self.media.dashboard_warning_light if self.media else None,
            "smoke_color": self.media.smoke_color if self.media else None,
            # Repair
            "recommended_solution": self.repair.recommended_solution if self.repair else None,
            "required_parts": "; ".join(self.repair.required_parts) if self.repair else None,
            "verification_status": self.repair.verification_status if self.repair else None,
            # Cost
            "estimated_cost_pkr": self.cost.estimated_cost_pkr if self.cost else None,
            "parts_cost_pkr": self.cost.parts_cost_pkr if self.cost else None,
            "labor_cost_pkr": self.cost.labor_cost_pkr if self.cost else None,
            "city": self.cost.city if self.cost else None,
            "price_date": self.cost.price_date if self.cost else None,
            # Source
            "source_platform": self.source.source_platform,
            "source_url": self.source.source_url,
            "source_id": self.source.source_id,
            "language": self.source.language,
            "rights_basis": self.source.rights_basis,
            "human_review_status": self.source.human_review_status,
            "confidence_score": self.source.confidence_score,
        }
        return flat
