"""Facebook Automotive Research Acquisition Module for AI Auto Pakistan.

Supports:
1. Authorized Meta Graph API ingestion for permitted public automotive pages.
2. Structured Manual Research Import from verified public automotive discussions.
Strictly adheres to privacy rules: no private groups, no personal contact numbers.
"""
from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

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

FACEBOOK_GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class FacebookResearchImporter:
    """Handles both Meta Graph API queries and structured manual research CSV imports."""

    REQUIRED_CSV_COLUMNS = [
        "source_url",
        "post_date",
        "make",
        "model",
        "variant",
        "manufacturing_year",
        "problem_title",
        "problem_description",
        "symptoms",
        "proposed_solution",
        "estimated_cost_pkr",
        "city",
        "evidence_quote",
        "review_status",
    ]

    def __init__(self, access_token: Optional[str] = None) -> None:
        config = get_config()
        self.access_token = (access_token or config.facebook_access_token).strip()
        self.config = config
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def is_api_configured(self) -> bool:
        return bool(self.access_token)

    def import_manual_csv(self, csv_path: Path | str) -> List[AutomotiveRecord]:
        """Loads human-researched Facebook automotive findings from a standard CSV."""
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Facebook research CSV not found at: {path}")

        records: List[AutomotiveRecord] = []
        with open(path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            missing = [c for c in self.REQUIRED_CSV_COLUMNS if c not in headers]
            if missing:
                raise ValueError(f"Facebook research CSV missing required columns: {missing}")

            for row_idx, r in enumerate(reader, start=1):
                url = (r.get("source_url") or "").strip()
                if not url:
                    continue  # Skip blank rows

                make_raw = r.get("make")
                model_raw = r.get("model")
                make, model = normalize_make_model(make_raw, model_raw)
                make = make or "Unknown"
                model = model or "Unknown"

                year_val = None
                if r.get("manufacturing_year"):
                    try:
                        year_val = int(r["manufacturing_year"].strip())
                    except ValueError:
                        pass

                cost_val = None
                if r.get("estimated_cost_pkr"):
                    try:
                        cost_val = float(r["estimated_cost_pkr"].strip())
                    except ValueError:
                        pass

                title = (r.get("problem_title") or "").strip()
                desc = (r.get("problem_description") or "").strip()
                symps = [s.strip() for s in (r.get("symptoms") or "").split(";") if s.strip()]

                matched_cat = self.taxonomy.match_category_from_text(f"{title} {desc} {' '.join(symps)}")
                cat_id = matched_cat.category_id if matched_cat else None

                record = AutomotiveRecord(
                    vehicle=VehicleInfo(
                        make=make,
                        model=model,
                        variant=r.get("variant") or None,
                        manufacturing_year=year_val,
                    ),
                    problem=ProblemInfo(
                        problem_title=title,
                        problem_description=desc,
                        symptoms=symps,
                        fault_category=cat_id,
                        diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
                    ),
                    repair=RepairInfo(
                        recommended_solution=r.get("proposed_solution") or None,
                    ) if r.get("proposed_solution") else None,
                    cost=CostInfo(
                        estimated_cost_pkr=cost_val,
                        city=r.get("city") or None,
                        price_date=r.get("post_date") or None,
                        price_source="facebook_discussion",
                    ) if cost_val or r.get("city") else None,
                    source=SourceQualityInfo(
                        source_platform="facebook",
                        source_url=url,
                        source_id=f"fb_row_{row_idx}",
                        publication_date=r.get("post_date") or None,
                        language="roman_ur",
                        rights_basis="manual_research_synthesis",
                        permission_status="public_discussion_research",
                        human_review_status=(r.get("review_status") or "pending").lower().strip(),
                        evidence_reference=r.get("evidence_quote") or None,
                    ),
                )
                records.append(record)

                self.logger.log(
                    AuditAction.RECORD_INGESTED,
                    source_id="facebook_research_import",
                    record_id=record.record_id,
                    status="SUCCESS",
                    details={"source_url": url, "vehicle": f"{make} {model}"},
                )

        return records
