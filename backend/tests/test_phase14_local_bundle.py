"""Tests for Spoken Damage-Moment Screenshot Capture and Zero-Port Local Bundle Exporter."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
import pytest

from data_engine.media import AuthorizedMediaPipeline, MediaVault
from data_engine.media.video_processor import detect_damage_moments, get_ffmpeg_binary
from data_engine.reports import LocalFolderBundleExporter
from data_engine.storage import StorageManager


def test_detect_damage_moments_multilingual():
    segments = [
        {"start": 0.0, "end": 3.0, "text": "Assalam o Alaikum dosto welcome to our garage"},
        {"start": 4.0, "end": 8.0, "text": "Bhai yahan dekhein brakes ka pad toot gaya hai aur rotor damaged hai"},
        {"start": 10.0, "end": 14.0, "text": "یہاں ریڈی ایٹر میں لیک ہے اور گاڑی گرم ہو رہی ہے"},
        {"start": 15.0, "end": 18.0, "text": "Please subscribe to the channel"},
    ]
    moments = detect_damage_moments(segments)
    assert len(moments) == 2
    assert moments[0]["timestamp_sec"] == 6.0
    assert "brakes" in moments[0]["matched_cues"] or "pad" in moments[0]["matched_cues"]
    assert moments[1]["timestamp_sec"] == 12.0


def test_damage_moment_screenshot_capture(tmp_path: Path, monkeypatch):
    ffmpeg = get_ffmpeg_binary()
    sample_mp4 = tmp_path / "brake_story.mp4"
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", "color=c=red:s=320x240:d=4",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        str(sample_mp4),
    ]
    if subprocess.run(cmd, capture_output=True).returncode != 0:
        pytest.skip("ffmpeg synthetic video generation unavailable")

    import data_engine.media.video_processor as vp_mod
    monkeypatch.setattr(vp_mod, "StorageManager", lambda: StorageManager(db_path=tmp_path / "dm.db"))

    pipeline = AuthorizedMediaPipeline(vault=MediaVault(vault_dir=tmp_path / "vault"))
    res = pipeline.process_authorized_video(
        video_path=sample_mp4,
        rights_basis="explicit_consent",
        make="Toyota",
        model="Corolla",
        title="Corolla brake damage inspection",
        transcript_segments=[
            {"start": 0.0, "end": 1.0, "text": "Intro"},
            {"start": 1.5, "end": 3.5, "text": "Yahan brake pad damage hai"},
        ],
    )
    assert len(res["damage_moments"]) == 1
    assert res["damage_moments"][0]["timestamp_sec"] == 2.5
    assert any(s.get("video_timestamp_sec") == 2.5 for s in res["screenshots"])


def test_local_folder_bundle_exporter(tmp_path: Path):
    bundle_out = tmp_path / "AI_Auto_Pakistan_Dataset"
    res = LocalFolderBundleExporter(bundle_dir=bundle_out).export_bundle()

    assert Path(res["viewer_html"]).exists()
    assert Path(res["master_json"]).exists()
    assert Path(res["master_jsonl"]).exists()
    assert Path(res["master_csv"]).exists()
    assert Path(res["ai_agent_knowledge"]).exists()
    assert (bundle_out / "ml_splits" / "dataset_card.json").exists()
    assert res["viewer_file_url"].startswith("file:///")

    html = Path(res["viewer_html"]).read_text(encoding="utf-8")
    assert "AI Auto Pakistan" in html
    assert "Offline Local Dataset Folder Viewer" in html
