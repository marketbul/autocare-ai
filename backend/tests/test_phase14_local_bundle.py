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
from data_engine.taxonomy import normalize_make_model


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
    assert Path(res["qa_solutions_file"]).exists()
    qa_payload = json.loads(Path(res["qa_solutions_file"]).read_text(encoding="utf-8"))
    assert "summary" in qa_payload and "records" in qa_payload
    assert Path(res["facebook_qa_file"]).exists()
    fb_payload = json.loads(Path(res["facebook_qa_file"]).read_text(encoding="utf-8"))
    assert "summary" in fb_payload and "records" in fb_payload
    assert Path(res["online_qa_file"]).exists()
    open_payload = json.loads(Path(res["online_qa_file"]).read_text(encoding="utf-8"))
    assert "summary" in open_payload and "records" in open_payload
    assert (bundle_out / "ml_splits" / "dataset_card.json").exists()
    assert res["viewer_file_url"].startswith("file:///")

    html = Path(res["viewer_html"]).read_text(encoding="utf-8")
    assert "AI Auto Pakistan" in html
    assert "Offline Local Dataset Folder Viewer" in html


def test_normalize_make_model_word_boundaries():
    assert normalize_make_model(None, "electricity and battery") != ("Honda", "City")
    assert normalize_make_model(None, "2018 Hyundai Elantra") == ("Hyundai", "Elantra")
    assert normalize_make_model(None, "Toyota GLi brake noise") == ("Toyota", "Corolla")
    assert normalize_make_model(None, "Honda Reborn suspension") == ("Honda", "Civic")


def test_video_processor_noise_stt_and_record_id(tmp_path: Path, monkeypatch):
    ffmpeg = get_ffmpeg_binary()
    sample_mp4 = tmp_path / "brake_noise.mp4"
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=2",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        str(sample_mp4),
    ]
    if subprocess.run(cmd, capture_output=True).returncode != 0:
        pytest.skip("ffmpeg synthetic video generation unavailable")

    import data_engine.media.video_processor as vp_mod
    db_path = tmp_path / "noise_test.db"
    monkeypatch.setattr(vp_mod, "StorageManager", lambda: StorageManager(db_path=db_path))

    pipeline = AuthorizedMediaPipeline(vault=MediaVault(vault_dir=tmp_path / "vault"))
    res = pipeline.process_authorized_video(
        video_path=sample_mp4,
        rights_basis="creative_common",
        title="Brakes & Brake Pads Problems? Don't Ignore!",
        transcript_text=". . . . .",
        record_id="yt_test_noise_01",
    )
    assert res["record_id"] == "yt_test_noise_01"
    stored, _ = StorageManager(db_path=db_path).query_records(include_examples=True, limit=10)
    assert len(stored) == 1
    assert stored[0]["record_id"] == "yt_test_noise_01"
    assert ". . . . ." not in (stored[0]["problem_description"] or "")
    assert stored[0]["fault_category_id"] == "FC-04"
