"""Unit tests for Phases 8, 9, 10, 11 of AI Auto Pakistan Data Engine."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from data_engine.media import MediaVault, TranscriptClaimExtractor
from data_engine.ml import GroupedMLSplitter
from data_engine.reports import DatasetReportGenerator
from data_engine.schema import (
    AutomotiveRecord,
    CostInfo,
    ProblemInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from data_engine.storage import StorageManager


def test_media_vault(tmp_path: Path):
    vault = MediaVault(vault_dir=tmp_path / "vault")
    sample_file = tmp_path / "engine_knock.wav"
    sample_file.write_bytes(b"RIFF....WAVEfmt ....dataFAKEAUDIOBYTES123")

    asset = vault.store_asset(
        source_file=sample_file,
        asset_type="audio",
        rights_basis="explicit_consent",
        attribution="Field Recording by Ustad Rafiq",
    )

    assert asset["sha256"]
    assert "media_vault/audio/" in asset["relative_reference"]
    assert Path(asset["absolute_path"]).exists()


def test_transcript_claim_extractor():
    extractor = TranscriptClaimExtractor()
    raw_transcript = (
        "Assalam-o-Alaikum dosto, aaj hamare paas Suzuki Alto 660cc aayi hai. "
        "Customer keh raha hai ke gaari garam ho rahi hai aur radiator se pani leak ho raha hai. "
        "Iska radiator cap replace karna parega jiska kharcha taqreeban 1500 rupay hoga."
    )

    claims = extractor.process_transcript(raw_transcript)
    assert claims.vehicle_make == "Suzuki"
    assert claims.vehicle_model == "Alto"
    assert claims.matched_fault_category == "FC-09"  # Cooling System
    assert 1500.0 in claims.cost_mentions_pkr
    assert "replace" in claims.suggested_repairs


def test_database_storage_manager(tmp_path: Path):
    db_file = tmp_path / "test_engine.db"
    storage = StorageManager(db_path=db_file)

    rec = AutomotiveRecord(
        vehicle=VehicleInfo(make="Honda", model="City", manufacturing_year=2019),
        problem=ProblemInfo(
            problem_title="AC not cooling in traffic",
            problem_description="AC compressor trips in bumper-to-bumper traffic",
            symptoms=["AC tripping", "garmi"],
            fault_category="FC-12",
        ),
        cost=CostInfo(estimated_cost_pkr=7500.0, city="Islamabad"),
        source=SourceQualityInfo(
            source_platform="pakwheels",
            source_id="pw_test_1",
            source_url="https://pakwheels.com/test",
            rights_basis="manual_research_synthesis",
            permission_status="terms_compliant",
            human_review_status="ml_ready",
        ),
    )

    storage.insert_record(rec)
    stats = storage.get_dataset_statistics()

    assert stats["total_records"] == 1
    assert stats["by_source"]["pakwheels_research_import"] == 1
    assert stats["by_category"]["FC-12"] == 1
    assert stats["by_make"]["Honda"] == 1


def test_grouped_ml_splitter():
    splitter = GroupedMLSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_seed=42)

    # Create 10 records with shared URLs (groups of 2)
    records = []
    for g in range(5):
        url = f"https://youtube.com/watch?v=cluster_{g}"
        for r in range(2):
            records.append(
                AutomotiveRecord(
                    vehicle=VehicleInfo(make="Toyota", model="Corolla", manufacturing_year=2015 + g),
                    problem=ProblemInfo(
                        problem_title=f"Issue {g}-{r}",
                        problem_description="Problem narrative",
                        symptoms=["symptom"],
                        fault_category="FC-01",
                    ),
                    source=SourceQualityInfo(
                        source_platform="youtube",
                        source_id=f"yt_{g}_{r}",
                        source_url=url,
                        rights_basis="official_api_metadata",
                        permission_status="public",
                    ),
                )
            )

    train, val, test = splitter.split_records(records)
    assert len(train) + len(val) + len(test) == 10

    # Verify zero leakage across groups
    train_urls = {r.source.source_url for r in train}
    val_urls = {r.source.source_url for r in val}
    test_urls = {r.source.source_url for r in test}

    assert train_urls.isdisjoint(val_urls), "Train and Val must share no source URLs"
    assert train_urls.isdisjoint(test_urls), "Train and Test must share no source URLs"
    assert val_urls.isdisjoint(test_urls), "Val and Test must share no source URLs"
