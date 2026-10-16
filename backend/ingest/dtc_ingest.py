"""Load the OBD-II diagnostic-code reference into DIAGNOSTICCODE and as citable chunks.

Input CSV columns (header required):
  code, description, system, possible_causes, symptoms, severity, source_ref, page, section
`page` / `section` are where the entry appears in the source document, so the
answer can cite it. `section` may be blank (defaults to the code itself).

Each code becomes ONE chunk (chunk_type = dtc_entry), so a P0301 query can
never be answered from a chunk that also describes P0302.

Usage:
  python -m ingest.dtc_ingest --csv data/obd2_codes.csv \
      --document-name "SAE J2012 OBD-II Generic Code Definitions" \
      --source "<where you got it>" --license-note "<terms>"
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import uuid

REQUIRED = ["code", "description", "system", "possible_causes", "symptoms", "severity",
            "source_ref", "page"]


def entry_text(r: dict) -> str:
    parts = [f"{r['code'].strip().upper()}: {r['description'].strip()}"]
    for label, key in [("System", "system"), ("Possible causes", "possible_causes"),
                       ("Symptoms", "symptoms"), ("Severity", "severity")]:
        if (r.get(key) or "").strip():
            parts.append(f"{label}: {r[key].strip()}")
    return "\n".join(parts)


def load(repo, embedder, csv_path: str, document_name: str, source: str, license_note: str,
         version: str | None = None) -> str:
    from autocare.repository import encode_embedding

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in REQUIRED if rows and c not in rows[0]]
    if missing:
        raise SystemExit(f"CSV missing columns: {missing}")

    doc_id = str(uuid.uuid4())
    repo.insert_document({
        "document_id": doc_id, "vehicle_id": None,  # generic: applies to every vehicle
        "document_name": document_name, "document_type": "dtc_reference", "version": version,
        "source": source, "license_note": license_note,
        "ingest_date": dt.date.today().isoformat(),
    })
    texts = [entry_text(r) for r in rows]
    vectors = embedder.encode(texts) if texts else []
    chunks = []
    for r, text, vec in zip(rows, texts, vectors):
        code = r["code"].strip().upper()
        repo.upsert_diagnostic_code({
            "code": code, "description": r["description"].strip(),
            "system": r.get("system"), "possible_causes": r.get("possible_causes"),
            "symptoms": r.get("symptoms"), "severity": r.get("severity"),
            "source_ref": r.get("source_ref"),
        })
        chunks.append({
            "chunk_id": str(uuid.uuid4()), "document_id": doc_id,
            "section": (r.get("section") or "").strip() or code,
            "page_number": int(r["page"]) if (r.get("page") or "").strip() else None,
            "text": text, "embedding": encode_embedding(vec), "chunk_type": "dtc_entry",
        })
    repo.insert_chunks(chunks)
    return doc_id


def main() -> None:
    from autocare.config import load_settings
    from autocare.db import Database
    from autocare.ml import build_models
    from autocare.repository import Repository

    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--document-name", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--license-note", required=True)
    ap.add_argument("--version", default=None)
    a = ap.parse_args()

    s = load_settings()
    db = Database(s.database_url)
    db.create_schema()
    embedder, _ = build_models(s)
    doc_id = load(Repository(db), embedder, a.csv, a.document_name, a.source, a.license_note, a.version)
    print(f"Loaded DTC reference as document {doc_id}")


if __name__ == "__main__":
    main()
