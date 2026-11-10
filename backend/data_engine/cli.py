"""Command-Line Interface for AI Auto Pakistan Data Engineering Platform.

Usage:
    python -m data_engine.cli status             # Check system directories, keys, and status
    python -m data_engine.cli sources            # List registered data sources and legal terms
    python -m data_engine.cli inspect            # Detailed audit of existing codebase assets
    python -m data_engine.cli consolidate        # Consolidate all local data + build ML splits
    python -m data_engine.cli import-templates   # Ingest research templates into DB & pipeline
    python -m data_engine.cli report             # Generate comprehensive quality audit report
    python -m data_engine.cli split              # Create leak-free train/val/test ML datasets
    python -m data_engine.cli serve              # Launch localhost dashboard on 127.0.0.1:8090
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cleaning import CleaningPipeline
from .config import get_config
from .logger import get_audit_logger
from .ml import GroupedMLSplitter
from .registry import create_default_source_registry
from .reports import DatasetReportGenerator
from .sources import (
    FacebookResearchImporter,
    LocalDatasetConsolidator,
    MechanicInterviewImporter,
    OwnerProblemReportImporter,
    PakWheelsResearchImporter,
)
from .storage import StorageManager


def cmd_status(args: argparse.Namespace) -> None:
    config = get_config()
    logger = get_audit_logger()
    summary = logger.get_summary()

    print("=" * 70)
    print("AI AUTO PAKISTAN -- DATASET ENGINEERING SYSTEM STATUS")
    print("=" * 70)
    print(f"Backend Root:        {config.backend_root}")
    print(f"Data Directory:      {config.data_dir}")
    print(f"Database URL:        {config.database_url}")
    print(f"YouTube API Key:     {'[CONFIGURED]' if config.youtube_api_key else '[NOT SET - Set YOUTUBE_API_KEY in .env]'}")
    print(f"Facebook Token:      {'[CONFIGURED]' if config.facebook_access_token else '[NOT SET - Set FACEBOOK_ACCESS_TOKEN in .env]'}")
    print(f"Metadata-Only Mode:  {config.metadata_only_default}")
    print(f"Consent Required:    {config.require_consent_for_interviews}")
    print(f"Anonymize PII:       {config.anonymize_personal_identifiers}")
    print("-" * 70)

    raw_counts = {}
    for sub in ["youtube", "facebook", "pakwheels", "mechanic_notes", "owner_reports", "manuals"]:
        p = config.raw_dir / sub
        raw_counts[sub] = len(list(p.glob("*"))) if p.exists() else 0

    print("DATA DIRECTORY COUNTS:")
    for sub, count in raw_counts.items():
        print(f"  * Raw {sub.capitalize():<18}: {count} file(s)")

    processed_count = len(list(config.processed_dir.glob("*"))) if config.processed_dir.exists() else 0
    ml_count = len(list(config.ml_ready_dir.glob("*"))) if config.ml_ready_dir.exists() else 0
    print(f"  * Processed Records      : {processed_count} file(s)")
    print(f"  * ML-Ready Splits        : {ml_count} file(s)")
    print("-" * 70)

    print("AUDIT LOG ACTIVITY:")
    print(f"  * Total Events Logged    : {summary['total_audit_events']}")

    if summary["actions"]:
        for act, cnt in summary["actions"].items():
            print(f"    - {act:<24}: {cnt}")
    print("=" * 70)


def cmd_sources(args: argparse.Namespace) -> None:
    registry = create_default_source_registry()
    sources = registry.list_all()

    print("=" * 80)
    print("AI AUTO PAKISTAN — REGISTERED AUTOMOTIVE DATA SOURCES")
    print("=" * 80)
    for s in sources:
        print(f"Source ID:          {s.source_id}")
        print(f"Name:               {s.name}")
        print(f"Source Type:        {s.source_type.value}")
        print(f"Rights / Legal:     {s.rights_basis.value}")
        print(f"Automated:          {'Yes' if s.is_automated else 'No (Manual / Curation Import)'}")
        print(f"Requires API Key:   {'Yes' if s.requires_api_key else 'No'}")
        print(f"Requires Consent:   {'Yes' if s.requires_permission else 'No'}")
        print(f"Rate Limiting:      {s.rate_limit_policy}")
        print(f"Description:        {s.description}")
        if s.limitations:
            print("Limitations & Rules:")
            for lim in s.limitations:
                print(f"  * {lim}")
        print("-" * 80)


def cmd_inspect(args: argparse.Namespace) -> None:
    config = get_config()
    print("=" * 80)
    print("AI AUTO PAKISTAN — EXISTING PROJECT INVENTORY & AUDIT")
    print("=" * 80)

    autocare_dir = config.backend_root / "autocare"
    if autocare_dir.exists():
        py_files = sorted(autocare_dir.glob("*.py"))
        print(f"\n[Core Application Modules] in {autocare_dir.name}/ ({len(py_files)} files):")
        for f in py_files:
            print(f"  - {f.name:<25} ({f.stat().st_size:,} bytes)")

    ingest_dir = config.backend_root / "ingest"
    if ingest_dir.exists():
        py_files = sorted(ingest_dir.glob("*.py"))
        print(f"\n[Existing Ingestion Scripts] in {ingest_dir.name}/ ({len(py_files)} files):")
        for f in py_files:
            print(f"  - {f.name:<25} ({f.stat().st_size:,} bytes)")

    data_dir = config.backend_root / "data"
    if data_dir.exists():
        csv_files = sorted(data_dir.glob("*.csv"))
        print(f"\n[Existing Dataset Files] in {data_dir.name}/ ({len(csv_files)} files):")
        for f in csv_files:
            print(f"  - {f.name:<30} ({f.stat().st_size:,} bytes)")

    sql_dir = config.backend_root / "sql"
    if sql_dir.exists():
        sql_files = sorted(sql_dir.glob("*.sql"))
        print(f"\n[Database Schemas] in {sql_dir.name}/ ({len(sql_files)} files):")
        for f in sql_files:
            print(f"  - {f.name:<30} ({f.stat().st_size:,} bytes)")
    print("=" * 80)


def cmd_import_templates(args: argparse.Namespace) -> None:
    config = get_config()
    storage = StorageManager()
    pipeline = CleaningPipeline()

    print("=" * 70)
    print("AI AUTO PAKISTAN — IMPORTING RESEARCH DATASET TEMPLATES")
    print("=" * 70)

    records = []
    # 1. Facebook
    fb_path = config.templates_dir / "facebook_research_template.csv"
    if fb_path.exists():
        fb_recs = FacebookResearchImporter().import_manual_csv(fb_path)
        records.extend(fb_recs)
        print(f"  [OK] Facebook: Imported {len(fb_recs)} record(s)")

    # 2. PakWheels
    pw_path = config.templates_dir / "pakwheels_research_template.csv"
    if pw_path.exists():
        pw_recs = PakWheelsResearchImporter().import_manual_csv(pw_path)
        records.extend(pw_recs)
        print(f"  [OK] PakWheels: Imported {len(pw_recs)} record(s)")

    # 3. Mechanic Interviews
    mi_path = config.templates_dir / "mechanic_interview_template.csv"
    if mi_path.exists():
        mi_recs = MechanicInterviewImporter().import_csv(mi_path)
        records.extend(mi_recs)
        print(f"  [OK] Mechanic Interviews: Imported {len(mi_recs)} record(s)")

    # 4. Owner Reports
    or_path = config.templates_dir / "owner_problem_report_template.csv"
    if or_path.exists():
        or_recs = OwnerProblemReportImporter().import_csv(or_path)
        records.extend(or_recs)
        print(f"  [OK] Owner Reports: Imported {len(or_recs)} record(s)")


    print(f"\nTotal imported records: {len(records)}")
    print("Executing Cleaning & Normalization Pipeline...")
    res = pipeline.process_batch(records)

    # Insert into Relational Database
    for r in records:
        storage.insert_record(r)

    print(f"  * Unique Processed Records : {res['unique_processed']}")
    print(f"  * Duplicates Flagged       : {res['duplicates_flagged']}")
    print(f"  * ML-Ready Records         : {res['ml_ready_records']}")
    print(f"  * Needs Review             : {res['needs_review_records']}")
    print(f"  * Relational DB Updated    : {storage.db_path.name}")
    print("=" * 70)


def cmd_report(args: argparse.Namespace) -> None:
    generator = DatasetReportGenerator()
    rep = generator.generate_report()
    dest = generator.export_markdown_report()

    print("=" * 70)
    print("AI AUTO PAKISTAN -- DATASET QUALITY & AUDIT REPORT")
    print("=" * 70)
    print(f"Database Total Records:   {rep['database_total_records']}")
    print(f"ML-Ready Records:         {rep['ml_ready_records']}")
    print(f"Audit Trail Events:       {rep['audit_trail_events']}")
    print("\nRecords by Source:")
    for src, cnt in rep["database_records_by_source"].items():
        print(f"  * {src:<22}: {cnt}")
    print("\nRecords by Fault Category:")
    for cat, cnt in rep["records_by_category"].items():
        print(f"  * {cat:<22}: {cnt}")
    print("\nRecords by Language:")
    for lang, cnt in rep["records_by_language"].items():
        print(f"  * {lang:<22}: {cnt}")
    print(f"\nMarkdown Report Exported: {dest}")
    print("=" * 70)


def cmd_split(args: argparse.Namespace) -> None:
    config = get_config()
    print("=" * 70)
    print("AI AUTO PAKISTAN -- LEAK-FREE ML DATASET PARTITIONING")
    print("=" * 70)

    # Load from templates or database
    all_records = []
    fb_path = config.templates_dir / "facebook_research_template.csv"
    if fb_path.exists():
        all_records.extend(FacebookResearchImporter().import_manual_csv(fb_path))
    pw_path = config.templates_dir / "pakwheels_research_template.csv"
    if pw_path.exists():
        all_records.extend(PakWheelsResearchImporter().import_manual_csv(pw_path))
    mi_path = config.templates_dir / "mechanic_interview_template.csv"
    if mi_path.exists():
        all_records.extend(MechanicInterviewImporter().import_csv(mi_path))
    or_path = config.templates_dir / "owner_problem_report_template.csv"
    if or_path.exists():
        all_records.extend(OwnerProblemReportImporter().import_csv(or_path))

    splitter = GroupedMLSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    train, val, test = splitter.split_records(all_records)
    outputs = splitter.export_splits(train, val, test)

    print(f"Total Available Records:   {len(all_records)}")
    print(f"Train Records (70%):       {len(train)}")
    print(f"Val Records   (15%):       {len(val)}")
    print(f"Test Records  (15%):       {len(test)}")
    print(f"Dataset Card Saved:        {outputs.get('dataset_card')}")
    print("=" * 70)


def cmd_consolidate(args: argparse.Namespace) -> None:
    print("=" * 70)
    print("AI AUTO PAKISTAN -- CONSOLIDATING LOCAL DATASETS & ML SPLITS")
    print("=" * 70)
    res = LocalDatasetConsolidator().consolidate_all(include_examples=True)
    print(json.dumps(res, indent=2))
    print("=" * 70)


def cmd_serve(args: argparse.Namespace) -> None:
    import uvicorn
    print(f"Starting AI Auto Pakistan Dataset Engineering Dashboard on http://{args.host}:{args.port}")
    uvicorn.run("data_engine.server:app", host=args.host, port=args.port, reload=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m data_engine.cli",
        description="AI Auto Pakistan Data Engineering Command-Line Interface",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Show system directories, keys, and operational status")
    subparsers.add_parser("sources", help="List registered automotive sources and legal policies")
    subparsers.add_parser("inspect", help="Inspect and audit existing codebase assets")
    subparsers.add_parser("consolidate", help="Consolidate all local datasets into DB and ML splits")
    subparsers.add_parser("import-templates", help="Import research CSV templates into DB & pipeline")
    subparsers.add_parser("report", help="Generate dataset quality and coverage audit report")
    subparsers.add_parser("split", help="Generate leak-free train/val/test ML datasets")
    serve_p = subparsers.add_parser("serve", help="Start Dataset Engineering Dashboard on localhost")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8090)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "status":
        cmd_status(args)
    elif args.command == "sources":
        cmd_sources(args)
    elif args.command == "inspect":
        cmd_inspect(args)
    elif args.command == "consolidate":
        cmd_consolidate(args)
    elif args.command == "import-templates":
        cmd_import_templates(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "split":
        cmd_split(args)
    elif args.command == "serve":
        cmd_serve(args)


if __name__ == "__main__":
    main()
