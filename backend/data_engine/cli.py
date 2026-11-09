"""Command-Line Interface for AI Auto Pakistan Data Engineering Platform.

Usage:
    python -m data_engine.cli status       # Check system directories, keys, and status
    python -m data_engine.cli sources      # List registered data sources and legal terms
    python -m data_engine.cli inspect      # Detailed audit of existing codebase assets
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import get_config
from .logger import get_audit_logger
from .registry import create_default_source_registry


def cmd_status(args: argparse.Namespace) -> None:
    config = get_config()
    logger = get_audit_logger()
    summary = logger.get_summary()

    print("=" * 70)
    print("AI AUTO PAKISTAN — DATASET ENGINEERING SYSTEM STATUS")
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

    # Count files in raw directories
    raw_counts = {}
    for sub in ["youtube", "facebook", "pakwheels", "mechanic_notes", "owner_reports", "manuals"]:
        p = config.raw_dir / sub
        raw_counts[sub] = len(list(p.glob("*"))) if p.exists() else 0

    print("DATA DIRECTORY COUNTS:")
    for sub, count in raw_counts.items():
        print(f"  • Raw {sub.capitalize():<18}: {count} file(s)")

    processed_count = len(list(config.processed_dir.glob("*"))) if config.processed_dir.exists() else 0
    ml_count = len(list(config.ml_ready_dir.glob("*"))) if config.ml_ready_dir.exists() else 0
    print(f"  • Processed Records      : {processed_count} file(s)")
    print(f"  • ML-Ready Splits        : {ml_count} file(s)")
    print("-" * 70)

    print("AUDIT LOG ACTIVITY:")
    print(f"  • Total Events Logged    : {summary['total_audit_events']}")
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

    # 1. Inspect Python Modules in autocare
    autocare_dir = config.backend_root / "autocare"
    if autocare_dir.exists():
        py_files = sorted(autocare_dir.glob("*.py"))
        print(f"\n[Core Application Modules] in {autocare_dir.name}/ ({len(py_files)} files):")
        for f in py_files:
            print(f"  - {f.name:<25} ({f.stat().st_size:,} bytes)")

    # 2. Inspect Ingestion Scripts in ingest
    ingest_dir = config.backend_root / "ingest"
    if ingest_dir.exists():
        py_files = sorted(ingest_dir.glob("*.py"))
        print(f"\n[Existing Ingestion Scripts] in {ingest_dir.name}/ ({len(py_files)} files):")
        for f in py_files:
            print(f"  - {f.name:<25} ({f.stat().st_size:,} bytes)")

    # 3. Inspect Starter Datasets in data
    data_dir = config.backend_root / "data"
    if data_dir.exists():
        csv_files = sorted(data_dir.glob("*.csv"))
        print(f"\n[Existing Dataset Files] in {data_dir.name}/ ({len(csv_files)} files):")
        for f in csv_files:
            print(f"  - {f.name:<30} ({f.stat().st_size:,} bytes)")

    # 4. Inspect Schemas in sql
    sql_dir = config.backend_root / "sql"
    if sql_dir.exists():
        sql_files = sorted(sql_dir.glob("*.sql"))
        print(f"\n[Database Schemas] in {sql_dir.name}/ ({len(sql_files)} files):")
        for f in sql_files:
            print(f"  - {f.name:<30} ({f.stat().st_size:,} bytes)")

    # 5. Inspect Tests
    tests_dir = config.backend_root / "tests"
    if tests_dir.exists():
        test_files = sorted(tests_dir.glob("test_*.py"))
        print(f"\n[Test Suites] in {tests_dir.name}/ ({len(test_files)} test files):")
        for f in test_files:
            print(f"  - {f.name}")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m data_engine.cli",
        description="AI Auto Pakistan Data Engineering Command-Line Interface",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Show system directories, keys, and operational status")
    subparsers.add_parser("sources", help="List registered automotive sources and legal policies")
    subparsers.add_parser("inspect", help="Inspect and audit existing codebase assets")

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


if __name__ == "__main__":
    main()
