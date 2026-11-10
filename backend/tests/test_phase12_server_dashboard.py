"""Integration tests for Local Consolidation and FastAPI Dataset Engineering Server."""
from __future__ import annotations

import base64
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from data_engine.config import get_config
from data_engine.server import app
from data_engine.sources import AutomotiveBlogImporter, LocalDatasetConsolidator
from data_engine.storage import StorageManager


def test_local_consolidator_counts():
    consolidator = LocalDatasetConsolidator()
    obd2 = consolidator.load_obd2_codes()
    symptoms = consolidator.load_symptom_corpus()
    manuals = consolidator.load_manuals()
    prices = consolidator.load_pakistan_prices()
    examples = consolidator.load_template_examples()

    assert len(obd2) == 18
    assert len(symptoms) == 207
    assert len(manuals) == 45
    assert len(prices) == 16
    assert len(examples) == 4
    assert all(e.source.rights_basis == "example_template" for e in examples)


def test_dashboard_and_read_endpoints():
    client = TestClient(app)

    res_html = client.get("/")
    assert res_html.status_code == 200
    assert "AI Auto Pakistan" in res_html.text

    res_health = client.get("/api/v1/dataset/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_stats = client.get("/api/v1/dataset/stats")
    assert res_stats.status_code == 200
    summary = res_stats.json()["summary"]
    assert summary["real_collected_records"] >= 286
    assert summary["total_fault_categories"] == 18
    assert summary["youtube_records"] == 0  # Honest zero when no API collection ran

    res_cats = client.get("/api/v1/dataset/categories")
    assert res_cats.status_code == 200
    assert res_cats.json()["total"] == 18

    res_fleet = client.get("/api/v1/dataset/vehicles")
    assert res_fleet.status_code == 200
    assert res_fleet.json()["total"] >= 100

    res_costs = client.get("/api/v1/dataset/costs")
    assert res_costs.status_code == 200
    assert res_costs.json()["total"] >= 16

    res_tpl = client.get("/api/v1/dataset/templates/pakwheels_research_template.csv")
    assert res_tpl.status_code == 200
    assert "thread_url" in res_tpl.text

    res_blog_tpl = client.get("/api/v1/dataset/templates/automotive_blogs_research_template.csv")
    assert res_blog_tpl.status_code == 200
    assert "article_url" in res_blog_tpl.text

    blog_recs = AutomotiveBlogImporter().import_manual_csv(
        get_config().templates_dir / "automotive_blogs_research_template.csv"
    )
    assert len(blog_recs) == 1
    assert blog_recs[0].vehicle.make == "Suzuki"
    assert blog_recs[0].vehicle.model == "Alto"

    res_exp = client.get("/api/v1/dataset/export/csv")
    assert res_exp.status_code == 200
    assert "record_id" in res_exp.text


def test_youtube_requires_api_key(monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    import data_engine.server as srv
    monkeypatch.setattr(srv, "get_config", lambda: type("Cfg", (), {
        "youtube_api_key": "",
        "facebook_access_token": "",
        "metadata_only_default": True,
        "require_consent_for_interviews": True,
        "anonymize_personal_identifiers": True,
    })())

    client = TestClient(app)
    res = client.post("/api/v1/dataset/collect/youtube", json={"queries": ["Suzuki Alto engine"], "max_results_per_query": 2})
    assert res.status_code == 400
    assert "YOUTUBE_API_KEY" in res.json()["detail"]


def test_create_record_and_review_isolated(tmp_path: Path, monkeypatch):
    test_db = tmp_path / "isolated_test.db"
    import data_engine.server as srv
    monkeypatch.setattr(srv, "StorageManager", lambda: StorageManager(db_path=test_db))

    client = TestClient(app)
    payload = {
        "make": "Suzuki",
        "model": "Alto",
        "manufacturing_year": 2022,
        "problem_title": "Engine overheating in summer traffic",
        "problem_description": "Call me at 0300-1234567. Gaari garam ho rahi hai and radiator fan is slow.",
        "symptoms": ["garam ho rahi hai", "fan slow"],
        "estimated_cost_pkr": 3500,
        "city": "Lahore",
        "source_platform": "owner_submission",
        "consent_given": True,
    }
    res = client.post("/api/v1/dataset/records", json=payload)
    assert res.status_code == 200
    body = res.json()
    rec_id = body["record_id"]

    # PII must be scrubbed
    assert "0300-1234567" not in body["record"]["problem"]["problem_description"]
    assert "[PHONE REDACTED]" in body["record"]["problem"]["problem_description"]

    # Review endpoint
    rev = client.post(f"/api/v1/dataset/records/{rec_id}/review", json={"status": "ml_ready", "reviewer_notes": "Verified"})
    assert rev.status_code == 200
    assert rev.json()["record"]["human_review_status"] == "ml_ready"
