"""Autonomous Zero-Port Dataset Collector & Local Folder Builder for AI Auto Pakistan.

Run from backend/:
    python -m data_engine.auto_collect_bundle
    python -m data_engine.auto_collect_bundle --all-queries --include-cc-search

Behavior:
1. Consolidates verified local project datasets into autocare.db + ML splits.
2. When YOUTUBE_API_KEY is available, collects metadata + comments via YouTube Data API v3.
3. Strictly honors license checks: processes video audio/screenshots ONLY when
   status.license == 'creativeCommon' (with yt_dlp) or for local permitted videos.
4. Transcribes spoken audio using faster-whisper and captures timestamped JPG screenshots
   at exact spoken damage/component moments (Urdu/Roman Urdu/English).
5. Exports everything into one standalone folder `<repo>/AI_Auto_Pakistan_Dataset/` with an offline
   `dataset_viewer.html` (`file:///...`) requiring NO server port.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cleaning import CleaningPipeline
from .media import AuthorizedMediaPipeline
from .media.video_processor import get_ffmpeg_binary
from .reports import LocalFolderBundleExporter
from .sources import LocalDatasetConsolidator, YouTubeCollector
from .storage import StorageManager

CC_AUTOMOTIVE_QUERIES = [
    "car brake pad damage inspection repair",
    "car engine knocking misfire sound",
    "car radiator overheating coolant leak",
    "car suspension noise repair",
    "car battery alternator problem",
]


def download_cc_video_if_permitted(
    video_url: str, license_val: str, out_dir: Path, duration_seconds: int = 0
) -> Optional[Path]:
    """Downloads a video ONLY if license=='creativeCommon' and yt_dlp is available."""
    if license_val != "creativeCommon":
        return None
    if importlib.util.find_spec("yt_dlp") is None:
        return None
    if duration_seconds and duration_seconds > 480:
        # Skip overly long (> 8 min) streams during automated batching
        return None

    ffmpeg_exe = get_ffmpeg_binary()
    out_tpl = str(out_dir / "%(id)s.%(ext)s")
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--ffmpeg-location",
        ffmpeg_exe,
        "-f",
        "bestvideo[height<=480]+bestaudio/best[acodec!=none][height<=480]/best",
        "--merge-output-format",
        "mp4",
        "-o",
        out_tpl,
        video_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    files = [p for p in out_dir.glob("*") if p.is_file() and p.suffix.lower() in {".mp4", ".webm", ".mkv", ".mov"}]
    return files[0] if files else None


def run_autonomous_bundle(
    api_key: Optional[str] = None,
    all_queries: bool = False,
    max_results: int = 5,
    include_cc_search: bool = False,
    max_cc_videos_to_process: int = 4,
    local_videos_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "youtube_status": "skipped_no_api_key",
        "youtube_videos_collected": 0,
        "youtube_comments_collected": 0,
        "cc_videos_found": 0,
        "cc_videos_processed": 0,
        "local_videos_processed": 0,
    }

    # Step 1: Consolidate verified local project datasets
    consol_res = LocalDatasetConsolidator().consolidate_all(include_examples=True)
    summary["local_consolidation"] = consol_res["counts"]

    # Step 2: YouTube Data API v3 Collection (only if API key configured)
    collector = YouTubeCollector(api_key=api_key)
    if collector.is_configured():
        summary["youtube_status"] = "ran"
        queries = [q["query"] for q in collector.load_search_queries()]
        if not all_queries:
            queries = queries[:3]

        all_raw: List[Dict[str, Any]] = []
        for q in queries:
            items = collector.fetch_video_metadata(q, max_results=max_results, include_comments=True)
            if items:
                collector.save_raw_batch(q, items)
                all_raw.extend(items)

        # Optional Creative Commons CC-BY search for permitted video transcription + screenshots
        if include_cc_search:
            for ccq in CC_AUTOMOTIVE_QUERIES:
                cc_items = collector.fetch_video_metadata(
                    ccq,
                    max_results=3,
                    include_comments=True,
                    max_comments_per_video=10,
                    video_license="creativeCommon",
                )
                if cc_items:
                    collector.save_raw_batch(f"cc_{ccq}", cc_items)
                    all_raw.extend(cc_items)

        records = collector.to_automotive_records(all_raw)
        if records:
            CleaningPipeline().process_batch(records)
            StorageManager().insert_records(records)

        summary["youtube_videos_collected"] = len(all_raw)
        summary["youtube_comments_collected"] = sum(len(i.get("comments") or []) for i in all_raw)

        # Process Creative Commons videos automatically (audio + Whisper STT + damage screenshots)
        cc_candidates = [it for it in all_raw if it.get("license") == "creativeCommon"]
        summary["cc_videos_found"] = len(cc_candidates)

        media_pipe = AuthorizedMediaPipeline()
        processed_vids: set[str] = set()
        for item in cc_candidates:
            if summary["cc_videos_processed"] >= max_cc_videos_to_process:
                break
            vid = item.get("video_id")
            if not vid or vid in processed_vids:
                continue
            with tempfile.TemporaryDirectory() as tmpdir:
                vid_path = download_cc_video_if_permitted(
                    item["video_url"],
                    item["license"],
                    Path(tmpdir),
                    duration_seconds=item.get("duration_seconds") or 0,
                )
                if vid_path:
                    media_pipe.process_authorized_video(
                        video_path=vid_path,
                        rights_basis="creative_common",
                        make=item.get("vehicle_make") or "Unknown",
                        model=item.get("vehicle_model") or "Unknown",
                        title=item.get("video_title") or "YouTube CC-BY Video",
                        attribution=item.get("channel_name") or "",
                        source_url=item.get("video_url"),
                    )
                    processed_vids.add(vid)
                    summary["cc_videos_processed"] += 1

    # Step 3: Process any explicitly authorized local mechanic/owner videos if provided
    if local_videos_dir and local_videos_dir.exists():
        media_pipe = AuthorizedMediaPipeline()
        for vf in local_videos_dir.glob("*.mp4"):
            media_pipe.process_authorized_video(
                video_path=vf,
                rights_basis="explicit_consent",
                title=vf.stem.replace("_", " "),
            )
            summary["local_videos_processed"] += 1

    # Step 4: Build standalone zero-port local folder bundle
    bundle_info = LocalFolderBundleExporter().export_bundle()
    summary["bundle"] = bundle_info
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build standalone offline AI Auto Pakistan Dataset Folder")
    parser.add_argument("--api-key", default=None, help="YouTube Data API v3 Key")
    parser.add_argument("--all-queries", action="store_true", help="Run all configured YouTube search queries")
    parser.add_argument("--include-cc-search", action="store_true", help="Also query CC-BY automotive clips for STT + screenshots")
    parser.add_argument("--max-cc-videos", type=int, default=4, help="Max CC-BY videos to transcribe & screenshot")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--local-videos-dir", default=None, help="Optional folder of consented MP4 videos")
    args = parser.parse_args()

    res = run_autonomous_bundle(
        api_key=args.api_key,
        all_queries=args.all_queries,
        max_results=args.max_results,
        include_cc_search=args.include_cc_search,
        max_cc_videos_to_process=args.max_cc_videos,
        local_videos_dir=Path(args.local_videos_dir) if args.local_videos_dir else None,
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
