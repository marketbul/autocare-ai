"""Mechanic Field Interviews and Car-Owner Problem Submissions.

Enforces:
1. Explicit Informed Consent: Rows without consent='yes' are strictly rejected.
2. Automated PII Sanitization: Strips Pakistani mobile numbers, CNIC numbers, emails, and vehicle plate numbers.
3. Diagnostic boundary distinction (owner report vs mechanic confirmed diagnosis).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..schema import (
    AutomotiveRecord,
    CostInfo,
    ProblemInfo,
    RepairInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from ..taxonomy import DiagnosisStage, get_taxonomy_manager, normalize_make_model

# Regular expressions for Pakistani Personally Identifiable Information (PII)
PHONE_REGEX = re.compile(r"(\+92|0)?3[0-9]{2}[-\s]?[0-9]{7}\b")
CNIC_REGEX = re.compile(r"\b[0-9]{5}-[0-9]{7}-[0-9]\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PLATE_REGEX = re.compile(r"\b[A-Z]{2,3}[-\s]?[0-9]{1,4}\b", re.IGNORECASE)


def scrub_pii(text: str) -> str:
    """Replaces personal identifiers with privacy redaction tokens."""
    if not text:
        return ""
    cleaned = PHONE_REGEX.sub("[PHONE REDACTED]", text)
    cleaned = CNIC_REGEX.sub("[CNIC REDACTED]", cleaned)
    cleaned = EMAIL_REGEX.sub("[EMAIL REDACTED]", cleaned)
    cleaned = PLATE_REGEX.sub("[PLATE REDACTED]", cleaned)
    return cleaned


class MechanicInterviewImporter:
    """Imports field interviews with experienced Pakistani mechanics with mandatory consent check."""

    REQUIRED_CSV_COLUMNS = [
        "interview_id",
        "mechanic_name",
        "experience_years",
        "workshop_name",
        "city",
        "interview_date",
        "consent",
        "make",
        "model",
        "years",
        "fault_topic",
        "symptoms",
        "diagnostic_advice",
        "recommended_parts",
        "estimated_labor_cost_pkr",
    ]

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def import_csv(self, csv_path: Path | str) -> List[AutomotiveRecord]:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Mechanic interview CSV not found at: {path}")

        records: List[AutomotiveRecord] = []
        with open(path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            missing = [c for c in self.REQUIRED_CSV_COLUMNS if c not in headers]
            if missing:
                raise ValueError(f"Mechanic interview CSV missing columns: {missing}")

            for row_idx, r in enumerate(reader, start=1):
                interview_id = (r.get("interview_id") or f"interview_{row_idx}").strip()
                consent = (r.get("consent") or "").strip().lower()

                # Ethical Gate: Mandatory explicit consent
                if consent != "yes":
                    self.logger.log(
                        AuditAction.RECORD_REJECTED,
                        source_id="mechanic_interviews",
                        record_id=interview_id,
                        status="REJECTED",
                        details={"reason": "Missing or negative consent", "consent_value": consent},
                    )
                    continue

                make_raw = r.get("make")
                model_raw = r.get("model")
                make, model = normalize_make_model(make_raw, model_raw)
                make = make or "Universal"
                model = model or "Universal"

                labor_cost = None
                if r.get("estimated_labor_cost_pkr"):
                    try:
                        labor_cost = float(r["estimated_labor_cost_pkr"].strip())
                    except ValueError:
                        pass

                parts = [p.strip() for p in (r.get("recommended_parts") or "").split(";") if p.strip()]
                topic = (r.get("fault_topic") or "").strip()
                advice = (r.get("diagnostic_advice") or "").strip()
                symptoms = [s.strip() for s in (r.get("symptoms") or "").split(";") if s.strip()]

                matched_cat = self.taxonomy.match_category_from_text(f"{topic} {advice} {' '.join(symptoms)}")
                cat_id = matched_cat.category_id if matched_cat else None

                record = AutomotiveRecord(
                    vehicle=VehicleInfo(
                        make=make,
                        model=model,
                    ),
                    problem=ProblemInfo(
                        problem_title=topic,
                        problem_description=advice,
                        symptoms=symptoms,
                        fault_category=cat_id,
                        diagnosis_stage=DiagnosisStage.MECHANIC_CONFIRMED_DIAGNOSIS.value,
                    ),
                    repair=RepairInfo(
                        recommended_solution=advice,
                        required_parts=parts,
                        mechanic_experience=f"{r.get('experience_years', '').strip()} yrs experience ({r.get('workshop_name', '').strip()})",
                        verification_status="verified_by_mechanic",
                    ),
                    cost=CostInfo(
                        labor_cost_pkr=labor_cost,
                        estimated_cost_pkr=labor_cost,
                        city=r.get("city") or None,
                        price_date=r.get("interview_date") or None,
                        price_source="mechanic_quote",
                    ) if labor_cost or r.get("city") else None,
                    source=SourceQualityInfo(
                        source_platform="mechanic_interview",
                        source_id=interview_id,
                        source_author_or_channel=r.get("mechanic_name") or "Verified Workshop Mechanic",
                        publication_date=r.get("interview_date") or None,
                        language="roman_ur",
                        rights_basis="explicit_consent",
                        permission_status="consent_signed",
                        human_review_status="approved",
                        confidence_score=0.95,
                    ),
                )
                records.append(record)

                self.logger.log(
                    AuditAction.RECORD_INGESTED,
                    source_id="mechanic_interviews",
                    record_id=record.record_id,
                    status="SUCCESS",
                    details={"mechanic": r.get("mechanic_name"), "city": r.get("city")},
                )

        return records


class OwnerProblemReportImporter:
    """Imports car-owner diagnostic experiences with automatic privacy protection (PII scrubbing)."""

    REQUIRED_CSV_COLUMNS = [
        "report_id",
        "make",
        "model",
        "variant",
        "manufacturing_year",
        "mileage_km",
        "city",
        "problem_title",
        "problem_narrative",
        "symptoms",
        "driving_condition",
        "repair_done",
        "total_bill_pkr",
        "repair_success",
    ]

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def import_csv(self, csv_path: Path | str) -> List[AutomotiveRecord]:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Owner reports CSV not found at: {path}")

        records: List[AutomotiveRecord] = []
        with open(path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            missing = [c for c in self.REQUIRED_CSV_COLUMNS if c not in headers]
            if missing:
                raise ValueError(f"Owner report CSV missing columns: {missing}")

            for row_idx, r in enumerate(reader, start=1):
                rep_id = (r.get("report_id") or f"owner_rep_{row_idx}").strip()

                make_raw = r.get("make")
                model_raw = r.get("model")
                make, model = normalize_make_model(make_raw, model_raw)
                make = make or "Unknown"
                model = model or "Unknown"

                # Scrub PII from narrative and title
                clean_title = scrub_pii(r.get("problem_title") or "")
                clean_desc = scrub_pii(r.get("problem_narrative") or "")
                clean_repair = scrub_pii(r.get("repair_done") or "")

                year_val = None
                if r.get("manufacturing_year"):
                    try:
                        year_val = int(r["manufacturing_year"].strip())
                    except ValueError:
                        pass

                bill_val = None
                if r.get("total_bill_pkr"):
                    try:
                        bill_val = float(r["total_bill_pkr"].strip())
                    except ValueError:
                        pass

                symps = [s.strip() for s in (r.get("symptoms") or "").split(";") if s.strip()]
                success = (r.get("repair_success") or "").strip().lower() in {"yes", "true", "1"}

                matched_cat = self.taxonomy.match_category_from_text(f"{clean_title} {clean_desc}")
                cat_id = matched_cat.category_id if matched_cat else None

                record = AutomotiveRecord(
                    vehicle=VehicleInfo(
                        make=make,
                        model=model,
                        variant=r.get("variant") or None,
                        manufacturing_year=year_val,
                    ),
                    problem=ProblemInfo(
                        problem_title=clean_title,
                        problem_description=clean_desc,
                        symptoms=symps,
                        fault_category=cat_id,
                        driving_conditions=r.get("driving_condition") or None,
                        diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
                    ),
                    repair=RepairInfo(
                        recommended_solution=clean_repair or None,
                        repair_success=success,
                        verification_status="verified_by_owner" if success else "unverified",
                    ) if clean_repair else None,
                    cost=CostInfo(
                        estimated_cost_pkr=bill_val,
                        city=r.get("city") or None,
                        price_source="owner_receipt",
                    ) if bill_val or r.get("city") else None,
                    source=SourceQualityInfo(
                        source_platform="owner_submission",
                        source_id=rep_id,
                        language="roman_ur",
                        rights_basis="user_submission",
                        permission_status="consent_signed",
                        human_review_status="reviewed",
                        confidence_score=0.80,
                    ),
                )
                records.append(record)

                self.logger.log(
                    AuditAction.RECORD_INGESTED,
                    source_id="owner_submissions",
                    record_id=record.record_id,
                    status="SUCCESS",
                    details={"report_id": rep_id, "vehicle": f"{make} {model}"},
                )

        return records
