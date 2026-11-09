"""PakWheels Automotive Knowledge Acquisition Module for AI Auto Pakistan.

Compliant with PakWheels Terms of Service:
- Automated scraping is strictly prohibited.
- Data is collected via structured researcher curation from public forum threads, blogs, and owner reviews.
- Preserves full URL provenance, publication date, and community consensus notes.
"""
from __future__ import annotations

import csv
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


class PakWheelsResearchImporter:
    """Imports human-researched automotive data from PakWheels forums & blogs."""

    REQUIRED_CSV_COLUMNS = [
        "thread_url",
        "thread_date",
        "make",
        "model",
        "variant",
        "manufacturing_year",
        "mileage_km",
        "problem_title",
        "problem_description",
        "symptoms",
        "community_solution",
        "cost_pkr",
        "city",
        "thread_author",
        "evidence_quote",
        "review_status",
    ]

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def import_manual_csv(self, csv_path: Path | str) -> List[AutomotiveRecord]:
        """Loads curated PakWheels research findings into validated AutomotiveRecord models."""
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"PakWheels research CSV not found at: {path}")

        records: List[AutomotiveRecord] = []
        with open(path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            missing = [c for c in self.REQUIRED_CSV_COLUMNS if c not in headers]
            if missing:
                raise ValueError(f"PakWheels research CSV missing required columns: {missing}")

            for row_idx, r in enumerate(reader, start=1):
                url = (r.get("thread_url") or "").strip()
                if not url:
                    continue

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

                mileage_val = None
                if r.get("mileage_km"):
                    try:
                        mileage_val = int(r["mileage_km"].strip())
                    except ValueError:
                        pass

                cost_val = None
                if r.get("cost_pkr"):
                    try:
                        cost_val = float(r["cost_pkr"].strip())
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
                        mileage_km=mileage_val,
                    ),
                    problem=ProblemInfo(
                        problem_title=title,
                        problem_description=desc,
                        symptoms=symps,
                        fault_category=cat_id,
                        diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
                    ),
                    repair=RepairInfo(
                        recommended_solution=r.get("community_solution") or None,
                    ) if r.get("community_solution") else None,
                    cost=CostInfo(
                        estimated_cost_pkr=cost_val,
                        city=r.get("city") or None,
                        price_date=r.get("thread_date") or None,
                        price_source="pakwheels_community",
                    ) if cost_val or r.get("city") else None,
                    source=SourceQualityInfo(
                        source_platform="pakwheels",
                        source_url=url,
                        source_id=f"pw_row_{row_idx}",
                        source_author_or_channel=r.get("thread_author") or None,
                        publication_date=r.get("thread_date") or None,
                        language="roman_ur",
                        rights_basis="manual_research_synthesis",
                        permission_status="terms_compliant_research",
                        human_review_status=(r.get("review_status") or "pending").lower().strip(),
                        evidence_reference=r.get("evidence_quote") or None,
                    ),
                )
                records.append(record)

                self.logger.log(
                    AuditAction.RECORD_INGESTED,
                    source_id="pakwheels_research_import",
                    record_id=record.record_id,
                    status="SUCCESS",
                    details={"thread_url": url, "vehicle": f"{make} {model}"},
                )

        return records
