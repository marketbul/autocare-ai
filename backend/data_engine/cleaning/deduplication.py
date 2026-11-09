"""Deduplication Engine for AI Auto Pakistan.

Detects duplicates across:
1. Exact Video IDs (e.g., YouTube vids)
2. Canonical URLs (strips tracking parameters, query params, hash fragments)
3. Content SimHash / Text Fingerprint on normalized problem symptoms

Rule: Never silently drop records. Flag duplicates, record canonical reference, and log to audit.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Set, Tuple
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from ..logger import AuditAction, get_audit_logger
from ..schema import AutomotiveRecord


def canonicalize_url(url: str) -> str:
    """Normalizes URLs by removing tracking query parameters (fbclid, utm_*, t=)."""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    query_params = parse_qs(parsed.query)

    # Strip marketing and timestamp tracking parameters
    stripped_params = {
        k: v for k, v in query_params.items()
        if not k.startswith("utm_") and k not in {"fbclid", "t", "ref", "source"}
    }
    clean_query = urlencode(stripped_params, doseq=True)
    clean_url = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/"),
        parsed.params,
        clean_query,
        "",  # drop fragment
    ))
    return clean_url


def compute_content_fingerprint(record: AutomotiveRecord) -> str:
    """Computes an MD5 fingerprint from normalized vehicle and symptom text."""
    parts = [
        (record.vehicle.make or "").strip().lower(),
        (record.vehicle.model or "").strip().lower(),
        str(record.vehicle.manufacturing_year or ""),
        (record.problem.problem_title or "").strip().lower(),
        " ".join(sorted(s.strip().lower() for s in record.problem.symptoms)),
    ]
    raw = "|".join(parts)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


class DeduplicationEngine:
    """Maintains deduplication state across ingestion sessions."""

    def __init__(self) -> None:
        self.seen_urls: Dict[str, str] = {}         # canonical_url -> first_record_id
        self.seen_video_ids: Dict[str, str] = {}    # video_id -> first_record_id
        self.seen_fingerprints: Dict[str, str] = {} # fingerprint -> first_record_id
        self.logger = get_audit_logger()

    def process_records(
        self, records: List[AutomotiveRecord]
    ) -> Tuple[List[AutomotiveRecord], List[Tuple[AutomotiveRecord, str, str]]]:
        """
        Evaluates records for duplicates.
        Returns:
            (unique_records, duplicate_records_with_reason_and_canonical_id)
        """
        unique: List[AutomotiveRecord] = []
        duplicates: List[Tuple[AutomotiveRecord, str, str]] = []

        for rec in records:
            # 1. Check URL
            raw_url = rec.source.source_url or ""
            canon_url = canonicalize_url(raw_url) if raw_url else ""
            if canon_url and canon_url in self.seen_urls:
                canonical_id = self.seen_urls[canon_url]
                duplicates.append((rec, f"Duplicate URL matching record {canonical_id}", canonical_id))
                self.logger.log(
                    AuditAction.RECORD_DUPLICATE_FLAGGED,
                    source_id=rec.source.source_platform,
                    record_id=rec.record_id,
                    status="WARNING",
                    details={"reason": "Duplicate URL", "canonical_id": canonical_id, "url": canon_url},
                )
                continue

            # 2. Check Video ID
            video_ref = rec.media.video_reference if rec.media else None
            yt_id = rec.source.source_id if rec.source.source_platform == "youtube" else None
            vid = video_ref or yt_id
            if vid and vid in self.seen_video_ids:
                canonical_id = self.seen_video_ids[vid]
                duplicates.append((rec, f"Duplicate Video ID matching record {canonical_id}", canonical_id))
                self.logger.log(
                    AuditAction.RECORD_DUPLICATE_FLAGGED,
                    source_id=rec.source.source_platform,
                    record_id=rec.record_id,
                    status="WARNING",
                    details={"reason": "Duplicate Video ID", "canonical_id": canonical_id, "vid": vid},
                )
                continue

            # 3. Check Content Fingerprint
            fp = compute_content_fingerprint(rec)
            if fp in self.seen_fingerprints:
                canonical_id = self.seen_fingerprints[fp]
                duplicates.append((rec, f"Identical problem fingerprint matching {canonical_id}", canonical_id))
                self.logger.log(
                    AuditAction.RECORD_DUPLICATE_FLAGGED,
                    source_id=rec.source.source_platform,
                    record_id=rec.record_id,
                    status="WARNING",
                    details={"reason": "Identical symptom content", "canonical_id": canonical_id},
                )
                continue

            # Register as canonical
            if canon_url:
                self.seen_urls[canon_url] = rec.record_id
            if vid:
                self.seen_video_ids[vid] = rec.record_id
            self.seen_fingerprints[fp] = rec.record_id
            unique.append(rec)

        return unique, duplicates
