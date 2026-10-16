"""Load advice recorded from real mechanics as citable sources ("mechanic notes").

Why: the owner's manual says what Toyota officially recommends; experienced
mechanics add practical workshop knowledge (likely causes, what to check, what a
repair usually involves). Recording it as named, dated notes keeps every piece of
advice traceable, so answers stay grounded (Story 2, AC2) instead of coming from
an LLM's memory.

Input CSV (header required) — see data/mechanic_notes.template.csv and
docs/mechanic_interview_guide.md:
  note_id, mechanic_name, experience_years, workshop, city, interview_date, consent,
  manufacturer, model, years, topic, advice

* consent must be "yes" (proposal §9.2), otherwise the row is skipped.
* manufacturer + model + years scope the note (years: 2018, 2014-2017 or 2015,2016).
  Leave all three blank for advice that applies to any car.
* One DOCUMENT per mechanic interview (and per model-year, because the schema links a
  document to one vehicle); one CHUNK per note. Notes have no page number; the topic
  is shown as the section.

Usage:
  python -m ingest.mechanic_notes --csv data/mechanic_notes.csv
  python -m ingest.mechanic_notes --csv data/mechanic_notes.csv --replace   # reload all notes
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import uuid
from collections import defaultdict

MECHANIC_NOTE = "mechanic_note"
REQUIRED = ["note_id", "mechanic_name", "experience_years", "workshop", "city", "interview_date",
            "consent", "manufacturer", "model", "years", "topic", "advice"]


def parse_years(spec: str) -> list[int]:
    spec = (spec or "").strip()
    if not spec:
        return []
    if "-" in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(y) for y in spec.split(",") if y.strip()]


def document_name(r: dict) -> str:
    who = r["mechanic_name"].strip()
    details = ", ".join(x for x in [
        f"{r['experience_years'].strip()} yrs" if r.get("experience_years", "").strip() else "",
        r.get("workshop", "").strip(), r.get("city", "").strip()] if x)
    return f"Mechanic interview: {who}" + (f" ({details})" if details else "") + f", {r['interview_date'].strip()}"


def load(repo, embedder, csv_path: str, replace: bool = False) -> dict:
    from autocare.repository import encode_embedding

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if rows:
        missing = [c for c in REQUIRED if c not in rows[0]]
        if missing:
            raise SystemExit(f"CSV is missing columns: {missing}")

    kept, skipped = [], []
    for r in rows:
        if (r.get("consent") or "").strip().lower() != "yes":
            skipped.append((r.get("note_id"), "no consent recorded"))
        elif not (r.get("advice") or "").strip() or not (r.get("topic") or "").strip():
            skipped.append((r.get("note_id"), "empty topic or advice"))
        elif bool((r.get("model") or "").strip()) != bool((r.get("years") or "").strip()):
            skipped.append((r.get("note_id"), "model and years must both be filled, or both blank"))
        else:
            kept.append(r)

    if replace:
        repo.delete_documents_by_type(MECHANIC_NOTE)

    # group: (interview, vehicle_id or None) -> notes
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in kept:
        interview = (r["mechanic_name"].strip(), r["interview_date"].strip())
        years = parse_years(r["years"])
        if not years:
            groups[(interview, None)].append(r)
            continue
        for y in years:
            vids = repo.find_vehicle_ids(r["manufacturer"], r["model"], y)
            if not vids:
                skipped.append((r["note_id"], f"no VEHICLE row for {r['manufacturer']} {r['model']} {y}"))
                continue
            groups[(interview, vids[0])].append(r)

    texts = [f"{r['topic'].strip()}: {r['advice'].strip()}" for g in groups.values() for r in g]
    vectors = iter(embedder.encode(texts) if texts else [])
    n_docs = n_chunks = 0
    for (interview, vehicle_id), notes in groups.items():
        doc_id = str(uuid.uuid4())
        repo.insert_document({
            "document_id": doc_id, "vehicle_id": vehicle_id,
            "document_name": document_name(notes[0]), "document_type": MECHANIC_NOTE,
            "version": interview[1], "source": "AutoCare AI team interview",
            "license_note": "Recorded with the mechanic's written consent (proposal §9.2)",
            "ingest_date": dt.date.today().isoformat(),
        })
        repo.insert_chunks([{
            "chunk_id": str(uuid.uuid4()), "document_id": doc_id, "section": r["topic"].strip(),
            "page_number": None, "text": f"{r['topic'].strip()}: {r['advice'].strip()}",
            "embedding": encode_embedding(next(vectors)), "chunk_type": MECHANIC_NOTE,
        } for r in notes])
        n_docs += 1
        n_chunks += len(notes)
    return {"documents": n_docs, "notes": n_chunks, "skipped": skipped}


def main() -> None:
    from autocare.config import load_settings
    from autocare.db import Database
    from autocare.ml import build_models
    from autocare.repository import Repository

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--replace", action="store_true",
                    help="delete all previously loaded mechanic notes first (use after editing the CSV)")
    a = ap.parse_args()

    s = load_settings()
    db = Database(s.database_url)
    db.create_schema()
    embedder, _ = build_models(s)
    out = load(Repository(db), embedder, a.csv, a.replace)
    print(f"Loaded {out['notes']} notes into {out['documents']} documents.")
    for note_id, why in out["skipped"]:
        print(f"  skipped {note_id}: {why}")
    print("Restart the API (or POST /api/v1/admin/reindex) to use them.")


if __name__ == "__main__":
    main()
