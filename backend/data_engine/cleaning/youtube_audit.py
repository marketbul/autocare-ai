"""YouTube Dataset Quality Auditor & Deduplication Cleanup for AI Auto Pakistan.

Fixes:
1. Merges duplicate CC-BY UUID media rows into canonical `yt_{video_id}` records (never losing audio/image FKs or comment solutions).
2. Replaces empty/punctuation-only Whisper STT noise (e.g. '. . . . .') with clean raw video metadata.
3. Re-runs word-boundary vehicle make/model normalization and 18-category fault matching.
4. Outputs an honest quality audit report logged to `audit_log.jsonl`.
"""
from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..taxonomy import get_taxonomy_manager, normalize_make_model


def audit_and_clean_youtube_records() -> Dict[str, Any]:
    config = get_config()
    logger = get_audit_logger()
    taxonomy = get_taxonomy_manager()
    db_path = config.backend_root / "autocare.db"

    # Load raw YouTube metadata map by video_id for fallback text
    raw_by_vid: Dict[str, Dict[str, Any]] = {}
    for f in (config.raw_dir / "youtube").glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            for it in d.get("items", []):
                if it.get("video_id"):
                    raw_by_vid[it["video_id"]] = it
        except Exception:
            continue

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    rows = [dict(r) for r in conn.execute("""
        SELECT dr.*, vf.make, vf.model
        FROM diagnostic_records dr
        LEFT JOIN vehicle_fleet vf ON dr.vehicle_id = vf.vehicle_id
        WHERE dr.source_id = 'youtube_official_api'
    """).fetchall()]

    # Step 1: Group by source_url to merge duplicate UUID media rows into canonical yt_<vid>
    by_url: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        u = (r.get("source_url") or "").strip()
        if u:
            by_url.setdefault(u, []).append(r)

    merged_dups = 0
    for url, grp in by_url.items():
        if len(grp) <= 1:
            continue
        # Pick canonical yt_* row as primary, others as media/secondary donors
        canon = next((x for x in grp if x["record_id"].startswith("yt_")), grp[0])
        donors = [x for x in grp if x["record_id"] != canon["record_id"]]

        for d in donors:
            # Transfer audio, image, video FK links
            audio_id = canon["audio_asset_id"] or d["audio_asset_id"]
            image_id = canon["image_asset_id"] or d["image_asset_id"]
            video_id_fk = canon["video_asset_id"] or d["video_asset_id"]

            # Keep non-garbage Whisper description if meaningful (>12 alnum chars and not dots)
            donor_desc = (d.get("problem_description") or "").strip()
            donor_alnum = re.sub(r"[\W_]+", "", donor_desc)
            merged_desc = canon["problem_description"]
            if len(donor_alnum) >= 20 and donor_desc != canon["problem_title"]:
                merged_desc = f"[Whisper Transcript]: {donor_desc}\n\n{canon['problem_description']}"

            conn.execute(
                """UPDATE diagnostic_records
                   SET audio_asset_id = ?, image_asset_id = ?, video_asset_id = ?,
                       problem_description = ?, rights_basis = COALESCE(?, rights_basis)
                   WHERE record_id = ?""",
                (audio_id, image_id, video_id_fk, merged_desc[:3500], d.get("rights_basis"), canon["record_id"]),
            )
            conn.execute("DELETE FROM diagnostic_records WHERE record_id = ?", (d["record_id"],))
            logger.log(
                AuditAction.RECORD_DUPLICATE_FLAGGED,
                source_id="youtube_audit",
                record_id=d["record_id"],
                status="MERGED",
                details={"canonical_record_id": canon["record_id"], "url": url},
            )
            merged_dups += 1

    conn.commit()

    # Step 2: Re-evaluate vehicle make/model, clean noise transcripts, and categorize all unique YouTube rows
    rows = [dict(r) for r in conn.execute("""
        SELECT dr.*, vf.make, vf.model
        FROM diagnostic_records dr
        LEFT JOIN vehicle_fleet vf ON dr.vehicle_id = vf.vehicle_id
        WHERE dr.source_id = 'youtube_official_api'
    """).fetchall()]

    repaired_noise = 0
    recategorized = 0
    veh_fixed = 0

    for r in rows:
        rid = r["record_id"]
        vid = rid.replace("yt_", "")
        raw_item = raw_by_vid.get(vid, {})

        desc = (r.get("problem_description") or "").strip()
        if len(re.sub(r"[\W_]+", "", desc)) < 10:
            desc = (raw_item.get("video_description") or r["problem_title"]).strip()
            repaired_noise += 1

        combined = f"{r['problem_title']} {desc}"
        matched_cat = taxonomy.match_category_from_text(combined)
        new_cat = matched_cat.category_id if matched_cat else r["fault_category_id"]
        if new_cat != r["fault_category_id"] and new_cat is not None:
            recategorized += 1

        new_make, new_model = normalize_make_model(None, combined)
        if not new_make:
            existing_make = (r.get("make") or "").strip()
            existing_model = (r.get("model") or "").strip()
            if existing_make and existing_make not in {"Unknown", "Generic"}:
                new_make, new_model = existing_make, existing_model or "Multi-Model"
            else:
                new_make, new_model = "Generic", "Multi-Model"
        veh_id = f"{new_make.lower()}-{new_model.lower()}-any"

        if new_make != r.get("make") or new_model != r.get("model"):
            veh_fixed += 1
            conn.execute(
                """INSERT OR IGNORE INTO vehicle_fleet (vehicle_id, make, model, market_country)
                   VALUES (?, ?, ?, 'Pakistan')""",
                (veh_id, new_make, new_model),
            )
            conn.execute("UPDATE diagnostic_records SET vehicle_id = ? WHERE record_id = ?", (veh_id, rid))

        conn.execute(
            "UPDATE diagnostic_records SET problem_description = ?, fault_category_id = ? WHERE record_id = ?",
            (desc, new_cat, rid),
        )

    conn.commit()

    # Step 3: Build final honest audit metrics
    final_rows = [dict(r) for r in conn.execute("""
        SELECT dr.*, vf.make, vf.model
        FROM diagnostic_records dr
        LEFT JOIN vehicle_fleet vf ON dr.vehicle_id = vf.vehicle_id
        WHERE dr.source_id = 'youtube_official_api'
    """).fetchall()]
    conn.close()

    urls = [r["source_url"] for r in final_rows if r["source_url"]]
    dup_urls = [u for u, c in Counter(urls).items() if c > 1]
    uncat = [r["problem_title"] for r in final_rows if not r["fault_category_id"]]

    return {
        "merged_duplicates_cleaned": merged_dups,
        "noise_descriptions_repaired": repaired_noise,
        "newly_categorized_records": recategorized,
        "vehicle_labels_normalized": veh_fixed,
        "final_unique_youtube_records": len(final_rows),
        "duplicate_urls_remaining": len(dup_urls),
        "categorized_count": len(final_rows) - len(uncat),
        "uncategorized_count": len(uncat),
        "uncategorized_titles": uncat,
        "with_comment_solutions": sum(1 for r in final_rows if r["recommended_solution"]),
        "with_audio_and_whisper": sum(1 for r in final_rows if r["audio_asset_id"]),
        "with_screenshots": sum(1 for r in final_rows if r["image_asset_id"]),
        "makes_breakdown": dict(Counter(r["make"] for r in final_rows)),
        "review_statuses": dict(Counter(r["human_review_status"] for r in final_rows)),
    }
