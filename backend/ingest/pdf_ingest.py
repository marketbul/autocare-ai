"""Minimal L1 ingestion for an owner's manual PDF, so Story 2 can run end to end.

Structure-aware chunking (proposal §6.2): new chunk at every heading and at
every WARNING / CAUTION / NOTICE box; tables become their own chunks; long
sections split on line boundaries. Every chunk keeps section path + page.

This is a working baseline for the Data & Retrieval lead to replace or refine,
not the final L1 pipeline.

Usage:
  python -m ingest.pdf_ingest --pdf corolla_2018_om.pdf --manufacturer Toyota \
      --model Corolla --years 2018 --document-name "Corolla 2018 Owner's Manual" \
      --source "toyota.com.pk" --license-note "Manufacturer owner's manual, consumer reference" \
      --page-offset 0
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import statistics
import uuid
from dataclasses import dataclass, field

import pdfplumber

MAX_CHARS = 1800
_WARN = re.compile(r"^\s*(WARNING|CAUTION|NOTICE|DANGER)\b", re.I)
_STEP = re.compile(r"^\s*(\d{1,2}[.)]|STEP\s+\d+)\s+", re.I)


@dataclass
class Line:
    text: str
    size: float
    page: int


@dataclass
class Chunk:
    section: str
    page_number: int
    chunk_type: str
    lines: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return clean_text("\n".join(self.lines))


_BULLETS = re.compile(r"[\u25a0-\u25ff\u2022\u25cf\uf06e\uf0a7\uf0b7]")   # ■ ● • and Wingdings bullets


def clean_text(t: str) -> str:
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)      # "peri-\nods" -> "periods"
    t = re.sub(r"(\w)- (\w)", r"\1\2", t)               # "peri- ods" on one line
    t = _BULLETS.sub("\n- ", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def _page_lines(page, page_no: int, margin: float) -> list[Line]:
    """Words -> lines, excluding header/footer bands and table regions."""
    tables = page.find_tables()
    bboxes = [t.bbox for t in tables]
    top_cut, bottom_cut = page.height * margin, page.height * (1 - margin)
    words = page.extract_words(extra_attrs=["size"], use_text_flow=True, keep_blank_chars=False)
    rows: dict[int, list[dict]] = {}
    for w in words:
        if w["top"] < top_cut or w["bottom"] > bottom_cut:
            continue
        cx, cy = (w["x0"] + w["x1"]) / 2, (w["top"] + w["bottom"]) / 2
        if any(x0 <= cx <= x1 and t <= cy <= b for x0, t, x1, b in bboxes):
            continue
        rows.setdefault(round(w["top"] / 3), []).append(w)
    lines = []
    for key in sorted(rows):
        ws = sorted(rows[key], key=lambda w: w["x0"])
        text = " ".join(w["text"] for w in ws).strip()
        if text:
            lines.append(Line(text, max(w["size"] for w in ws), page_no))
    return lines


def _table_chunks(page, page_no: int, section: str) -> list[Chunk]:
    out = []
    for t in page.find_tables():
        rows = [" | ".join((c or "").strip() for c in r) for r in t.extract() if any(r)]
        if rows:
            out.append(Chunk(section, page_no, "table", rows))
    return out


def chunk_pdf(path: str, page_offset: int = 0, margin: float = 0.05) -> list[Chunk]:
    """page_offset: printed page = physical page - page_offset (so citations match
    the page numbers printed in the manual)."""
    with pdfplumber.open(path) as pdf:
        per_page = [(_page_lines(p, i + 1, margin), p, i + 1) for i, p in enumerate(pdf.pages)]
        sizes = [ln.size for lines, _, _ in per_page for ln in lines]
        if not sizes:
            return []  # scanned PDF: needs OCR first
        body = statistics.median(sizes)
        heading_sizes = sorted({round(s, 1) for s in sizes if s >= body * 1.15}, reverse=True)
        level = {s: i for i, s in enumerate(heading_sizes)}

        chunks: list[Chunk] = []
        path_stack: list[tuple[int, str]] = []   # (heading level, heading text)
        cur: Chunk | None = None

        def section() -> str:
            return " > ".join(t for _, t in path_stack[-2:]) if path_stack else "Front matter"

        def start(kind: str, page: int) -> Chunk:
            nonlocal cur
            if cur and cur.text:
                chunks.append(cur)
            cur = Chunk(section(), page - page_offset, kind)
            return cur

        for lines, page, page_no in per_page:
            for ln in lines:
                size = round(ln.size, 1)
                if size in level and len(ln.text) <= 120:
                    lv = level[size]
                    while path_stack and path_stack[-1][0] >= lv:
                        path_stack.pop()
                    path_stack.append((lv, ln.text))
                    start("narrative", page_no)
                    continue
                if _WARN.match(ln.text):
                    start("warning", page_no)
                elif cur is None:
                    start("narrative", page_no)
                elif cur.chunk_type == "warning" and len(cur.text) > 600:
                    start("narrative", page_no)
                if len(cur.text) + len(ln.text) > MAX_CHARS:
                    start(cur.chunk_type, page_no)
                cur.lines.append(ln.text)
            for tc in _table_chunks(page, page_no, section()):
                tc.page_number = page_no - page_offset
                chunks.append(tc)
        if cur and cur.text:
            chunks.append(cur)

    for c in chunks:
        if c.chunk_type == "narrative" and sum(bool(_STEP.match(l)) for l in c.lines) >= 2:
            c.chunk_type = "procedure"
    return [c for c in chunks if len(c.text) >= 30]


def parse_years(spec: str) -> list[int]:
    if "-" in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(y) for y in spec.split(",")]


def main() -> None:
    from autocare.config import load_settings
    from autocare.db import Database
    from autocare.ml import build_models
    from autocare.repository import Repository, encode_embedding

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--manufacturer", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--years", required=True,
                    help="Model year(s) this manual covers: 2018, or 2014-2016, or 2017,2018. "
                         "One Document row is created per year (schema has one vehicle per document).")
    ap.add_argument("--document-name", required=True)
    ap.add_argument("--document-type", default="owner_manual")
    ap.add_argument("--version", default=None)
    ap.add_argument("--source", required=True)
    ap.add_argument("--license-note", required=True)
    ap.add_argument("--page-offset", type=int, default=0)
    args = ap.parse_args()

    settings = load_settings()
    db = Database(settings.database_url)
    db.create_schema()
    repo = Repository(db)
    embedder, _ = build_models(settings)

    chunks = chunk_pdf(args.pdf, args.page_offset)
    if not chunks:
        raise SystemExit("No text extracted. Is the PDF scanned? Run OCR first.")
    vectors = embedder.encode([f"{c.section}\n{c.text}" for c in chunks])
    print(f"{len(chunks)} chunks from {args.pdf}")

    for year in parse_years(args.years):
        vids = repo.find_vehicle_ids(args.manufacturer, args.model, year)
        if not vids:
            raise SystemExit(f"No VEHICLE row for {args.manufacturer} {args.model} {year}. "
                             f"Run ingest.seed_vehicles first.")
        doc_id = str(uuid.uuid4())
        repo.insert_document({
            "document_id": doc_id, "vehicle_id": vids[0], "document_name": args.document_name,
            "document_type": args.document_type, "version": args.version, "source": args.source,
            "license_note": args.license_note, "ingest_date": dt.date.today().isoformat(),
        })
        repo.insert_chunks([
            {"chunk_id": str(uuid.uuid4()), "document_id": doc_id, "section": c.section,
             "page_number": c.page_number, "text": c.text,
             "embedding": encode_embedding(v), "chunk_type": c.chunk_type}
            for c, v in zip(chunks, vectors)
        ])
        print(f"  -> document {doc_id} for {args.manufacturer} {args.model} {year}")
    print("Done. Restart the API or POST /api/v1/admin/reindex.")


if __name__ == "__main__":
    main()
