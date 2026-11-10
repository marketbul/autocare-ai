"""Database Storage Manager for AI Auto Pakistan.

Handles relational database initialization, records ingestion, foreign keys,
review workflow, and multi-dimensional metrics querying.
Supports SQLite (local prototyping) and PostgreSQL.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..registry import create_default_source_registry
from ..schema import AutomotiveRecord
from ..taxonomy import AUTOMOTIVE_FAULT_CATEGORIES, PAKISTANI_FLEET

PLATFORM_TO_SOURCE_ID = {
    "youtube": "youtube_official_api",
    "youtube_official_api": "youtube_official_api",
    "facebook": "facebook_research_import",
    "facebook_research_import": "facebook_research_import",
    "pakwheels": "pakwheels_research_import",
    "pakwheels_research_import": "pakwheels_research_import",
    "mechanic_interview": "mechanic_interviews",
    "mechanic_interviews": "mechanic_interviews",
    "owner_submission": "owner_submissions",
    "owner_submissions": "owner_submissions",
    "manuals": "manuals_and_bulletins",
    "manuals_and_bulletins": "manuals_and_bulletins",
    "starter_symptom_corpus": "starter_symptom_corpus",
    "pakistan_price_reference": "pakistan_price_reference",
    "automotive_blog": "automotive_blog_research",
    "automotive_blog_research": "automotive_blog_research",
}


class StorageManager:
    """Relational database gateway for automotive datasets."""

    def __init__(self, db_path: Optional[Path | str] = None) -> None:
        config = get_config()
        self.config = config
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

            # Seed / Sync Registered Sources
            registry = create_default_source_registry()
            for s in registry.list_all():
                conn.execute(
                    """INSERT OR REPLACE INTO data_sources
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
                    """INSERT OR REPLACE INTO fault_categories
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

    def seed_vehicle_fleet(self) -> int:
        """Seeds vehicle_fleet from vehicles.csv and PAKISTANI_FLEET."""
        inserted = 0
        with self._get_connection() as conn:
            # 1. Seed from vehicles.csv (Corolla, Civic, Swift variants)
            veh_csv = self.config.data_dir / "vehicles.csv"
            if veh_csv.exists():
                with open(veh_csv, mode="r", encoding="utf-8-sig") as f:
                    for row in csv.DictReader(f):
                        vid = (row.get("vehicle_id") or "").strip()
                        if not vid or vid.startswith("#"):
                            continue
                        year = None
                        try:
                            year = int(row["year"]) if row.get("year") else None
                        except ValueError:
                            pass
                        conn.execute(
                            """INSERT OR IGNORE INTO vehicle_fleet
                            (vehicle_id, make, model, variant, manufacturing_year, engine_type, transmission, fuel_type, market_country)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pakistan')""",
                            (
                                vid,
                                row.get("manufacturer", "").strip(),
                                row.get("model", "").strip(),
                                row.get("variant", "").strip() or None,
                                year,
                                row.get("engine", "").strip() or None,
                                row.get("transmission", "").strip() or None,
                                row.get("fuel_type", "").strip() or None,
                            ),
                        )
                        inserted += 1

            # 2. Seed all 15 models in PAKISTANI_FLEET (Alto, Cultus, Mehran, Wagon R, Yaris, etc.)
            for slug, fv in PAKISTANI_FLEET.items():
                vid = f"{slug}-pk"
                conn.execute(
                    """INSERT OR IGNORE INTO vehicle_fleet
                    (vehicle_id, make, model, variant, manufacturing_year, engine_cc, engine_type, fuel_type, transmission, market_country)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pakistan')""",
                    (
                        vid,
                        fv.make,
                        fv.model,
                        ", ".join(fv.common_variants[:3]),
                        fv.years_range[1],
                        fv.engine_cc_range[0] if fv.engine_cc_range else None,
                        fv.market_segment,
                        ", ".join(fv.fuel_types),
                        ", ".join(fv.transmissions),
                    ),
                )
                inserted += 1
            conn.commit()
        return inserted

    def _insert_one(self, conn: sqlite3.Connection, record: AutomotiveRecord) -> None:
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

        source_key = PLATFORM_TO_SOURCE_ID.get(record.source.source_platform, record.source.source_platform)
        cat_id = record.problem.fault_category if record.problem.fault_category in AUTOMOTIVE_FAULT_CATEGORIES else None

        def _lookup_asset(rel_ref: Optional[str]) -> Optional[str]:
            if not rel_ref:
                return None
            r = conn.execute("SELECT asset_id FROM media_assets WHERE relative_reference = ?", (rel_ref,)).fetchone()
            return r["asset_id"] if r else None

        audio_aid = _lookup_asset(record.audio.audio_file_reference if record.audio else None)
        image_aid = _lookup_asset(record.media.image_reference if record.media else None)
        video_aid = _lookup_asset(record.media.video_reference if record.media else None)

        conn.execute(
            """INSERT OR REPLACE INTO diagnostic_records
            (record_id, vehicle_id, fault_category_id, source_id, problem_title, problem_description,
             symptoms_json, suspected_causes_json, confirmed_causes_json, severity, diagnosis_stage,
             audio_asset_id, image_asset_id, video_asset_id,
             sound_category, sound_description, detected_component, dashboard_warning_light, smoke_color,
             recommended_solution, repair_steps_json, required_parts_json, repair_success, verification_status,
             estimated_cost_pkr, parts_cost_pkr, labor_cost_pkr, city, price_date, price_source,
             source_url, publication_date, collection_date, language, rights_basis, confidence_score,
             human_review_status, reviewer_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                audio_aid,
                image_aid,
                video_aid,
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

    def insert_record(self, record: AutomotiveRecord) -> None:
        """Upserts a single AutomotiveRecord into relational storage."""
        with self._get_connection() as conn:
            self._insert_one(conn, record)
            conn.commit()

    def insert_records(self, records: List[AutomotiveRecord]) -> int:
        """Batch upserts multiple AutomotiveRecords in one transaction."""
        if not records:
            return 0
        with self._get_connection() as conn:
            for rec in records:
                self._insert_one(conn, rec)
            conn.commit()
        return len(records)

    def register_media_asset(self, asset: Dict[str, Any], asset_type: str) -> str:
        """Saves a media asset reference into media_assets table."""
        asset_id = f"media_{asset['sha256'][:16]}"
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO media_assets
                (asset_id, asset_type, relative_reference, sha256_hash, size_bytes, rights_basis, attribution, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    asset_id,
                    asset_type,
                    asset["relative_reference"],
                    asset["sha256"],
                    asset["size_bytes"],
                    asset["rights_basis"],
                    asset.get("attribution", ""),
                    dt.datetime.now(dt.timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        return asset_id

    def query_records(
        self,
        make: Optional[str] = None,
        model: Optional[str] = None,
        source_id: Optional[str] = None,
        category_id: Optional[str] = None,
        language: Optional[str] = None,
        status: Optional[str] = None,
        search_text: Optional[str] = None,
        include_examples: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Filters and paginates diagnostic_records joined with vehicle & category."""
        clauses: List[str] = []
        params: List[Any] = []

        if make:
            clauses.append("lower(vf.make) = lower(?)")
            params.append(make.strip())
        if model:
            clauses.append("lower(vf.model) LIKE lower(?)")
            params.append(f"%{model.strip()}%")
        if source_id:
            mapped = PLATFORM_TO_SOURCE_ID.get(source_id, source_id)
            clauses.append("dr.source_id = ?")
            params.append(mapped)
        if category_id:
            if category_id == "Uncategorized":
                clauses.append("dr.fault_category_id IS NULL")
            else:
                clauses.append("dr.fault_category_id = ?")
                params.append(category_id)
        if language:
            clauses.append("dr.language = ?")
            params.append(language.strip())
        if status:
            clauses.append("dr.human_review_status = ?")
            params.append(status.strip())
        if not include_examples:
            clauses.append("dr.rights_basis != 'example_template'")
        if search_text:
            clauses.append(
                "(lower(dr.problem_title) LIKE lower(?) OR lower(dr.problem_description) LIKE lower(?) OR lower(dr.symptoms_json) LIKE lower(?))"
            )
            q = f"%{search_text.strip()}%"
            params.extend([q, q, q])

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        base_from = f"""
            FROM diagnostic_records dr
            LEFT JOIN vehicle_fleet vf ON dr.vehicle_id = vf.vehicle_id
            LEFT JOIN fault_categories fc ON dr.fault_category_id = fc.category_id
            LEFT JOIN media_assets ma_img ON dr.image_asset_id = ma_img.asset_id
            LEFT JOIN media_assets ma_aud ON dr.audio_asset_id = ma_aud.asset_id
            {where_sql}
        """

        with self._get_connection() as conn:
            total_row = conn.execute(f"SELECT COUNT(*) AS cnt {base_from}", params).fetchone()
            total = total_row["cnt"] if total_row else 0

            rows = conn.execute(
                f"""
                SELECT dr.*, vf.make, vf.model, vf.variant, vf.manufacturing_year,
                       fc.name AS category_name, fc.name_roman_ur AS category_roman_ur,
                       ma_img.relative_reference AS image_reference,
                       ma_aud.relative_reference AS audio_reference
                {base_from}
                ORDER BY dr.collection_date DESC, dr.record_id ASC
                LIMIT ? OFFSET ?
                """,
                [*params, limit, offset],
            ).fetchall()

        results: List[Dict[str, Any]] = []
        for r in rows:
            item = dict(r)
            for jf, target in [
                ("symptoms_json", "symptoms"),
                ("suspected_causes_json", "suspected_causes"),
                ("confirmed_causes_json", "confirmed_causes"),
                ("repair_steps_json", "repair_steps"),
                ("required_parts_json", "required_parts"),
            ]:
                try:
                    item[target] = json.loads(item.get(jf) or "[]")
                except json.JSONDecodeError:
                    item[target] = []
            item["is_example"] = item.get("rights_basis") == "example_template"
            results.append(item)

        return results, total

    def update_review_status(
        self, record_id: str, new_status: str, reviewer_notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Updates human review status (pending, reviewed, approved, ml_ready, rejected)."""
        allowed = {"pending", "needs_review", "reviewed", "approved", "ml_ready", "rejected"}
        clean_status = new_status.strip().lower()
        if clean_status not in allowed:
            raise ValueError(f"Invalid review status '{new_status}'. Allowed: {sorted(allowed)}")

        with self._get_connection() as conn:
            cur = conn.execute(
                "UPDATE diagnostic_records SET human_review_status = ?, reviewer_notes = COALESCE(?, reviewer_notes) WHERE record_id = ?",
                (clean_status, reviewer_notes, record_id),
            )
            conn.commit()
            if cur.rowcount == 0:
                return None

        self.logger.log(
            AuditAction.RECORD_REVIEWED,
            source_id="manual_review_ui",
            record_id=record_id,
            status="SUCCESS",
            details={"new_status": clean_status, "notes": reviewer_notes},
        )
        rows, _ = self.query_records(limit=1)
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM diagnostic_records WHERE record_id = ?", (record_id,)).fetchone()
            return dict(row) if row else None

    def get_fleet_vehicles(self, make: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if make:
                rows = conn.execute(
                    "SELECT * FROM vehicle_fleet WHERE lower(make) = lower(?) ORDER BY make, model, manufacturing_year DESC",
                    (make.strip(),),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM vehicle_fleet ORDER BY make, model, manufacturing_year DESC"
                ).fetchall()
        return [dict(r) for r in rows]

    def get_fault_categories_with_counts(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT fc.*, COUNT(dr.record_id) AS record_count
                FROM fault_categories fc
                LEFT JOIN diagnostic_records dr ON fc.category_id = dr.fault_category_id
                    AND dr.rights_basis != 'example_template'
                GROUP BY fc.category_id
                ORDER BY fc.category_id
                """
            ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["subcomponents"] = json.loads(d.pop("subcomponents_json") or "[]")
            d["multilingual_symptom_keywords"] = json.loads(d.pop("symptom_keywords_json") or "[]")
            d["typical_causes"] = json.loads(d.pop("typical_causes_json") or "[]")
            out.append(d)
        return out

    def get_cost_records(self, make: Optional[str] = None, model: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses = ["dr.estimated_cost_pkr IS NOT NULL"]
        params: List[Any] = []
        if make:
            clauses.append("lower(vf.make) = lower(?)")
            params.append(make.strip())
        if model:
            clauses.append("lower(vf.model) LIKE lower(?)")
            params.append(f"%{model.strip()}%")
        where_sql = "WHERE " + " AND ".join(clauses)
        with self._get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT dr.record_id, vf.make, vf.model, vf.variant, dr.problem_title,
                       dr.fault_category_id, dr.estimated_cost_pkr, dr.parts_cost_pkr,
                       dr.labor_cost_pkr, dr.city, dr.price_date, dr.price_source,
                       dr.rights_basis, dr.required_parts_json
                FROM diagnostic_records dr
                LEFT JOIN vehicle_fleet vf ON dr.vehicle_id = vf.vehicle_id
                {where_sql}
                ORDER BY dr.estimated_cost_pkr DESC
                """,
                params,
            ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["required_parts"] = json.loads(d.pop("required_parts_json") or "[]")
            d["is_example"] = d.get("rights_basis") == "example_template"
            out.append(d)
        return out

    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Calculates exact live dataset metrics without inventing numbers."""
        stats: Dict[str, Any] = {
            "total_records": 0,
            "real_records_count": 0,
            "example_records_count": 0,
            "by_source": {},
            "real_by_source": {},
            "by_category": {},
            "by_make": {},
            "by_model": {},
            "by_language": {},
            "by_review_status": {},
            "ml_ready_count": 0,
            "reviewed_count": 0,
            "total_vehicles_in_fleet": 0,
            "distinct_vehicle_models_covered": 0,
            "fault_categories_covered": 0,
            "media_counts": {"audio": 0, "images": 0, "videos": 0, "video_metadata_records": 0, "transcribed": 0},
        }

        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM diagnostic_records").fetchone()
            stats["total_records"] = row["total"] if row else 0

            ex_row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM diagnostic_records WHERE rights_basis = 'example_template'"
            ).fetchone()
            stats["example_records_count"] = ex_row["cnt"] if ex_row else 0
            stats["real_records_count"] = stats["total_records"] - stats["example_records_count"]

            for r in conn.execute("SELECT source_id, COUNT(*) AS cnt FROM diagnostic_records GROUP BY source_id"):
                stats["by_source"][r["source_id"]] = r["cnt"]

            for r in conn.execute(
                "SELECT source_id, COUNT(*) AS cnt FROM diagnostic_records WHERE rights_basis != 'example_template' GROUP BY source_id"
            ):
                stats["real_by_source"][r["source_id"]] = r["cnt"]

            for r in conn.execute(
                "SELECT fault_category_id, COUNT(*) AS cnt FROM diagnostic_records WHERE rights_basis != 'example_template' GROUP BY fault_category_id"
            ):
                cat_key = r["fault_category_id"] or "Uncategorized"
                stats["by_category"][cat_key] = r["cnt"]

            stats["fault_categories_covered"] = sum(1 for k in stats["by_category"] if k != "Uncategorized")

            for r in conn.execute(
                "SELECT language, COUNT(*) AS cnt FROM diagnostic_records WHERE rights_basis != 'example_template' GROUP BY language"
            ):
                stats["by_language"][r["language"]] = r["cnt"]

            for r in conn.execute("SELECT human_review_status, COUNT(*) AS cnt FROM diagnostic_records GROUP BY human_review_status"):
                stats["by_review_status"][r["human_review_status"]] = r["cnt"]

            for r in conn.execute("""
                SELECT vf.make, COUNT(dr.record_id) AS cnt
                FROM diagnostic_records dr
                JOIN vehicle_fleet vf ON dr.vehicle_id = vf.vehicle_id
                WHERE dr.rights_basis != 'example_template'
                GROUP BY vf.make
            """):
                stats["by_make"][r["make"]] = r["cnt"]

            for r in conn.execute("""
                SELECT vf.make || ' ' || vf.model AS vehicle_name, COUNT(dr.record_id) AS cnt
                FROM diagnostic_records dr
                JOIN vehicle_fleet vf ON dr.vehicle_id = vf.vehicle_id
                WHERE dr.rights_basis != 'example_template'
                GROUP BY vf.make, vf.model
            """):
                stats["by_model"][r["vehicle_name"]] = r["cnt"]

            vf_row = conn.execute("SELECT COUNT(*) AS cnt FROM vehicle_fleet").fetchone()
            stats["total_vehicles_in_fleet"] = vf_row["cnt"] if vf_row else 0

            dm_row = conn.execute("SELECT COUNT(DISTINCT make || '|' || model) AS cnt FROM vehicle_fleet").fetchone()
            stats["distinct_vehicle_models_covered"] = dm_row["cnt"] if dm_row else 0

            # Media counts (honest zero if none uploaded/collected)
            for r in conn.execute("SELECT asset_type, COUNT(*) AS cnt FROM media_assets GROUP BY asset_type"):
                if r["asset_type"] in stats["media_counts"]:
                    stats["media_counts"][r["asset_type"]] = r["cnt"]

            vid_meta = conn.execute(
                "SELECT COUNT(*) AS cnt FROM diagnostic_records WHERE source_id = 'youtube_official_api' AND rights_basis != 'example_template'"
            ).fetchone()
            stats["media_counts"]["video_metadata_records"] = vid_meta["cnt"] if vid_meta else 0

            tr_row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM diagnostic_records WHERE audio_asset_id IS NOT NULL"
            ).fetchone()
            stats["media_counts"]["transcribed"] = tr_row["cnt"] if tr_row else 0

            stats["ml_ready_count"] = stats["by_review_status"].get("ml_ready", 0)
            stats["reviewed_count"] = (
                stats["by_review_status"].get("reviewed", 0)
                + stats["by_review_status"].get("approved", 0)
                + stats["by_review_status"].get("ml_ready", 0)
            )

        return stats
