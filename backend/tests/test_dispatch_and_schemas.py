"""Unit tests for Fault-to-Specialist Dispatch Engine and 4-Tier Lakehouse Schemas."""
from __future__ import annotations

import pytest
from autocare.dispatch import (
    DispatchRequest,
    detect_specialty,
    evaluate_composite_score,
    haversine_distance_km,
    recommend_specialist_workshops,
    SPECIALTIES,
    VERIFIED_WORKSHOPS
)
from autocare.lakehouse_schemas import (
    BronzeTelemetryEvent,
    CountingBloomFilter,
    SILVER_PARQUET_SCHEMA_DEF,
    GOLD_RELATIONAL_SCHEMAS
)

def test_haversine_distance_known_coordinates():
    # Distance between Lahore Bilal Gunj (31.5912, 74.3085) and Gulberg (31.5180, 74.3510) is ~9 km
    dist = haversine_distance_km(31.5912, 74.3085, 31.5180, 74.3510)
    assert 7.0 <= dist <= 12.0
    # Distance to same point is 0
    assert haversine_distance_km(31.5, 74.3, 31.5, 74.3) == 0.0

def test_detect_specialty_by_dtc():
    assert detect_specialty("P0217", None) == "engine_cooling"
    assert detect_specialty("C0035", None) == "brakes_hydraulics"
    assert detect_specialty("P0300", None) == "efi_electrical"
    assert detect_specialty("P0700", None) == "transmission_gearbox"
    assert detect_specialty("C1511", None) == "suspension_steering"
    assert detect_specialty("B1421", None) == "hvac_air_conditioning"

def test_detect_specialty_by_keywords():
    assert detect_specialty(None, "Mera radiator pani boil kar raha hai") == "engine_cooling"
    assert detect_specialty(None, "Brake pedal spongy hai aur ruk nahi rahi") == "brakes_hydraulics"
    assert detect_specialty(None, "Car missing kar rahi hai aur lambi self le rahi hai") == "efi_electrical"
    assert detect_specialty(None, "Gear change pe jhatka aur slip ho raha hai") == "transmission_gearbox"

def test_composite_scoring_weights():
    # Max score when skill=1.0, dist=0km, rating=5.0, queue=4 slots
    max_score = evaluate_composite_score(skill_match=1.0, distance_km=0.0, rating=5.0, queue_slots=4)
    assert round(max_score, 2) == 1.0

    # Score decreases when distance increases
    close_score = evaluate_composite_score(skill_match=1.0, distance_km=2.0, rating=4.8, queue_slots=2)
    far_score = evaluate_composite_score(skill_match=1.0, distance_km=20.0, rating=4.8, queue_slots=2)
    assert close_score > far_score

def test_dispatch_recommendation_pipeline():
    req = DispatchRequest(
        user_lat=31.5500,
        user_lon=74.3300,
        city="Lahore",
        dtc_code="P0217",
        symptom_text="radiator overheating",
        vehicle_make="Toyota"
    )
    res = recommend_specialist_workshops(req)
    assert res.detected_specialty == "engine_cooling"
    assert len(res.recommendations) > 0
    top_w = res.recommendations[0]
    assert "engine_cooling" in SPECIALTIES
    assert top_w.estimated_pkr_low > 0
    assert top_w.estimated_pkr_high > top_w.estimated_pkr_low
    assert top_w.composite_score > 0.0

def test_bronze_telemetry_schema_and_cas_hash():
    event = BronzeTelemetryEvent(
        timestamp="2026-11-17T08:30:00Z",
        vin="NZE1405021984000",
        make="Toyota",
        model="Corolla",
        year=2021,
        engine_rpm=2400,
        speed_kmh=65.0,
        coolant_temp_c=102.5,
        fuel_trim_pct=5.2,
        maf_rate_gs=16.8,
        active_dtc_codes=["P0217"]
    )
    cas_hash = event.compute_cas_hash()
    assert len(cas_hash) == 64
    assert isinstance(cas_hash, str)

def test_counting_bloom_filter():
    bf = CountingBloomFilter(size=1024, k_hashes=4)
    assert not bf.contains("P0217")
    bf.add("P0217")
    assert bf.contains("P0217")
    assert not bf.contains("P9999")
    # Test removal
    bf.remove("P0217")
    assert not bf.contains("P0217")

def test_lakehouse_schemas_integrity():
    assert "partition_keys" in SILVER_PARQUET_SCHEMA_DEF
    assert len(SILVER_PARQUET_SCHEMA_DEF["columns"]) >= 10
    assert "vehicles" in GOLD_RELATIONAL_SCHEMAS
    assert "mechanic_workshops" in GOLD_RELATIONAL_SCHEMAS
    assert "dispatch_tickets" in GOLD_RELATIONAL_SCHEMAS
