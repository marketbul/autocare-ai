"""Quality Validation and Missing-Field Analyzer for AI Auto Pakistan.

Calculates completeness scores, identifies broken references, and marks
records needing manual review.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple
from ..schema import AutomotiveRecord
from .normalizer import validate_price_sanity, validate_year_sanity


class RecordQualityValidator:
    """Evaluates record completeness, data sanity, and review readiness."""

    CORE_FIELDS = [
        ("vehicle", "make"),
        ("vehicle", "model"),
        ("vehicle", "manufacturing_year"),
        ("problem", "problem_title"),
        ("problem", "problem_description"),
        ("problem", "symptoms"),
        ("problem", "fault_category"),
        ("source", "source_url"),
        ("source", "language"),
        ("source", "rights_basis"),
    ]

    def evaluate_record(self, record: AutomotiveRecord) -> Dict[str, Any]:
        """Calculates completeness and checks validation constraints."""
        missing_fields: List[str] = []
        filled_count = 0

        flat = record.to_flat_dict()
        for parent, field_name in self.CORE_FIELDS:
            val = flat.get(field_name)
            if val is None or val == "" or val == []:
                missing_fields.append(f"{parent}.{field_name}")
            else:
                filled_count += 1

        completeness_pct = round((filled_count / len(self.CORE_FIELDS)) * 100, 1)

        # Sanity checks
        issues: List[str] = []
        is_year_ok, year_msg = validate_year_sanity(record.vehicle.manufacturing_year)
        if not is_year_ok and year_msg:
            issues.append(year_msg)

        if record.cost:
            is_cost_ok, cost_msg = validate_price_sanity(record.cost.estimated_cost_pkr)
            if not is_cost_ok and cost_msg:
                issues.append(cost_msg)

        # Determine ML-readiness
        is_ml_ready = (
            completeness_pct >= 60.0
            and len(issues) == 0
            and bool(record.problem.fault_category)
            and bool(record.problem.symptoms)
        )

        return {
            "record_id": record.record_id,
            "completeness_score": completeness_pct,
            "missing_core_fields": missing_fields,
            "validation_issues": issues,
            "is_ml_ready": is_ml_ready,
            "needs_manual_review": len(issues) > 0 or completeness_pct < 60.0,
        }
