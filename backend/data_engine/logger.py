"""Audit and Provenance Logger for AI Auto Pakistan Data Engineering System.

Ensures complete traceability:
- Every collection run, ingest, validation, deduplication, and cleaning step is logged.
- Never silently drops records: flagged or duplicate items are recorded with full rationale.
"""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import get_config


class AuditAction(str, Enum):
    COLLECTION_STARTED = "collection_started"
    COLLECTION_COMPLETED = "collection_completed"
    RECORD_INGESTED = "record_ingested"
    RECORD_VALIDATED = "record_validated"
    RECORD_NORMALIZED = "record_normalized"
    RECORD_DUPLICATE_FLAGGED = "record_duplicate_flagged"
    RECORD_REJECTED = "record_rejected"
    RECORD_REVIEWED = "record_reviewed"
    DATASET_SPLIT_GENERATED = "dataset_split_generated"
    MEDIA_EXTRACTED = "media_extracted"


@dataclass
class AuditEntry:
    timestamp: str
    action: str
    source_id: str
    record_id: Optional[str]
    status: str
    details: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class AuditLogger:
    """Append-only audit logger saving to JSONL and tracking operational stats."""

    def __init__(self, log_path: Optional[Path] = None) -> None:
        config = get_config()
        self.log_path = log_path or config.audit_log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._action_counts: Dict[str, int] = {}

    def log(
        self,
        action: AuditAction,
        source_id: str,
        record_id: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
            action=action.value,
            source_id=source_id,
            record_id=record_id,
            status=status,
            details=details or {},
        )
        self._action_counts[action.value] = self._action_counts.get(action.value, 0) + 1
        with open(self.log_path, mode="a", encoding="utf-8") as f:
            f.write(entry.to_json() + "\n")
        return entry

    def get_summary(self) -> Dict[str, Any]:
        """Reads recent audit history and aggregates action metrics."""
        summary = {
            "total_audit_events": 0,
            "actions": {},
            "statuses": {},
            "sources": {},
        }
        if not self.log_path.exists():
            return summary

        with open(self.log_path, mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    summary["total_audit_events"] += 1
                    act = data.get("action", "unknown")
                    st = data.get("status", "unknown")
                    src = data.get("source_id", "unknown")
                    summary["actions"][act] = summary["actions"].get(act, 0) + 1
                    summary["statuses"][st] = summary["statuses"].get(st, 0) + 1
                    summary["sources"][src] = summary["sources"].get(src, 0) + 1
                except json.JSONDecodeError:
                    continue
        return summary


_AUDIT_LOGGER_INSTANCE: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Singleton getter for AuditLogger."""
    global _AUDIT_LOGGER_INSTANCE
    if _AUDIT_LOGGER_INSTANCE is None:
        _AUDIT_LOGGER_INSTANCE = AuditLogger()
    return _AUDIT_LOGGER_INSTANCE
