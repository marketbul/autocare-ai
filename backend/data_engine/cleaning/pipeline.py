"""Data Cleaning and Processing Pipeline Orchestrator for AI Auto Pakistan.

Coordinates:
1. Multilingual term normalization and language tagging
2. Deduplication across Video IDs, URLs, and symptom fingerprints
3. Schema validation and quality score calculation
4. Exporting processed records to data/processed/
5. Provenance tracking in audit log (zero silent record drops)
"""
from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..schema import AutomotiveRecord
from .deduplication import DeduplicationEngine
from .normalizer import detect_language, normalize_automotive_text
from .validator import RecordQualityValidator


class CleaningPipeline:
    """End-to-end data processing and validation engine."""

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.dedup = DeduplicationEngine()
        self.validator = RecordQualityValidator()

    def process_batch(self, raw_records: List[AutomotiveRecord]) -> Dict[str, Any]:
        """Runs normalization, deduplication, and quality validation on a batch."""
        if not raw_records:
            return {"total_input": 0, "unique_processed": 0, "duplicates_flagged": 0}

        # Step 1: Normalization
        for rec in raw_records:
            # Normalize text
            rec.problem.problem_title = normalize_automotive_text(rec.problem.problem_title)
            rec.problem.problem_description = normalize_automotive_text(rec.problem.problem_description)
            rec.problem.symptoms = [normalize_automotive_text(s) for s in rec.problem.symptoms]

            # Detect language if unspecified or generic
            if rec.source.language in {"en", "unknown", ""}:
                detected = detect_language(f"{rec.problem.problem_title} {rec.problem.problem_description}")
                rec.source.language = detected

        # Step 2: Deduplication
        unique_records, duplicates = self.dedup.process_records(raw_records)

        # Step 3: Quality Validation & Status Flagging
        processed_records: List[Dict[str, Any]] = []
        ml_ready_count = 0
        needs_review_count = 0

        for rec in unique_records:
            eval_res = self.validator.evaluate_record(rec)
            if eval_res["is_ml_ready"]:
                ml_ready_count += 1
                rec.source.human_review_status = "ml_ready"
            elif eval_res["needs_manual_review"]:
                needs_review_count += 1
                rec.source.human_review_status = "needs_review"

            rec_dict = rec.model_dump()
            rec_dict["quality_eval"] = eval_res
            processed_records.append(rec_dict)

            self.logger.log(
                AuditAction.RECORD_VALIDATED,
                source_id=rec.source.source_platform,
                record_id=rec.record_id,
                status="SUCCESS",
                details={
                    "completeness": eval_res["completeness_score"],
                    "is_ml_ready": eval_res["is_ml_ready"],
                },
            )

        # Step 4: Save Processed Batch to data/processed/
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
        jsonl_path = self.config.processed_dir / f"processed_{timestamp}.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for item in processed_records:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        # Tabular CSV export
        csv_path = self.config.processed_dir / f"processed_{timestamp}.csv"
        flat_rows = [rec.to_flat_dict() for rec in unique_records]
        if flat_rows:
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=list(flat_rows[0].keys()))
                writer.writeheader()
                writer.writerows(flat_rows)

        summary = {
            "total_input": len(raw_records),
            "unique_processed": len(unique_records),
            "duplicates_flagged": len(duplicates),
            "ml_ready_records": ml_ready_count,
            "needs_review_records": needs_review_count,
            "processed_jsonl_output": str(jsonl_path),
            "processed_csv_output": str(csv_path),
        }
        return summary
