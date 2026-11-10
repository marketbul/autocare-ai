"""AI-Agent Knowledge & Evaluation Dataset Exporter for AI Auto Pakistan.

Produces a clean, structured JSONL bundle (`data/ml_ready/ai_agent_dataset.jsonl`)
specifically designed for downstream AI Agent RAG pipelines, triage models, and
diagnostic evaluators, preserving strict separation between verified facts and
anecdotal social media / comment claims.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import get_config
from ..storage import StorageManager

VERIFIED_STAGES = frozenset({
    "mechanic_confirmed_diagnosis",
    "verified_repair_outcome",
})


class AIAgentDatasetExporter:
    """Exports cleaned automotive knowledge in an AI-Agent ready JSONL structure."""

    def __init__(self, storage: Optional[StorageManager] = None) -> None:
        self.config = get_config()
        self.storage = storage or StorageManager()

    def build_agent_records(self, include_pending: bool = True) -> List[Dict[str, Any]]:
        items, _ = self.storage.query_records(include_examples=False, limit=10000)
        out: List[Dict[str, Any]] = []

        for it in items:
            status = it.get("human_review_status") or "pending"
            if status == "rejected":
                continue
            if not include_pending and status not in {"ml_ready", "approved", "reviewed"}:
                continue

            stage = it.get("diagnosis_stage") or "owner_reported_problem"
            ver_status = it.get("verification_status") or "unverified"
            is_verified = stage in VERIFIED_STAGES or ver_status in {"verified_by_mechanic", "verified"}

            out.append({
                "id": it["record_id"],
                "vehicle": {
                    "make": it.get("make"),
                    "model": it.get("model"),
                    "variant": it.get("variant"),
                    "year": it.get("manufacturing_year"),
                },
                "fault_category": {
                    "id": it.get("fault_category_id"),
                    "name": it.get("category_name"),
                    "name_roman_ur": it.get("category_roman_ur"),
                },
                "problem_occurrence": {
                    "title": it.get("problem_title"),
                    "description": it.get("problem_description"),
                    "symptoms": it.get("symptoms") or [],
                    "severity": it.get("severity"),
                    "language": it.get("language"),
                },
                "solutions_and_repairs": {
                    "recommended_solution": it.get("recommended_solution"),
                    "required_parts": it.get("required_parts") or [],
                    "diagnosis_stage": stage,
                    "verification_status": ver_status,
                },
                "cost_pkr": {
                    "estimated_total": it.get("estimated_cost_pkr"),
                    "parts_cost": it.get("parts_cost_pkr"),
                    "labor_cost": it.get("labor_cost_pkr"),
                    "city": it.get("city"),
                    "price_date": it.get("price_date"),
                    "price_source": it.get("price_source"),
                } if it.get("estimated_cost_pkr") is not None else None,
                "media_evidence": {
                    "sound_category": it.get("sound_category"),
                    "detected_component": it.get("detected_component"),
                    "dashboard_warning_light": it.get("dashboard_warning_light"),
                    "smoke_color": it.get("smoke_color"),
                },
                "provenance": {
                    "source_id": it.get("source_id"),
                    "source_url": it.get("source_url"),
                    "rights_basis": it.get("rights_basis"),
                    "human_review_status": status,
                    "confidence_score": it.get("confidence_score"),
                    "is_verified_fact": is_verified,
                },
            })
        return out

    def export_jsonl(self, include_pending: bool = True) -> Path:
        records = self.build_agent_records(include_pending=include_pending)
        dest = self.config.ml_ready_dir / "ai_agent_dataset.jsonl"
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return dest
