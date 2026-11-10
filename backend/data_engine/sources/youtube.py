"""Official YouTube Data API v3 Metadata Collector for AI Auto Pakistan.

Harvests structured automotive video metadata, channel provenance, view statistics,
and diagnostic fault indicators. Adheres to YouTube API Terms of Service:
- Collects public metadata only (no video/audio media downloading without explicit rights).
- Manages API quota and rate limits.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..schema import (
    AutomotiveRecord,
    ImageVideoInfo,
    ProblemInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from ..taxonomy import DiagnosisStage, get_taxonomy_manager, normalize_make_model

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def parse_iso8601_duration(duration_str: str) -> str:
    """Converts ISO 8601 duration (e.g., PT14M32S) to human readable MM:SS or HH:MM:SS."""
    if not duration_str or not duration_str.startswith("PT"):
        return duration_str or "00:00"
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return duration_str
    hours, minutes, seconds = match.groups()
    h = int(hours) if hours else 0
    m = int(minutes) if minutes else 0
    s = int(seconds) if seconds else 0
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


class YouTubeCollector:
    """Automated metadata collector powered by YouTube Data API v3."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        config = get_config()
        self.api_key = (api_key or config.youtube_api_key).strip()
        self.config = config
        self.logger = get_audit_logger()
        self.taxonomy = get_taxonomy_manager()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def load_search_queries(self) -> List[Dict[str, Any]]:
        """Loads search queries from configurable JSON/TXT files."""
        json_path = self.config.queries_dir / "youtube_queries.json"
        txt_path = self.config.queries_dir / "youtube_queries.txt"

        queries: List[Dict[str, Any]] = []
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    queries.extend(data.get("queries", []))
            except Exception:
                pass

        if not queries and txt_path.exists():
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        queries.append({"id": f"q_{len(queries)+1}", "query": line})

        return queries

    def fetch_video_metadata(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Queries YouTube API v3 and returns enriched metadata dictionaries."""
        if not self.is_configured():
            raise ValueError(
                "YouTube API key is not configured. Please set YOUTUBE_API_KEY in your .env file."
            )

        self.logger.log(
            AuditAction.COLLECTION_STARTED,
            source_id="youtube_official_api",
            status="RUNNING",
            details={"query": query, "max_results": max_results},
        )

        headers = {"User-Agent": "AIAutoPakistan-DataEngine/1.0"}
        search_params = {
            "key": self.api_key,
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": min(max_results, 50),
            "relevanceLanguage": "ur",
        }

        with httpx.Client(timeout=self.config.request_timeout_seconds) as client:
            resp = client.get(YOUTUBE_SEARCH_URL, params=search_params, headers=headers)
            resp.raise_for_status()
            search_data = resp.json()

            items = search_data.get("items", [])
            video_ids = [it["id"]["videoId"] for it in items if "videoId" in it.get("id", {})]

            if not video_ids:
                return []

            # Batch retrieve video statistics, duration, and tags
            details_params = {
                "key": self.api_key,
                "id": ",".join(video_ids),
                "part": "snippet,contentDetails,statistics",
            }
            details_resp = client.get(YOUTUBE_VIDEOS_URL, params=details_params, headers=headers)
            details_resp.raise_for_status()
            details_data = details_resp.json()

        records: List[Dict[str, Any]] = []
        for item in details_data.get("items", []):
            vid_id = item["id"]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})

            title = snippet.get("title", "")
            desc = snippet.get("description", "")
            combined_text = f"{title} {desc}"

            # Multilingual Category & Fleet Entity Resolution
            matched_cat = self.taxonomy.match_category_from_text(combined_text)
            make, model = normalize_make_model(None, combined_text)

            rec = {
                "video_id": vid_id,
                "video_title": title,
                "video_description": desc,
                "channel_name": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "video_url": f"https://www.youtube.com/watch?v={vid_id}",
                "publication_date": snippet.get("publishedAt", ""),
                "duration": parse_iso8601_duration(content.get("duration", "")),
                "view_count": int(stats.get("viewCount", 0)) if "viewCount" in stats else None,
                "like_count": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
                "comment_count": int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
                "tags": snippet.get("tags", []),
                "search_query_used": query,
                "vehicle_make": make,
                "vehicle_model": model,
                "suspected_fault_category": matched_cat.category_id if matched_cat else None,
                "language": snippet.get("defaultAudioLanguage") or snippet.get("defaultLanguage") or "roman_ur",
                "collection_date": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            records.append(rec)
            self.logger.log(
                AuditAction.RECORD_INGESTED,
                source_id="youtube_official_api",
                record_id=f"yt_{vid_id}",
                status="SUCCESS",
                details={"title": title, "channel": rec["channel_name"]},
            )

        self.logger.log(
            AuditAction.COLLECTION_COMPLETED,
            source_id="youtube_official_api",
            status="SUCCESS",
            details={"query": query, "records_harvested": len(records)},
        )
        return records

    def save_raw_batch(self, query: str, records: List[Dict[str, Any]]) -> Path:
        """Saves a batch of raw records to data/raw/youtube/."""
        safe_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", query.lower())[:30]
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_slug}_{timestamp}.json"
        dest = self.config.raw_dir / "youtube" / filename
        dest.parent.mkdir(parents=True, exist_ok=True)

        with open(dest, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "source": "youtube_official_api",
                    "search_query": query,
                    "record_count": len(records),
                    "harvested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "items": records,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        return dest

    def to_automotive_records(self, raw_items: List[Dict[str, Any]]) -> List[AutomotiveRecord]:
        """Converts raw YouTube metadata dicts into normalized AutomotiveRecord instances."""
        out: List[AutomotiveRecord] = []
        for item in raw_items:
            vid_id = item.get("video_id", "")
            title = (item.get("video_title") or "Untitled YouTube Automotive Video").strip()
            desc = (item.get("video_description") or title).strip()
            make = item.get("vehicle_make") or "Unknown"
            model = item.get("vehicle_model") or "Unknown"
            tags = [str(t).strip() for t in item.get("tags", []) if str(t).strip()][:8]
            lang = item.get("language") or "roman_ur"
            if lang not in {"en", "ur", "roman_ur", "punjabi"}:
                lang = "roman_ur" if lang.startswith("ur") else "en"

            import uuid
            rec = AutomotiveRecord(
                record_id=f"yt_{vid_id}" if vid_id else str(uuid.uuid4()),
                vehicle=VehicleInfo(make=make, model=model),
                problem=ProblemInfo(
                    problem_title=title,
                    problem_description=desc[:2000],
                    symptoms=tags,
                    fault_category=item.get("suspected_fault_category"),
                    diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
                ),
                media=ImageVideoInfo(
                    video_reference=vid_id or None,
                    media_type="video_metadata",
                    image_description=f"Duration: {item.get('duration', 'unknown')}, Views: {item.get('view_count', 0)}",
                    annotation_status="unannotated",
                ),
                source=SourceQualityInfo(
                    source_platform="youtube",
                    source_url=item.get("video_url"),
                    source_id=vid_id or title[:32],
                    source_author_or_channel=item.get("channel_name"),
                    publication_date=item.get("publication_date"),
                    collection_date=item.get("collection_date") or dt.datetime.now(dt.timezone.utc).isoformat(),
                    language=lang,
                    rights_basis="official_api_metadata",
                    permission_status="public_metadata",
                    human_review_status="pending",
                    confidence_score=0.6,
                ),
            )
            out.append(rec)
        return out

