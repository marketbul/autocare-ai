"""Tests for Multi-Source Automotive Data Ingestion (Phases 3, 4, 5, 6)."""
from __future__ import annotations

from pathlib import Path
import pytest

from data_engine.config import get_config
from data_engine.sources import (
    FacebookResearchImporter,
    MechanicInterviewImporter,
    OwnerProblemReportImporter,
    PakWheelsResearchImporter,
    YouTubeCollector,
    scrub_pii,
)


def test_youtube_collector_configuration():
    collector = YouTubeCollector()
    queries = collector.load_search_queries()
    assert len(queries) >= 15, "Must load configured YouTube automotive search queries"

    # Verify duration parser
    from data_engine.sources.youtube import parse_iso8601_duration
    assert parse_iso8601_duration("PT15M30S") == "15:30"
    assert parse_iso8601_duration("PT1H02M05S") == "01:02:05"


def test_facebook_manual_import():
    config = get_config()
    template_path = config.templates_dir / "facebook_research_template.csv"
    assert template_path.exists()

    importer = FacebookResearchImporter()
    records = importer.import_manual_csv(template_path)
    assert len(records) == 1

    rec = records[0]
    assert rec.vehicle.make == "Suzuki"
    assert rec.vehicle.model == "Cultus"
    assert rec.source.source_platform == "facebook"
    assert rec.cost.estimated_cost_pkr == 12000.0


def test_pakwheels_manual_import():
    config = get_config()
    template_path = config.templates_dir / "pakwheels_research_template.csv"
    assert template_path.exists()

    importer = PakWheelsResearchImporter()
    records = importer.import_manual_csv(template_path)
    assert len(records) == 1

    rec = records[0]
    assert rec.vehicle.make == "Toyota"
    assert rec.vehicle.model == "Corolla"
    assert rec.source.source_platform == "pakwheels"
    assert rec.source.rights_basis == "manual_research_synthesis"


def test_mechanic_interview_consent_gate(tmp_path: Path):
    importer = MechanicInterviewImporter()

    # Case A: Valid with consent
    valid_csv = tmp_path / "valid_mechanic.csv"
    valid_csv.write_text(
        "interview_id,mechanic_name,experience_years,workshop_name,city,interview_date,consent,make,model,years,fault_topic,symptoms,diagnostic_advice,recommended_parts,estimated_labor_cost_pkr\n"
        "int_1,Ustad Aslam,20,Aslam Autos,Lahore,2026-05-01,yes,Toyota,Corolla,2015-2020,Overheating fan motor,high temp,replace motor,fan motor,1500\n",
        encoding="utf-8",
    )
    records = importer.import_csv(valid_csv)
    assert len(records) == 1
    assert records[0].source.rights_basis == "explicit_consent"

    # Case B: Refusal without consent
    no_consent_csv = tmp_path / "no_consent_mechanic.csv"
    no_consent_csv.write_text(
        "interview_id,mechanic_name,experience_years,workshop_name,city,interview_date,consent,make,model,years,fault_topic,symptoms,diagnostic_advice,recommended_parts,estimated_labor_cost_pkr\n"
        "int_2,Secret Mechanic,10,Secret Garage,Karachi,2026-05-01,no,Honda,Civic,2018,Brake issue,noise,fix pads,pads,2000\n",
        encoding="utf-8",
    )
    rejected_records = importer.import_csv(no_consent_csv)
    assert len(rejected_records) == 0, "Must strictly reject interview without consent"


def test_pii_scrubbing():
    dirty_text = "Call me at 0300-1234567 or +923219876543. CNIC is 35201-1234567-1, plate is LEA-2021, email test@yahoo.com."
    cleaned = scrub_pii(dirty_text)

    assert "0300-1234567" not in cleaned
    assert "+923219876543" not in cleaned
    assert "35201-1234567-1" not in cleaned
    assert "test@yahoo.com" not in cleaned
    assert "[PHONE REDACTED]" in cleaned
    assert "[CNIC REDACTED]" in cleaned
    assert "[EMAIL REDACTED]" in cleaned


def test_facebook_flexible_qa_file_import(tmp_path: Path):
    importer = FacebookResearchImporter()

    quick_csv = tmp_path / "quick_fb_qa.csv"
    quick_csv.write_text(
        "question,proposed_solution,city\n"
        "Meri Corolla GLi garm ho rahi hai call 0300-1234567,Radiator flush karwaya rs 2500 kharcha aya,Lahore\n",
        encoding="utf-8",
    )
    recs = importer.import_flexible_qa_file(quick_csv)
    assert len(recs) == 1
    assert recs[0].vehicle.make == "Toyota"
    assert recs[0].vehicle.model == "Corolla"
    assert "[PHONE REDACTED]" in recs[0].problem.problem_title
    assert recs[0].cost is not None and recs[0].cost.estimated_cost_pkr == 2500.0
    assert recs[0].repair is not None and recs[0].repair.verification_status == "unverified"

    json_path = tmp_path / "fb_qa.json"
    json_path.write_text(
        '[{"question": "Suzuki Alto gear jerking issue", "answers": ["AGS calibration resolved it"], "city": "Karachi"}]',
        encoding="utf-8",
    )
    jrecs = importer.import_flexible_qa_file(json_path)
    assert len(jrecs) == 1
    assert jrecs[0].vehicle.make == "Suzuki"
    assert jrecs[0].vehicle.model == "Alto"
    assert jrecs[0].repair.recommended_solution == "AGS calibration resolved it"
