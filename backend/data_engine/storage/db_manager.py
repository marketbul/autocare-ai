"""Database Storage Manager for AI Auto Pakistan.

Handles relational database initialization, records ingestion, foreign keys,
and multi-dimensional metrics querying. Supports SQLite (local prototyping) and PostgreSQL.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..registry import create_default_source_registry
from ..schema import AutomotiveRecord
from ..taxonomy import AUTOMOTIVE_FAULT_CATEGORIES


PLATFORM_TO_SOURCE_ID = {
    "youtube": "youtube_official_api",
    "facebook": "facebook_research_import",
    "pakwheels": "pakwheels_research_import",
    "mechanic_interview": "mechanic_interviews",
    "owner_submission": "owner_submissions",
    "manuals": "manuals_and_bulletins",
}


class StorageManager:
    """Relational database gateway for automotive datasets."""

    def __init__(self, db_path: Optional[Path | str] = None) -> None:
        config = get_config()
        self.db_path = Path(db_path or (config.backend_root / "autocare.db"))
        self.logger = get_audit_logger()
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_database(self) -> None:
        """Executes DDL schema and seeds baseline sources and taxonomy."""
        schema_path = Path(__file__).parent / "schema.data_engine.sql"
        if not schema_path.exists():
            return

        with open(schema_path, "r", encoding="utf-8") as f:
            ddl = f.read()

        with self._get_connection() as conn:
            conn.executescript(ddl)

            # Seed Registered Sources
            registry = create_default_source_registry()
            for s in registry.list_all():
                conn.execute(
                    """INSERT OR IGNORE INTO data_sources
                    (source_id, name, source_type, rights_basis, is_automated, requires_api_key, attribution_required, rate_limit_policy, enabled, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        s.source_id,
                        s.name,
                        s.source_type.value,
                        s.rights_basis.value,
                        s.is_automated,
                        s.requires_api_key,
                        s.attribution_required,
                        s.rate_limit_policy,
                        s.enabled,
                        s.description,
                    ),
                )

            # Seed Fault Categories
            for cat in AUTOMOTIVE_FAULT_CATEGORIES.values():
                conn.execute(
                    """INSERT OR IGNORE INTO fault_categories
                    (category_id, name, name_ur, name_roman_ur, description, subcomponents_json, symptom_keywords_json, typical_causes_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        cat.category_id,
                        cat.name,
                        cat.name_ur,
                        cat.name_roman_ur,
                        cat.description,
                        json.dumps(cat.subcomponents, ensure_ascii=False),
                        json.dumps(cat.multilingual_symptom_keywords, ensure_ascii=False),
                        json.dumps(cat.typical_causes, ensure_ascii=False),
                    ),
                )
            conn.commit()

    def insert_record(self, record: AutomotiveRecord) -> None:
        """Upserts a single AutomotiveRecord into relational storage."""
        with self._get_connection() as conn:
            # 1. Upsert Vehicle
            veh_id = f"{record.vehicle.make.lower()}-{record.vehicle.model.lower()}-{record.vehicle.manufacturing_year or 'any'}"
            conn.execute(
                """INSERT OR IGNORE INTO vehicle_fleet
                (vehicle_id, make, model, variant, manufacturing_year, engine_cc, engine_type, fuel_type, transmission, market_country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    veh_id,
                    record.vehicle.make,
                    record.vehicle.model,
                    record.vehicle.variant,
                    record.vehicle.manufacturing_year,
                    record.vehicle.engine_cc,
                    record.vehicle.engine_type,
                    record.vehicle.fuel_type,
                    record.vehicle.transmission,
                    record.vehicle.market_country,
                ),
            )

            # 2. Insert Diagnostic Record
            source_key = PLATFORM_TO_SOURCE_ID.get(record.source.source_platform, record.source.source_platform)
            cat_id = record.problem.fault_category if record.problem.fault_category in AUTOMOTIVE_FAULT_CATEGORIES else None

            conn.execute(
                """INSERT OR REPLACE INTO diagnostic_records
                (record_id, vehicle_id, fault_category_id, source_id, problem_title, problem_description,
                 symptoms_json, suspected_causes_json, confirmed_causes_json, severity, diagnosis_stage,
                 sound_category, sound_description, detected_component, dashboard_warning_light, smoke_color,
                 recommended_solution, repair_steps_json, required_parts_json, repair_success, verification_status,
                 estimated_cost_pkr, parts_cost_pkr, labor_cost_pkr, city, price_date, price_source,
                 source_url, publication_date, collection_date, language, rights_basis, confidence_score,
                 human_review_status, reviewer_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.record_id,
                    veh_id,
                    cat_id,
                    source_key,
                    record.problem.problem_title,
                    record.problem.problem_description,
                    json.dumps(record.problem.symptoms, ensure_ascii=False),
                    json.dumps(record.problem.suspected_causes, ensure_ascii=False),
                    json.dumps(record.problem.confirmed_causes, ensure_ascii=False),
                    record.problem.severity,
                    record.problem.diagnosis_stage,
                    record.audio.sound_category if record.audio else None,
                    record.audio.sound_description if record.audio else None,
                    record.media.detected_component if record.media else None,
                    record.media.dashboard_warning_light if record.media else None,
                    record.media.smoke_color if record.media else None,
                    record.repair.recommended_solution if record.repair else None,
                    json.dumps(record.repair.repair_steps if record.repair else [], ensure_ascii=False),
                    json.dumps(record.repair.required_parts if record.repair else [], ensure_ascii=False),
                    record.repair.repair_success if record.repair else None,
                    record.repair.verification_status if record.repair else "unverified",
                    record.cost.estimated_cost_pkr if record.cost else None,
                    record.cost.parts_cost_pkr if record.cost else None,
                    record.cost.labor_cost_pkr if record.cost else None,
                    record.cost.city if record.cost else None,
                    record.cost.price_date if record.cost else None,
                    record.cost.price_source if record.cost else None,
                    record.source.source_url,
                    record.source.publication_date,
                    record.source.collection_date,
                    record.source.language,
                    record.source.rights_basis,
                    record.source.confidence_score,
                    record.source.human_review_status,
                    record.source.reviewer_notes,
                ),
            )
            conn.commit()

    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Calculates exact live dataset metrics without inventing numbers."""
        stats = {
            "total_records": 0,
            "by_source": {},
            "by_category": {},
            "by_make": {},
            "by_language": {},
            "by_review_status": {},
            "ml_ready_count": 0,
        }

        with self._get_connection() as conn:
            # Total records
            row = conn.execute("SELECT COUNT(*) AS total FROM diagnostic_records").fetchone()
            stats["total_records"] = row["total"] if row else 0

            # By Source
            for r in conn.execute("SELECT source_id, COUNT(*) AS cnt FROM diagnostic_records GROUP BY source_id"):
                stats["by_source"][r["source_id"]] = r["cnt"]

            # By Fault Category
            for r in conn.execute("SELECT fault_category_id, COUNT(*) AS cnt FROM diagnostic_records GROUP BY fault_category_id"):
                cat_key = r["fault_category_id"] or "Uncategorized"
                stats["by_category"][cat_key] = r["cnt"]

            # By Language
            for r in conn.execute("SELECT language, COUNT(*) AS cnt FROM diagnostic_records GROUP BY language"):
                stats["by_language"][r["language"]] = r["cnt"]

            # By Review Status
            for r in conn.execute("SELECT human_review_status, COUNT(*) AS cnt FROM diagnostic_records GROUP BY human_review_status"):
                stats["by_review_status"][r["human_review_status"]] = r["cnt"]

            # By Make
            for r in conn.execute("""
                SELECT vf.make, COUNT(dr.record_id) as cnt
                FROM diagnostic_records dr
                JOIN vehicle_fleet vf ON dr.vehicle_id = vf.vehicle_id
                GROUP BY vf.make
            """):
                stats["by_make"][r["make"]] = r["cnt"]

            stats["ml_ready_count"] = stats["by_review_status"].get("ml_ready", 0)

        return stats
