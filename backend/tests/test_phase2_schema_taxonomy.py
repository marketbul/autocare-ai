"""Phase 2 Unit Tests: Automotive Fault Taxonomy & Normalized Schema for AI Auto Pakistan."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from data_engine.schema import (
    AudioInfo,
    AutomotiveRecord,
    CostInfo,
    ImageVideoInfo,
    ProblemInfo,
    RepairInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from data_engine.taxonomy import (
    AUTOMOTIVE_FAULT_CATEGORIES,
    DiagnosisStage,
    get_taxonomy_manager,
    normalize_make_model,
)


def test_fault_categories_completeness():
    assert len(AUTOMOTIVE_FAULT_CATEGORIES) == 18, "Must contain exactly 18 standard fault categories"

    expected_ids = [f"FC-{i:02d}" for i in range(1, 19)]
    for eid in expected_ids:
        assert eid in AUTOMOTIVE_FAULT_CATEGORIES
        cat = AUTOMOTIVE_FAULT_CATEGORIES[eid]
        assert cat.name, f"Category {eid} missing name"
        assert cat.name_ur, f"Category {eid} missing Urdu name"
        assert cat.name_roman_ur, f"Category {eid} missing Roman Urdu name"
        assert len(cat.subcomponents) >= 4, f"Category {eid} needs subcomponents"
        assert len(cat.multilingual_symptom_keywords) >= 4, f"Category {eid} needs symptom keywords"


def test_taxonomy_manager_keyword_matching():
    tm = get_taxonomy_manager()

    # Overheating query
    match1 = tm.match_category_from_text("gaari garam ho rahi hai aur radiator se steam nikal rahi hai")
    assert match1 is not None
    assert match1.category_id == "FC-09", "Must match Cooling System"

    # Brake squeal
    match2 = tm.match_category_from_text("brake lagane par seeti aur chis ki awaz aati hai")
    assert match2 is not None
    assert match2.category_id == "FC-04", "Must match Brakes"

    # Starting / self motor
    match3 = tm.match_category_from_text("gaari start nahi ho rahi self awaz kar raha hai")
    assert match3 is not None
    assert match3.category_id == "FC-17", "Must match Starting and Ignition"


def test_fleet_normalization():
    make, model = normalize_make_model("suzuki", "alto vxr")
    assert make == "Suzuki" and model == "Alto"

    make, model = normalize_make_model("toyota", "corolla grande")
    assert make == "Toyota" and model == "Corolla"

    make, model = normalize_make_model(None, "mehran euro 2")
    assert make == "Suzuki" and model == "Mehran"


def test_automotive_record_schema():
    record = AutomotiveRecord(
        vehicle=VehicleInfo(
            make="Suzuki",
            model="Alto",
            variant="VXL AGS",
            manufacturing_year=2021,
            engine_cc=660,
            engine_type="R06A",
            fuel_type="Petrol",
            transmission="AGS",
            mileage_km=42000,
        ),
        problem=ProblemInfo(
            problem_title="Engine knocking sound at cold start",
            problem_description="Ticking and knocking noise from engine head when starting in the morning",
            symptoms=["khatkhat awaz", "cold start rattle", "rough idle"],
            fault_category="FC-01",
            affected_component="Tappets / Hydraulic Lifters",
            suspected_causes=["Low oil pressure at start", "Worn valve lifters"],
            severity="moderate",
            diagnosis_stage=DiagnosisStage.MECHANIC_SUGGESTED_CAUSE.value,
        ),
        audio=AudioInfo(
            sound_category="Engine knocking",
            sound_description="Metallic rhythmic tapping synchronized with engine RPM",
            engine_rpm=950,
            vehicle_stationary_or_moving="stationary",
            audio_quality="high",
        ),
        cost=CostInfo(
            estimated_cost_pkr=8500.0,
            parts_cost_pkr=5500.0,
            labor_cost_pkr=3000.0,
            city="Lahore",
            price_date="2026-05-15",
            price_source="workshop_bill",
        ),
        source=SourceQualityInfo(
            source_platform="youtube",
            source_url="https://youtube.com/watch?v=sample123",
            source_id="yt_sample123",
            source_author_or_channel="Pak Mechanic Garage",
            language="roman_ur",
            rights_basis="official_api_metadata",
            permission_status="public_metadata",
            confidence_score=0.85,
        ),
    )

    flat = record.to_flat_dict()
    assert flat["make"] == "Suzuki"
    assert flat["model"] == "Alto"
    assert flat["manufacturing_year"] == 2021
    assert flat["fault_category"] == "FC-01"
    assert flat["estimated_cost_pkr"] == 8500.0
    assert flat["sound_category"] == "Engine knocking"


def test_schema_validators():
    # Year validation
    with pytest.raises(ValidationError):
        VehicleInfo(make="Toyota", model="Corolla", manufacturing_year=1940)

    # Cost negative validation
    with pytest.raises(ValidationError):
        CostInfo(estimated_cost_pkr=-500)
