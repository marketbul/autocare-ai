"""Unit tests for Phase 7: Data Normalization, Deduplication, and Quality Validation."""
from __future__ import annotations

import pytest

from data_engine.cleaning import (
    CleaningPipeline,
    DeduplicationEngine,
    canonicalize_url,
    detect_language,
    normalize_automotive_text,
    validate_price_sanity,
    validate_year_sanity,
)
from data_engine.schema import (
    AutomotiveRecord,
    CostInfo,
    ProblemInfo,
    SourceQualityInfo,
    VehicleInfo,
)


def test_canonicalize_url():
    raw1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&utm_source=twitter&fbclid=IwAR2"
    clean1 = canonicalize_url(raw1)
    assert "utm_source" not in clean1
    assert "fbclid" not in clean1
    assert "t=" not in clean1
    assert "v=dQw4w9WgXcQ" in clean1


def test_language_detection():
    # Urdu script
    assert detect_language("گاڑی گرم ہو رہی ہے اور پانی کم ہو رہا ہے") == "ur"

    # Roman Urdu
    assert detect_language("gaari start nahi ho rahi self awaz kar raha hai") == "roman_ur"

    # English
    assert detect_language("Engine knocking sound when accelerating on the highway") == "en"

    # Punjabi
    assert detect_language("veere gaadi start nahi ho rahi tusi dasso ki karan") == "punjabi"


def test_automotive_term_normalization():
    dirty = "injan se awaz aa rahi hai aur kangi kharab hai chimte bhi toot gaye"
    clean = normalize_automotive_text(dirty)

    assert "engine" in clean
    assert "steering rack (kangi)" in clean
    assert "lower control arms (chimte)" in clean


def test_price_and_year_sanity():
    assert validate_price_sanity(5000.0)[0] is True
    assert validate_price_sanity(-500)[0] is False
    assert validate_price_sanity(25_000_000)[0] is False

    assert validate_year_sanity(2018)[0] is True
    assert validate_year_sanity(1950)[0] is False
    assert validate_year_sanity(2035)[0] is False


def test_deduplication_engine():
    rec1 = AutomotiveRecord(
        vehicle=VehicleInfo(make="Toyota", model="Corolla", manufacturing_year=2018),
        problem=ProblemInfo(
            problem_title="Engine overheating issue",
            problem_description="Coolant boiling over",
            symptoms=["garam", "boiling"],
        ),
        source=SourceQualityInfo(
            source_platform="youtube",
            source_url="https://youtube.com/watch?v=same_id&t=10",
            source_id="vid_101",
            rights_basis="official_api_metadata",
            permission_status="public",
        ),
    )

    rec2 = AutomotiveRecord(
        vehicle=VehicleInfo(make="Toyota", model="Corolla", manufacturing_year=2018),
        problem=ProblemInfo(
            problem_title="Engine overheating issue",
            problem_description="Coolant boiling over",
            symptoms=["garam", "boiling"],
        ),
        source=SourceQualityInfo(
            source_platform="youtube",
            source_url="https://youtube.com/watch?v=same_id&utm_source=fb",
            source_id="vid_102",
            rights_basis="official_api_metadata",
            permission_status="public",
        ),
    )

    engine = DeduplicationEngine()
    unique, duplicates = engine.process_records([rec1, rec2])

    assert len(unique) == 1
    assert len(duplicates) == 1
    assert duplicates[0][2] == rec1.record_id, "Must reference the canonical record ID"
