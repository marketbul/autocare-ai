"""Official YouTube Data API v3 Metadata & Comments Collector for AI Auto Pakistan.

Harvests structured automotive video metadata, channel provenance, license status,
thumbnail references, and public comment problem/solution discussions.

Adheres strictly to YouTube API Terms of Service & Project Ethics:
- Collects metadata, official thumbnails, and public comment threads via official REST API.
- Checks status.license ('creativeCommon' vs 'youtube') before allowing media extraction.
- Never downloads copyrighted Standard YouTube License videos/audio automatically.
- Scrubs PII from comments and keeps community comment claims tagged as 'unverified'.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..media.transcription import COST_MENTION_REGEX
from ..schema import (
    AutomotiveRecord,
    CostInfo,
    ImageVideoInfo,
    ProblemInfo,
    RepairInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from ..taxonomy import DiagnosisStage, get_taxonomy_manager, normalize_make_model
from .submissions import scrub_pii

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_COMMENTS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

SOLUTION_KEYWORDS = (
    "solution", "fixed", "solve", "hal", "theek", "replace", "change", "badla",
    "badal", "clean", "saaf", "check", "mechanic", "workshop", "karwaya", "lagwaya",
    "repair", "wiring", "sensor", "fuse", "relay", "flush", "tuning",
)
PROBLEM_KEYWORDS = (
    "problem", "issue", "masla", "kharab", "awaz", "garam", "overheat", "start nahi",
    "miss", "misfire", "jerk", "jhatka", "smoke", "dhuan", "leak", "vibrat", "light",
    "kyun", "kaise", "error", "fault", "band ho", "average",
)


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


def parse_iso8601_seconds(duration_str: str) -> int:
    """Returns total seconds for ISO 8601 duration."""
    if not duration_str or not duration_str.startswith("PT"):
        return 0
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return 0
    hours, minutes, seconds = match.groups()
    return (int(hours or 0) * 3600) + (int(minutes or 0) * 60) + int(seconds or 0)


def classify_comment_intent(text: str) -> str:
    """Classifies whether a comment describes a problem occurrence, suggested solution, or cost."""
    low = (text or "").lower()
    has_cost = bool(COST_MENTION_REGEX.search(low))
    has_sol = any(k in low for k in SOLUTION_KEYWORDS)
    has_prob = any(k in low for k in PROBLEM_KEYWORDS)
    if has_cost and has_sol:
        return "solution_with_cost"
    if has_sol:
        return "suggested_solution"
    if has_prob:
        return "problem_occurrence"
    if has_cost:
        return "cost_experience"
    return "discussion"


class YouTubeCollector:
    """Automated metadata and comments collector powered by YouTube Data API v3."""

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

    def fetch_video_comments(
        self, video_id: str, max_comments: int = 15, client: Optional[httpx.Client] = None
    ) -> List[Dict[str, Any]]:
        """Fetches public top-level comments and replies for a YouTube video."""
        if not self.is_configured():
            raise ValueError("YouTube API key is not configured.")

        params = {
            "key": self.api_key,
            "videoId": video_id,
            "part": "snippet,replies",
            "order": "relevance",
            "textFormat": "plainText",
            "maxResults": min(max_comments, 50),
        }
        headers = {"User-Agent": "AIAutoPakistan-DataEngine/1.0"}

        def _do_request(c: httpx.Client) -> httpx.Response:
            return c.get(YOUTUBE_COMMENTS_URL, params=params, headers=headers)

        if client is not None:
            resp = _do_request(client)
        else:
            with httpx.Client(timeout=self.config.request_timeout_seconds) as c:
                resp = _do_request(c)

        # Comments can be disabled on some videos (403 commentsDisabled)
        if resp.status_code == 403:
            return []
        resp.raise_for_status()
        data = resp.json()

        comments: List[Dict[str, Any]] = []
        for thread in data.get("items", []):
            top = thread.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            raw_text = (top.get("textDisplay") or top.get("textOriginal") or "").strip()
            clean_text = scrub_pii(raw_text)
            if not clean_text:
                continue

            replies_out: List[Dict[str, Any]] = []
            for rep in thread.get("replies", {}).get("comments", []):
                rs = rep.get("snippet", {})
                rep_text = scrub_pii((rs.get("textDisplay") or rs.get("textOriginal") or "").strip())
                if rep_text:
                    replies_out.append({
                        "text": rep_text,
                        "intent": classify_comment_intent(rep_text),
                        "like_count": int(rs.get("likeCount", 0)),
                        "published_at": rs.get("publishedAt"),
                    })

            comments.append({
                "comment_id": thread.get("id"),
                "text": clean_text,
                "intent": classify_comment_intent(clean_text),
                "like_count": int(top.get("likeCount", 0)),
                "published_at": top.get("publishedAt"),
                "replies": replies_out,
            })

        return comments

    def fetch_video_metadata(
        self,
        query: str,
        max_results: int = 10,
        include_comments: bool = True,
        max_comments_per_video: int = 15,
        video_license: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Queries YouTube API v3 and returns enriched metadata + comments."""
        if not self.is_configured():
            raise ValueError(
                "YouTube API key is not configured. Please set YOUTUBE_API_KEY in your .env file."
            )

        self.logger.log(
            AuditAction.COLLECTION_STARTED,
            source_id="youtube_official_api",
            status="RUNNING",
            details={"query": query, "max_results": max_results, "include_comments": include_comments, "video_license": video_license},
        )

        headers = {"User-Agent": "AIAutoPakistan-DataEngine/1.0"}
        search_params: Dict[str, Any] = {
            "key": self.api_key,
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": min(max_results, 50),
            "relevanceLanguage": "ur",
        }
        if video_license:
            search_params["videoLicense"] = video_license

        with httpx.Client(timeout=self.config.request_timeout_seconds) as client:
            resp = client.get(YOUTUBE_SEARCH_URL, params=search_params, headers=headers)
            resp.raise_for_status()
            search_data = resp.json()

            items = search_data.get("items", [])
            video_ids = [it["id"]["videoId"] for it in items if "videoId" in it.get("id", {})]

            if not video_ids:
                return []

            details_params = {
                "key": self.api_key,
                "id": ",".join(video_ids),
                "part": "snippet,contentDetails,statistics,status",
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
                status_info = item.get("status", {})

                title = snippet.get("title", "")
                desc = snippet.get("description", "")
                thumbs = snippet.get("thumbnails", {})
                thumb_url = (
                    thumbs.get("high", {}).get("url")
                    or thumbs.get("medium", {}).get("url")
                    or thumbs.get("default", {}).get("url")
                )

                comments: List[Dict[str, Any]] = []
                if include_comments:
                    comments = self.fetch_video_comments(
                        vid_id, max_comments=max_comments_per_video, client=client
                    )

                comments_blob = " ".join(
                    [c["text"] + " " + " ".join(r["text"] for r in c.get("replies", [])) for c in comments]
                )
                combined_text = f"{title} {desc} {comments_blob}"

                matched_cat = self.taxonomy.match_category_from_text(combined_text)
                make, model = normalize_make_model(None, combined_text)

                problem_comments = [
                    c["text"] for c in comments if c["intent"] == "problem_occurrence"
                ]
                solution_comments = []
                for c in comments:
                    if c["intent"] in {"suggested_solution", "solution_with_cost"}:
                        solution_comments.append(c["text"])
                    for rep in c.get("replies", []):
                        if rep["intent"] in {"suggested_solution", "solution_with_cost"}:
                            solution_comments.append(rep["text"])

                rec = {
                    "video_id": vid_id,
                    "video_title": title,
                    "video_description": desc,
                    "channel_name": snippet.get("channelTitle", ""),
                    "channel_id": snippet.get("channelId", ""),
                    "video_url": f"https://www.youtube.com/watch?v={vid_id}",
                    "thumbnail_url": thumb_url,
                    "license": status_info.get("license", "youtube"),
                    "has_captions": content.get("caption") == "true",
                    "publication_date": snippet.get("publishedAt", ""),
                    "duration": parse_iso8601_duration(content.get("duration", "")),
                    "duration_seconds": parse_iso8601_seconds(content.get("duration", "")),
                    "view_count": int(stats.get("viewCount", 0)) if "viewCount" in stats else None,
                    "like_count": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
                    "comment_count": int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
                    "tags": snippet.get("tags", []),
                    "search_query_used": query,
                    "vehicle_make": make,
                    "vehicle_model": model,
                    "suspected_fault_category": matched_cat.category_id if matched_cat else None,
                    "language": snippet.get("defaultAudioLanguage") or snippet.get("defaultLanguage") or "roman_ur",
                    "comments": comments,
                    "extracted_problem_comments": problem_comments[:5],
                    "extracted_solution_comments": solution_comments[:5],
                    "collection_date": dt.datetime.now(dt.timezone.utc).isoformat(),
                }
                records.append(rec)
                self.logger.log(
                    AuditAction.RECORD_INGESTED,
                    source_id="youtube_official_api",
                    record_id=f"yt_{vid_id}",
                    status="SUCCESS",
                    details={
                        "title": title,
                        "channel": rec["channel_name"],
                        "license": rec["license"],
                        "comments_collected": len(comments),
                    },
                )

        self.logger.log(
            AuditAction.COLLECTION_COMPLETED,
            source_id="youtube_official_api",
            status="SUCCESS",
            details={"query": query, "records_harvested": len(records)},
        )
        return records

    def save_raw_batch(self, query: str, records: List[Dict[str, Any]]) -> Path:
        """Saves a batch of raw records (with comments & metadata) to data/raw/youtube/."""
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
        """Converts raw YouTube metadata + comments into normalized AutomotiveRecord instances."""
        out: List[AutomotiveRecord] = []
        for item in raw_items:
            vid_id = item.get("video_id", "")
            title = (item.get("video_title") or "Untitled YouTube Automotive Video").strip()
            desc = (item.get("video_description") or title).strip()
            make = item.get("vehicle_make") or "Unknown"
            model = item.get("vehicle_model") or "Unknown"
            tags = [str(t).strip() for t in item.get("tags", []) if str(t).strip()][:8]
            prob_comments = item.get("extracted_problem_comments") or []
            sol_comments = item.get("extracted_solution_comments") or []

            lang = item.get("language") or "roman_ur"
            if lang not in {"en", "ur", "roman_ur", "punjabi"}:
                lang = "roman_ur" if lang.startswith("ur") else "en"

            # Combine description with comment-reported problem context without inventing facts
            desc_parts = [desc[:1400]]
            if prob_comments:
                desc_parts.append("Viewer Problem Reports: " + " | ".join(prob_comments[:3]))
            full_desc = scrub_pii("\n".join(p for p in desc_parts if p))

            # Extract any PKR cost mentions from description/comments
            cost_val = None
            for m in COST_MENTION_REGEX.finditer(f"{desc} {' '.join(sol_comments)}"):
                raw_num = m.group(1) or m.group(2)
                if raw_num:
                    try:
                        val = float(raw_num.replace(",", ""))
                        if "hazaar" in m.group(0).lower() or "k" in m.group(0).lower():
                            val *= 1000
                        if 100 <= val <= 2_000_000:
                            cost_val = val
                            break
                    except ValueError:
                        pass

            proposed_sol = " | ".join(sol_comments[:3]) if sol_comments else None
            license_val = item.get("license", "youtube")
            rights = "creative_common_api_metadata" if license_val == "creativeCommon" else "official_api_metadata"

            rec = AutomotiveRecord(
                record_id=f"yt_{vid_id}" if vid_id else str(uuid.uuid4()),
                vehicle=VehicleInfo(make=make, model=model),
                problem=ProblemInfo(
                    problem_title=title,
                    problem_description=full_desc[:2500],
                    symptoms=tags + prob_comments[:3],
                    fault_category=item.get("suspected_fault_category"),
                    diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
                ),
                media=ImageVideoInfo(
                    image_reference=item.get("thumbnail_url"),
                    video_reference=vid_id or None,
                    media_type="video_metadata",
                    image_description=f"Duration: {item.get('duration', 'unknown')}, Views: {item.get('view_count', 0)}, License: {license_val}",
                    annotation_status="unannotated",
                ),
                repair=RepairInfo(
                    recommended_solution=proposed_sol,
                    verification_status="unverified",  # Social media / YouTube comments are NEVER verified facts
                ) if proposed_sol else None,
                cost=CostInfo(
                    estimated_cost_pkr=cost_val,
                    price_source="youtube_comment_mention",
                ) if cost_val else None,
                source=SourceQualityInfo(
                    source_platform="youtube",
                    source_url=item.get("video_url"),
                    source_id=vid_id or title[:32],
                    source_author_or_channel=item.get("channel_name"),
                    publication_date=item.get("publication_date"),
                    collection_date=item.get("collection_date") or dt.datetime.now(dt.timezone.utc).isoformat(),
                    language=lang,
                    evidence_reference=f"license={license_val}; comments_analyzed={len(item.get('comments') or [])}",
                    rights_basis=rights,
                    permission_status="cc_by_permitted" if license_val == "creativeCommon" else "public_metadata",
                    human_review_status="pending",
                    confidence_score=0.6,
                ),
            )
            out.append(rec)
        return out
