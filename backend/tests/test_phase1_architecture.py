"""Phase 1 Architecture & Foundation Verification Tests for AI Auto Pakistan."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from data_engine.config import get_config
from data_engine.logger import AuditAction, AuditLogger
from data_engine.registry import RightsBasis, SourceType, create_default_source_registry


def test_config_resolution():
    config = get_config()
    assert config.backend_root.exists(), "Backend root must exist"
    assert config.data_dir.exists(), "Data directory must exist"
    assert config.raw_dir.exists(), "Raw data directory must exist"
    assert config.processed_dir.exists(), "Processed data directory must exist"
    assert config.ml_ready_dir.exists(), "ML ready data directory must exist"

    # Ethical and legal safeguards
    assert config.metadata_only_default is True
    assert config.require_consent_for_interviews is True
    assert config.anonymize_personal_identifiers is True
    assert config.allow_unauthorized_scraping is False

    # Check vehicle makes & languages
    assert "Suzuki" in config.supported_makes
    assert "Toyota" in config.supported_makes
    assert "Honda" in config.supported_makes
    assert "en" in config.supported_languages
    assert "ur" in config.supported_languages
    assert "roman_ur" in config.supported_languages


def test_source_registry():
    registry = create_default_source_registry()
    sources = registry.list_all()
    assert len(sources) >= 6, "Must register at least 6 primary automotive data sources"

    # YouTube checks
    yt = registry.get("youtube_official_api")
    assert yt is not None
    assert yt.source_type == SourceType.YOUTUBE
    assert yt.requires_api_key is True
    assert yt.is_automated is True

    # PakWheels checks (strictly respectful of Terms of Service)
    pw = registry.get("pakwheels_research_import")
    assert pw is not None
    assert pw.source_type == SourceType.PAKWHEELS
    assert pw.is_automated is False, "PakWheels must be manual research import, not unauthorized scraping"

    # Mechanic Interviews checks
    mi = registry.get("mechanic_interviews")
    assert mi is not None
    assert mi.rights_basis == RightsBasis.EXPLICIT_CONSENT
    assert mi.requires_permission is True

    # Owner Submissions
    os_src = registry.get("owner_submissions")
    assert os_src is not None
    assert os_src.source_type == SourceType.CAR_OWNER_REPORT


def test_audit_logger(tmp_path: Path):
    test_log = tmp_path / "test_audit.jsonl"
    logger = AuditLogger(log_path=test_log)

    entry1 = logger.log(
        action=AuditAction.COLLECTION_STARTED,
        source_id="youtube_official_api",
        record_id=None,
        status="SUCCESS",
        details={"query": "Suzuki Alto engine noise"},
    )
    assert entry1.status == "SUCCESS"
    assert test_log.exists()

    entry2 = logger.log(
        action=AuditAction.RECORD_DUPLICATE_FLAGGED,
        source_id="youtube_official_api",
        record_id="vid_123",
        status="WARNING",
        details={"reason": "Duplicate video ID detected"},
    )
    assert entry2.record_id == "vid_123"

    summary = logger.get_summary()
    assert summary["total_audit_events"] == 2
    assert summary["actions"]["collection_started"] == 1
    assert summary["actions"]["record_duplicate_flagged"] == 1
    assert summary["sources"]["youtube_official_api"] == 2


def test_search_queries_config():
    config = get_config()
    queries_json = config.queries_dir / "youtube_queries.json"
    queries_txt = config.queries_dir / "youtube_queries.txt"

    assert queries_json.exists(), "youtube_queries.json must exist"
    assert queries_txt.exists(), "youtube_queries.txt must exist"

    with open(queries_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "queries" in data
        assert len(data["queries"]) >= 15

        # Check vehicle problem coverage
        query_texts = [q["query"].lower() for q in data["queries"]]
        assert any("alto" in q for q in query_texts)
        assert any("corolla" in q for q in query_texts)
        assert any("civic" in q for q in query_texts)
        assert any("cultus" in q for q in query_texts)
