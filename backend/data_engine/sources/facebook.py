"""Facebook Automotive Research Acquisition Module for AI Auto Pakistan.

Supports:
1. Authorized Meta Graph API ingestion for permitted public automotive pages.
2. Structured Manual Research Import from verified public automotive discussions.
Strictly adheres to privacy rules: no private groups, no personal contact numbers.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from ..cleaning.normalizer import detect_language
from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..media.transcription import COST_MENTION_REGEX
from ..schema import (
    AutomotiveRecord,
    CostInfo,
    ProblemInfo,
    RepairInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from ..taxonomy import DiagnosisStage, get_taxonomy_manager, normalize_make_model
from .submissions import scrub_pii

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

    def _parse_record_from_dict(
        self, r: Dict[str, Any], row_idx: int, source_label: str = "csv"
    ) -> Optional[AutomotiveRecord]:
        """Normalizes a single curated Facebook Q&A dict/CSV row into an AutomotiveRecord."""
        raw_title = (r.get("problem_title") or r.get("question") or "").strip()
        raw_desc = (r.get("problem_description") or r.get("question_details") or raw_title).strip()
        title = scrub_pii(raw_title or raw_desc[:120])
        desc = scrub_pii(raw_desc or title)
        if not title and not desc:
            return None

        url = (r.get("source_url") or f"local://facebook/{source_label}/{row_idx}").strip()

        raw_sol = r.get("proposed_solution") or r.get("solution") or r.get("answers")
        if isinstance(raw_sol, list):
            raw_sol = " | ".join(str(x).strip() for x in raw_sol if str(x).strip())
        proposed_sol = scrub_pii(str(raw_sol or "").strip()) or None

        evidence = scrub_pii((r.get("evidence_quote") or "").strip()) or None

        raw_symps = r.get("symptoms")
        if isinstance(raw_symps, list):
            symps = [scrub_pii(str(s).strip()) for s in raw_symps if str(s).strip()]
        else:
            symps = [scrub_pii(s.strip()) for s in str(raw_symps or "").split(";") if s.strip()]

        make_raw = r.get("make")
        model_raw = r.get("model")
        make, model = normalize_make_model(make_raw, model_raw)
        if not make or make.lower() == "unknown":
            inferred_make, inferred_model = normalize_make_model(
                None, f"{title} {desc} {proposed_sol or ''}"
            )
            make = inferred_make or "Generic"
            model = inferred_model or "Multi-Model"
        elif not model or model.lower() == "unknown":
            model = "Multi-Model"

        year_val = None
        if r.get("manufacturing_year"):
            try:
                year_val = int(str(r["manufacturing_year"]).strip())
            except ValueError:
                pass

        cost_val = None
        if r.get("estimated_cost_pkr"):
            try:
                cost_val = float(str(r["estimated_cost_pkr"]).strip())
            except ValueError:
                pass
        if cost_val is None:
            m = COST_MENTION_REGEX.search(f"{raw_desc} {raw_sol or ''}")
            if m:
                raw_num = m.group(1) or m.group(2)
                if raw_num:
                    try:
                        val = float(raw_num.replace(",", ""))
                        if "hazaar" in m.group(0).lower() or "k" in m.group(0).lower():
                            val *= 1000
                        if 100 <= val <= 2_000_000:
                            cost_val = val
                    except ValueError:
                        pass

        combined_text = f"{title} {desc} {' '.join(symps)}"
        matched_cat = self.taxonomy.match_category_from_text(combined_text)
        cat_id = matched_cat.category_id if matched_cat else None

        lang = detect_language(f"{title} {desc}")
        if lang not in {"en", "ur", "roman_ur", "punjabi"}:
            lang = "roman_ur"

        review_status = str(r.get("review_status") or "pending").lower().strip()
        if review_status not in {"pending", "approved", "rejected", "ml_ready", "example_template"}:
            review_status = "pending"
        verification = "verified" if review_status == "approved" else "unverified"

        fingerprint = hashlib.sha1(f"{url}|{title}".encode("utf-8")).hexdigest()[:12]
        city_val = str(r.get("city") or "").strip() or None
        post_date = str(r.get("post_date") or "").strip() or None

        record = AutomotiveRecord(
            record_id=f"fb_{fingerprint}",
            vehicle=VehicleInfo(
                make=make,
                model=model,
                variant=str(r.get("variant") or "").strip() or None,
                manufacturing_year=year_val,
            ),
            problem=ProblemInfo(
                problem_title=title,
                problem_description=desc,
                symptoms=symps or [title],
                fault_category=cat_id,
                diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
            ),
            repair=RepairInfo(
                recommended_solution=proposed_sol,
                verification_status=verification,
            ) if proposed_sol else None,
            cost=CostInfo(
                estimated_cost_pkr=cost_val,
                city=city_val,
                price_date=post_date,
                price_source="facebook_discussion",
            ) if cost_val or city_val else None,
            source=SourceQualityInfo(
                source_platform="facebook",
                source_url=url,
                source_id=f"fb_{fingerprint}",
                publication_date=post_date,
                language=lang,
                rights_basis="manual_research_synthesis",
                permission_status="public_discussion_research",
                human_review_status=review_status,
                evidence_reference=evidence,
            ),
        )

        self.logger.log(
            AuditAction.RECORD_INGESTED,
            source_id="facebook_research_import",
            record_id=record.record_id,
            status="SUCCESS",
            details={"source_url": url, "vehicle": f"{make} {model}"},
        )
        return record

    def import_manual_csv(self, csv_path: Path | str) -> List[AutomotiveRecord]:
        """Loads human-researched Facebook automotive findings from a strict 14-column CSV."""
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
                if not (r.get("source_url") or "").strip():
                    continue
                rec = self._parse_record_from_dict(r, row_idx, path.stem)
                if rec is not None:
                    records.append(rec)

        return records

    def import_flexible_qa_file(self, file_path: Path | str) -> List[AutomotiveRecord]:
        """Loads public Facebook Q&A records from quick CSV, full CSV, JSON, or JSONL files."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Facebook Q&A file not found at: {path}")

        suffix = path.suffix.lower()
        raw_rows: List[Dict[str, Any]] = []

        if suffix == ".csv":
            with open(path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headers = set(reader.fieldnames or [])
                if not headers.intersection({"problem_title", "question", "problem_description"}):
                    raise ValueError(
                        f"CSV {path.name} must contain at least one of: problem_title, question, problem_description"
                    )
                raw_rows = list(reader)
        elif suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                raw_rows = [x for x in payload if isinstance(x, dict)]
            elif isinstance(payload, dict):
                raw_rows = [
                    x for x in (payload.get("records") or payload.get("items") or []) if isinstance(x, dict)
                ]
        elif suffix == ".jsonl":
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        raw_rows.append(obj)
        else:
            raise ValueError(f"Unsupported Facebook Q&A format: {suffix}. Use .csv, .json, or .jsonl")

        records: List[AutomotiveRecord] = []
        for row_idx, r in enumerate(raw_rows, start=1):
            rec = self._parse_record_from_dict(r, row_idx, path.stem)
            if rec is not None:
                records.append(rec)
        return records
