"""Authorized Automotive Websites & Technical Blogs Importer for AI Auto Pakistan.

Supports importing structured research findings from authorized automotive websites,
RSS/API feeds, or human-curated technical blog notes while preserving attribution and permissions.
Strictly prohibits unauthorized scraping or bypassing website Terms of Service.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List

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


class AutomotiveBlogImporter:
    """Imports curated articles and guides from authorized automotive websites & blogs."""

    REQUIRED_CSV_COLUMNS = [
        "article_url",
        "publish_date",
        "website_name",
        "make",
        "model",
        "variant",
        "manufacturing_year",
        "article_title",
        "problem_summary",
        "symptoms",
        "recommended_solution",
        "estimated_cost_pkr",
        "permission_status",
        "evidence_quote",
    ]

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def import_manual_csv(self, csv_path: Path | str) -> List[AutomotiveRecord]:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Automotive blog CSV not found at: {path}")

        records: List[AutomotiveRecord] = []
        with open(path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            missing = [c for c in self.REQUIRED_CSV_COLUMNS if c not in headers]
            if missing:
                raise ValueError(f"Automotive blog CSV missing required columns: {missing}")

            for row_idx, r in enumerate(reader, start=1):
                url = (r.get("article_url") or "").strip()
                if not url:
                    continue

                make, model = normalize_make_model(r.get("make"), r.get("model"))
                make = make or "Universal"
                model = model or "General"

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

                title = (r.get("article_title") or "").strip()
                desc = (r.get("problem_summary") or "").strip()
                symps = [s.strip() for s in (r.get("symptoms") or "").split(";") if s.strip()]

                matched = self.taxonomy.match_category_from_text(f"{title} {desc} {' '.join(symps)}")
                cat_id = matched.category_id if matched else None

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
                        symptoms=symps or [title],
                        fault_category=cat_id,
                        diagnosis_stage=DiagnosisStage.MECHANIC_SUGGESTED_CAUSE.value,
                    ),
                    repair=RepairInfo(
                        recommended_solution=r.get("recommended_solution") or None,
                    ) if r.get("recommended_solution") else None,
                    cost=CostInfo(
                        estimated_cost_pkr=cost_val,
                        price_date=r.get("publish_date") or None,
                        price_source=r.get("website_name") or "automotive_blog",
                    ) if cost_val else None,
                    source=SourceQualityInfo(
                        source_platform="automotive_blog",
                        source_url=url,
                        source_id=f"blog_row_{row_idx}",
                        source_author_or_channel=r.get("website_name") or None,
                        publication_date=r.get("publish_date") or None,
                        language="en",
                        rights_basis="manual_research_synthesis",
                        permission_status=(r.get("permission_status") or "authorized_reference").strip(),
                        human_review_status="pending",
                        evidence_reference=r.get("evidence_quote") or None,
                        confidence_score=0.75,
                    ),
                )
                records.append(record)
                self.logger.log(
                    AuditAction.RECORD_INGESTED,
                    source_id="automotive_blog_research",
                    record_id=record.record_id,
                    status="SUCCESS",
                    details={"article_url": url, "website": r.get("website_name")},
                )
        return records
