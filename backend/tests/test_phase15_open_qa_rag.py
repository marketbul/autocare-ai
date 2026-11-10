"""Unit Tests for Open Mechanics Q&A & NHTSA Safety REST Collectors (RAG Expansion)."""
from __future__ import annotations

from data_engine.registry import create_default_source_registry
from data_engine.sources.open_qa import (
    NHTSAComplaintsCollector,
    StackExchangeMechanicsCollector,
    clean_html_text,
)


def test_open_sources_registered():
    registry = create_default_source_registry()
    ids = {s.source_id for s in registry.list_all()}
    assert "stackexchange_mechanics" in ids
    assert "nhtsa_official_api" in ids


def test_clean_html_text_strips_markup_and_pii():
    raw = "<p>My Toyota Corolla won&#39;t start. Call 0300-1234567 &amp; check starter.</p>"
    cleaned = clean_html_text(raw)
    assert "<p>" not in cleaned
    assert "won't start" in cleaned
    assert "0300-1234567" not in cleaned
    assert "[PHONE REDACTED]" in cleaned


def test_stackexchange_collector_to_records():
    collector = StackExchangeMechanicsCollector()
    sample_items = [
        {
            "question_id": 99001,
            "title": "Toyota Corolla brakes squeal when stopping",
            "body": "Brake pads make high-pitched noise at slow speed.",
            "tags": ["toyota", "corolla", "brakes"],
            "score": 12,
            "view_count": 4500,
            "is_accepted": True,
            "link": "https://mechanics.stackexchange.com/questions/99001",
            "content_license": "CC BY-SA 4.0",
            "creation_date": 1700000000,
            "answers": [
                {"answer_id": 1, "is_accepted": True, "score": 15, "text": "Inspect worn brake pads and lubricate caliper pins."},
                {"answer_id": 2, "is_accepted": False, "score": 3, "text": "Also check rotor thickness for warping."},
            ],
        }
    ]
    records = collector.to_automotive_records(sample_items)
    assert len(records) == 1
    r = records[0]
    assert r.record_id == "se_99001"
    assert r.vehicle.make == "Toyota"
    assert r.vehicle.model == "Corolla"
    assert r.problem.fault_category == "FC-04"
    assert r.repair is not None
    assert "brake pads" in r.repair.recommended_solution.lower()
    assert r.repair.verification_status == "unverified"
    assert r.source.source_platform == "stackexchange_mechanics"


def test_nhtsa_collector_to_records():
    collector = NHTSAComplaintsCollector()
    payload = {
        "recalls": [
            {
                "NHTSACampaignNumber": "24V123000",
                "Component": "FUEL SYSTEM, GASOLINE:DELIVERY:FUEL PUMP",
                "Summary": "The low pressure fuel pump impeller may deform and cause stalling.",
                "Consequence": "Engine stall increases crash risk.",
                "Remedy": "Dealers will replace the fuel pump assembly free of charge.",
                "_make_q": "toyota",
                "_model_q": "corolla",
                "_year_q": 2020,
            }
        ],
        "complaints": [
            {
                "odiNumber": "11500001",
                "components": "ENGINE AND ENGINE COOLING",
                "summary": "Coolant leak near radiator hose caused engine overheating in traffic.",
                "fire": False,
                "crash": False,
                "_make_q": "honda",
                "_model_q": "civic",
                "_year_q": 2019,
            }
        ],
    }
    records = collector.to_automotive_records(payload)
    assert len(records) == 2

    rec, cmp_rec = records[0], records[1]
    assert rec.record_id == "nhtsa_rec_24V123000"
    assert rec.vehicle.make == "Toyota"
    assert rec.vehicle.model == "Corolla"
    assert rec.repair is not None and rec.repair.verification_status == "verified_by_oem"

    assert cmp_rec.record_id == "nhtsa_cmp_11500001"
    assert cmp_rec.vehicle.make == "Honda"
    assert cmp_rec.vehicle.model == "Civic"
    assert cmp_rec.source.source_platform == "nhtsa_official_api"
