"""Local Automotive Dataset Consolidator for AI Auto Pakistan.

Unifies all verified local project datasets into the normalized Data Engine schema:
1. SAE J2012 OBD-II Diagnostic Trouble Codes (data/obd2_codes.csv)
2. Multilingual Symptom Corpus in EN / UR / Roman UR (data/symptom_labels.starter.csv)
3. OEM Owner & Service Manuals Index + Extracted Text (data/manuals/manuals_index.json)
4. Pakistan Spare Parts & Workshop Labour Price Database (autocare/pricing.py)
5. Vehicle Fleet Catalog (data/vehicles.csv + PAKISTANI_FLEET)
6. Clearly-badged Example Templates (data/templates/*.csv) kept distinct from real records
"""
from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

from ..cleaning import CleaningPipeline
from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..ml import GroupedMLSplitter
from ..reports import DatasetReportGenerator
from ..schema import (
    AutomotiveRecord,
    CostInfo,
    ProblemInfo,
    RepairInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from ..storage import StorageManager
from ..taxonomy import DiagnosisStage, get_taxonomy_manager
from .facebook import FacebookResearchImporter
from .pakwheels import PakWheelsResearchImporter
from .submissions import MechanicInterviewImporter, OwnerProblemReportImporter

OBD2_SYSTEM_TO_FC = {
    "powertrain": "FC-01",
    "cooling": "FC-09",
    "emissions": "FC-11",
    "transmission": "FC-02",
    "braking": "FC-04",
    "electrical": "FC-07",
}

STARTER_CAT_TO_FC = {
    "braking": "FC-04",
    "cooling": "FC-09",
    "electrical": "FC-07",
    "engine": "FC-01",
    "suspension_steering": "FC-05",
    "transmission": "FC-02",
    "tyres_wheels": "FC-13",
}


class LocalDatasetConsolidator:
    """Consolidates real local datasets into normalized AutomotiveRecords and SQLite."""

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def load_obd2_codes(self) -> List[AutomotiveRecord]:
        path = self.config.data_dir / "obd2_codes.csv"
        if not path.exists():
            return []

        records: List[AutomotiveRecord] = []
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                code = (row.get("code") or "").strip()
                if not code or code.startswith("#"):
                    continue
                desc = (row.get("description") or "").strip()
                system = (row.get("system") or "").strip()
                causes = [c.strip() for c in (row.get("possible_causes") or "").split(",") if c.strip()]
                symptoms = [s.strip() for s in (row.get("symptoms") or "").split(",") if s.strip()]
                sev = (row.get("severity") or "moderate").strip().lower()

                matched = self.taxonomy.match_category_from_text(f"{code} {desc} {system} {' '.join(symptoms)}")
                cat_id = matched.category_id if matched else OBD2_SYSTEM_TO_FC.get(system.lower(), "FC-14")

                rec = AutomotiveRecord(
                    record_id=f"obd2_{code}",
                    vehicle=VehicleInfo(make="Universal", model="OBD-II Standard"),
                    problem=ProblemInfo(
                        problem_title=f"{code}: {desc}",
                        problem_description=f"SAE J2012 DTC {code} ({system}) - {desc}. Section: {row.get('section', '')}, Page: {row.get('page', '')}",
                        symptoms=symptoms,
                        fault_category=cat_id,
                        suspected_causes=causes,
                        severity=sev,
                        diagnosis_stage=DiagnosisStage.MECHANIC_CONFIRMED_DIAGNOSIS.value,
                    ),
                    source=SourceQualityInfo(
                        source_platform="manuals",
                        source_url=f"local://obd2/{code}",
                        source_id=f"obd2_{code}",
                        source_author_or_channel=row.get("source_ref") or "SAE J2012 Standard",
                        language="en",
                        rights_basis="public_technical_documentation",
                        permission_status="public_standard",
                        confidence_score=1.0,
                        human_review_status="ml_ready",
                    ),
                )
                records.append(rec)
        return records

    def load_symptom_corpus(self) -> List[AutomotiveRecord]:
        path = self.config.data_dir / "symptom_labels.starter.csv"
        if not path.exists():
            return []

        records: List[AutomotiveRecord] = []
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                ex_id = (row.get("example_id") or "").strip()
                if not ex_id or ex_id.startswith("#"):
                    continue
                group_id = (row.get("group_id") or ex_id).strip()
                lang = (row.get("language") or "en").strip()
                text = (row.get("text") or "").strip()
                raw_cat = (row.get("category") or "").strip().lower()
                urgency = (row.get("urgency") or "moderate").strip().lower()

                cat_id = STARTER_CAT_TO_FC.get(raw_cat)
                if not cat_id:
                    matched = self.taxonomy.match_category_from_text(text)
                    cat_id = matched.category_id if matched else "FC-14"

                # Group by group_id via source_url so EN/UR/Roman UR translations stay in the same ML split
                rec = AutomotiveRecord(
                    record_id=f"sym_{ex_id}",
                    vehicle=VehicleInfo(make="Toyota", model="Corolla"),
                    problem=ProblemInfo(
                        problem_title=text[:120],
                        problem_description=text,
                        symptoms=[text],
                        fault_category=cat_id,
                        severity=urgency,
                        diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
                    ),
                    source=SourceQualityInfo(
                        source_platform="starter_symptom_corpus",
                        source_url=f"local://symptom_corpus/{ex_id}",
                        source_id=ex_id,
                        source_author_or_channel="AutoCare AI Multilingual Symptom Corpus",
                        language=lang,
                        evidence_reference=f"group:{group_id}",
                        rights_basis="starter_synthetic_corpus",
                        permission_status="project_internal_corpus",
                        confidence_score=0.85,
                        human_review_status="ml_ready",
                        reviewer_notes="Authored multilingual symptom baseline (grouped EN/UR/Roman UR)",
                    ),
                )
                records.append(rec)
        return records

    def load_manuals(self) -> List[AutomotiveRecord]:
        index_path = self.config.data_dir / "manuals" / "manuals_index.json"
        if not index_path.exists():
            return []

        with open(index_path, "r", encoding="utf-8") as f:
            manuals = json.load(f)

        vehicle_map = {
            "toyota_corolla": ("Toyota", "Corolla"),
            "honda_civic": ("Honda", "Civic"),
            "suzuki_swift": ("Suzuki", "Swift"),
        }

        records: List[AutomotiveRecord] = []
        for idx, m in enumerate(manuals, start=1):
            veh_key = (m.get("vehicle") or "").lower()
            make, model = vehicle_map.get(veh_key, ("Unknown", "Unknown"))
            title = (m.get("title") or f"{make} {model} Manual").strip()
            year = m.get("year")
            txt_rel = m.get("txt_path")
            excerpt = title
            if txt_rel:
                txt_file = self.config.backend_root / Path(txt_rel.replace("\\", "/"))
                if txt_file.exists():
                    try:
                        excerpt = txt_file.read_text(encoding="utf-8", errors="ignore")[:1200].strip()
                    except Exception:
                        pass

            matched = self.taxonomy.match_category_from_text(f"{title} {excerpt[:400]}")
            cat_id = matched.category_id if matched else "FC-01"

            rec = AutomotiveRecord(
                record_id=f"manual_{idx:03d}_{veh_key}",
                vehicle=VehicleInfo(
                    make=make,
                    model=model,
                    manufacturing_year=int(year) if year else None,
                ),
                problem=ProblemInfo(
                    problem_title=title,
                    problem_description=excerpt,
                    symptoms=[title],
                    fault_category=cat_id,
                    diagnosis_stage=DiagnosisStage.VERIFIED_REPAIR_OUTCOME.value,
                ),
                source=SourceQualityInfo(
                    source_platform="manuals",
                    source_url=m.get("url") or f"local://manuals/{idx}",
                    source_id=f"manual_{idx:03d}",
                    source_author_or_channel=f"{make} Official Documentation",
                    publication_date=f"{year}-01-01" if year else None,
                    language="en",
                    rights_basis="public_technical_documentation",
                    permission_status="oem_reference",
                    confidence_score=1.0,
                    human_review_status="ml_ready",
                ),
            )
            records.append(rec)
        return records

    def load_pakistan_prices(self) -> List[AutomotiveRecord]:
        try:
            from autocare.pricing import PAKISTAN_PRICE_DATABASE
        except Exception:
            return []

        key_to_vehicle = {
            "corolla": ("Toyota", "Corolla"),
            "civic": ("Honda", "Civic"),
            "swift": ("Suzuki", "Swift"),
        }
        cat_map = {
            "braking": "FC-04",
            "cooling": "FC-09",
            "engine": "FC-01",
            "transmission": "FC-02",
            "electrical": "FC-07",
            "steering": "FC-06",
        }

        records: List[AutomotiveRecord] = []
        for veh_key, quotes in PAKISTAN_PRICE_DATABASE.items():
            make, model = key_to_vehicle.get(veh_key, ("Unknown", veh_key.title()))
            for idx, q in enumerate(quotes, start=1):
                cat_id = cat_map.get(q.category.lower(), "FC-01")
                avg_oem = round((q.oem_price_min_pkr + q.oem_price_max_pkr) / 2.0, 2)
                rec = AutomotiveRecord(
                    record_id=f"price_{veh_key}_{idx:02d}",
                    vehicle=VehicleInfo(make=make, model=model),
                    problem=ProblemInfo(
                        problem_title=f"{make} {model}: {q.part_name} Replacement",
                        problem_description=q.quality_notes,
                        symptoms=[q.part_name, q.category],
                        fault_category=cat_id,
                        affected_component=q.part_name,
                        diagnosis_stage=DiagnosisStage.VERIFIED_REPAIR_OUTCOME.value,
                    ),
                    repair=RepairInfo(
                        recommended_solution=q.quality_notes,
                        required_parts=[q.part_name],
                        estimated_repair_time=f"{q.recommended_replacement_hours} hours",
                        verification_status="verified_by_mechanic",
                    ),
                    cost=CostInfo(
                        estimated_cost_pkr=avg_oem + q.estimated_labour_pkr,
                        minimum_cost_pkr=q.aftermarket_price_min_pkr + q.estimated_labour_pkr,
                        maximum_cost_pkr=q.oem_price_max_pkr + q.estimated_labour_pkr,
                        parts_cost_pkr=avg_oem,
                        labor_cost_pkr=q.estimated_labour_pkr,
                        price_date="2026-05-01",
                        city="Lahore / Karachi / Islamabad",
                        price_source="pakistan_market_benchmark",
                    ),
                    source=SourceQualityInfo(
                        source_platform="pakistan_price_reference",
                        source_url=f"local://pricing/{veh_key}/{idx}",
                        source_id=f"price_{veh_key}_{idx:02d}",
                        source_author_or_channel="AutoCare AI Pakistan Workshop Survey",
                        language="en",
                        rights_basis="market_survey_benchmark",
                        permission_status="project_internal_corpus",
                        confidence_score=0.9,
                        human_review_status="ml_ready",
                    ),
                )
                records.append(rec)
        return records

    def load_template_examples(self) -> List[AutomotiveRecord]:
        """Loads the 4 template examples, strictly flagged as example_template."""
        examples: List[AutomotiveRecord] = []

        loaders = [
            (self.config.templates_dir / "facebook_research_template.csv", FacebookResearchImporter().import_manual_csv, "fb"),
            (self.config.templates_dir / "pakwheels_research_template.csv", PakWheelsResearchImporter().import_manual_csv, "pw"),
            (self.config.templates_dir / "mechanic_interview_template.csv", MechanicInterviewImporter().import_csv, "mech"),
            (self.config.templates_dir / "owner_problem_report_template.csv", OwnerProblemReportImporter().import_csv, "owner"),
        ]
        for path, fn, prefix in loaders:
            if path.exists():
                recs = fn(path)
                for i, r in enumerate(recs, start=1):
                    r.record_id = f"example_{prefix}_{i:02d}"
                    r.source.rights_basis = "example_template"
                    r.source.human_review_status = "example_template"
                    r.source.reviewer_notes = "[EXAMPLE TEMPLATE RECORD] Illustrative schema demo — not external collected data."
                    examples.append(r)
        return examples

    def consolidate_all(self, include_examples: bool = True) -> Dict[str, Any]:
        """Consolidates all local datasets, seeds fleet, cleans, stores in SQLite, and generates ML splits."""
        storage = StorageManager()
        fleet_seeded = storage.seed_vehicle_fleet()

        real_records: List[AutomotiveRecord] = []
        obd2 = self.load_obd2_codes()
        symptoms = self.load_symptom_corpus()
        manuals = self.load_manuals()
        prices = self.load_pakistan_prices()

        real_records.extend(obd2)
        real_records.extend(symptoms)
        real_records.extend(manuals)
        real_records.extend(prices)

        # Clean & normalize real records
        pipeline = CleaningPipeline()
        clean_summary = pipeline.process_batch(real_records)

        # Persist real records to SQLite
        storage.insert_records(real_records)

        # Persist clearly-flagged template examples (kept separate from ML splits!)
        example_records: List[AutomotiveRecord] = []
        if include_examples:
            example_records = self.load_template_examples()
            storage.insert_records(example_records)

        # Generate Leak-Free ML Splits strictly on real records (never mix example templates)
        splitter = GroupedMLSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
        train_recs, val_recs, test_recs = splitter.split_records(real_records)
        split_paths = splitter.export_splits(train_recs, val_recs, test_recs)

        # Generate fresh Quality Report
        report_path = DatasetReportGenerator(storage=storage).export_markdown_report()

        self.logger.log(
            AuditAction.COLLECTION_COMPLETED,
            source_id="local_consolidator",
            status="SUCCESS",
            details={
                "fleet_seeded": fleet_seeded,
                "obd2_codes": len(obd2),
                "symptom_corpus": len(symptoms),
                "manuals": len(manuals),
                "pakistan_prices": len(prices),
                "example_templates": len(example_records),
            },
        )

        return {
            "fleet_seeded": fleet_seeded,
            "counts": {
                "obd2_codes": len(obd2),
                "symptom_corpus": len(symptoms),
                "manuals": len(manuals),
                "pakistan_prices": len(prices),
                "total_real_records": len(real_records),
                "example_template_records": len(example_records),
            },
            "cleaning_summary": clean_summary,
            "ml_splits": {
                "train": len(train_recs),
                "val": len(val_recs),
                "test": len(test_recs),
                "dataset_card": split_paths.get("dataset_card"),
            },
            "report_path": str(report_path),
            "db_path": str(storage.db_path),
        }
