"""Unit & Integration Tests for YouTube Comments/License, Authorized Video Extraction & AI-Agent Export."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from data_engine.media import AuthorizedMediaPipeline, MediaVault
from data_engine.media.video_processor import get_ffmpeg_binary
from data_engine.ml import AIAgentDatasetExporter
from data_engine.server import app
from data_engine.sources.youtube import YouTubeCollector, classify_comment_intent
from data_engine.storage import StorageManager


def test_comment_intent_classification():
    assert classify_comment_intent("gaari start nahi ho rahi aur engine awaz de raha hai") == "problem_occurrence"
    assert classify_comment_intent("Thermostat valve replace karwaya theek ho gayi") == "suggested_solution"
    assert classify_comment_intent("Mechanic ne radiator cap replace kia rs 1500 kharcha aya") == "solution_with_cost"


def test_youtube_to_automotive_records_with_comments():
    collector = YouTubeCollector(api_key="dummy_test_key")
    raw_items = [
        {
            "video_id": "abc123xyz",
            "video_title": "Suzuki Cultus overheating issue and cooling fan fix",
            "video_description": "Explaining why Cultus overheats in Lahore traffic.",
            "channel_name": "Pak Garage",
            "video_url": "https://www.youtube.com/watch?v=abc123xyz",
            "thumbnail_url": "https://i.ytimg.com/vi/abc123xyz/hqdefault.jpg",
            "license": "creativeCommon",
            "duration": "08:15",
            "view_count": 12400,
            "tags": ["Cultus", "overheating", "radiator"],
            "vehicle_make": "Suzuki",
            "vehicle_model": "Cultus",
            "suspected_fault_category": "FC-09",
            "language": "roman_ur",
            "comments": [{"text": "Fan motor change karwaya rs 4500 mein hal ho gaya"}],
            "extracted_problem_comments": ["Meri Cultus traffic mein garam ho rahi hai"],
            "extracted_solution_comments": ["Fan motor change karwaya rs 4500 mein hal ho gaya"],
        }
    ]
    records = collector.to_automotive_records(raw_items)
    assert len(records) == 1
    rec = records[0]
    assert rec.vehicle.make == "Suzuki"
    assert rec.vehicle.model == "Cultus"
    assert rec.problem.fault_category == "FC-09"
    assert rec.repair is not None
    assert rec.repair.verification_status == "unverified"  # Comments are NEVER confirmed facts
    assert rec.cost is not None
    assert rec.cost.estimated_cost_pkr == 4500.0
    assert rec.source.permission_status == "cc_by_permitted"
    assert rec.media.image_reference == "https://i.ytimg.com/vi/abc123xyz/hqdefault.jpg"


def test_authorized_video_permission_gate_and_ffmpeg_extraction(tmp_path: Path, monkeypatch):
    # Create a real synthetic 2-second test video using bundled ffmpeg
    ffmpeg = get_ffmpeg_binary()
    sample_mp4 = tmp_path / "test_clip.mp4"
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=2",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        str(sample_mp4),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        pytest.skip("ffmpeg test video generation unavailable in this environment")

    vault = MediaVault(vault_dir=tmp_path / "vault")
    pipeline = AuthorizedMediaPipeline(vault=vault)

    # 1. Standard copyrighted YouTube license must be blocked
    with pytest.raises(PermissionError):
        pipeline.extract_audio_wav(sample_mp4, rights_basis="youtube")

    # 2. Permitted creativeCommon / explicit_consent video extracts audio + screenshots + claims
    test_db = tmp_path / "vid_test.db"
    import data_engine.media.video_processor as vp_mod
    monkeypatch.setattr(vp_mod, "StorageManager", lambda: StorageManager(db_path=test_db))

    res = pipeline.process_authorized_video(
        video_path=sample_mp4,
        rights_basis="explicit_consent",
        make="Suzuki",
        model="Alto",
        title="Alto radiator leak workshop inspection",
        timestamps_sec=[0.5, 1.5],
        transcript_text="Suzuki Alto 2021 radiator se pani leak ho raha hai cap replace karne par 1200 rupay kharcha aya.",
        attribution="Mechanic permission test",
    )

    assert Path(res["audio_asset"]["absolute_path"]).exists()
    assert len(res["screenshots"]) == 2
    assert all(Path(s["absolute_path"]).exists() for s in res["screenshots"])
    assert res["extracted_claims"]["vehicle_make"] == "Suzuki"
    assert res["extracted_claims"]["vehicle_model"] == "Alto"
    assert 1200.0 in res["extracted_claims"]["cost_mentions_pkr"]


def test_agent_jsonl_export_endpoint():
    client = TestClient(app)
    res = client.get("/api/v1/dataset/export/agent-jsonl")
    assert res.status_code == 200
    lines = [ln for ln in res.text.strip().splitlines() if ln.strip()]
    assert len(lines) >= 286
    first = json.loads(lines[0])
    assert "problem_occurrence" in first
    assert "solutions_and_repairs" in first
    assert "provenance" in first
    assert "is_verified_fact" in first["provenance"]
