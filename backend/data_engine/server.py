"""FastAPI Dataset Engineering API & Localhost Dashboard Server for AI Auto Pakistan.

Run directly:
    python -m uvicorn data_engine.server:app --host 127.0.0.1 --port 8090
"""
from __future__ import annotations

import base64
import csv
import datetime as dt
import io
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, Field

from .cleaning import CleaningPipeline, detect_language, normalize_automotive_text
from .config import get_config
from .logger import AuditAction, get_audit_logger
from .media import MediaVault
from .ml import GroupedMLSplitter
from .registry import create_default_source_registry
from .reports import DatasetReportGenerator
from .schema import (
    AutomotiveRecord,
    CostInfo,
    ProblemInfo,
    RepairInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from .sources import (
    AutomotiveBlogImporter,
    FacebookResearchImporter,
    LocalDatasetConsolidator,
    MechanicInterviewImporter,
    OwnerProblemReportImporter,
    PakWheelsResearchImporter,
    YouTubeCollector,
    scrub_pii,
)
from .storage import StorageManager
from .taxonomy import DiagnosisStage, get_taxonomy_manager, normalize_make_model

router = APIRouter(prefix="/api/v1/dataset", tags=["AI Auto Pakistan Data Engine"])

DASHBOARD_HTML_PATH = Path(__file__).parent / "dashboard" / "index.html"


# ---------------------------------------------------------------------------
# Pydantic Request Models
# ---------------------------------------------------------------------------
class NewVehicleRecordIn(BaseModel):
    make: str = Field(..., min_length=1, max_length=60)
    model: str = Field(..., min_length=1, max_length=60)
    variant: Optional[str] = None
    manufacturing_year: Optional[int] = Field(None, ge=1960, le=2027)
    engine_cc: Optional[int] = Field(None, ge=500, le=8000)
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    mileage_km: Optional[int] = Field(None, ge=0, le=2000000)
    problem_title: str = Field(..., min_length=3, max_length=200)
    problem_description: str = Field(..., min_length=3, max_length=4000)
    symptoms: List[str] = Field(default_factory=list)
    fault_category: Optional[str] = None
    severity: Optional[str] = "moderate"
    diagnosis_stage: str = DiagnosisStage.OWNER_REPORTED_PROBLEM.value
    recommended_solution: Optional[str] = None
    required_parts: List[str] = Field(default_factory=list)
    estimated_cost_pkr: Optional[float] = Field(None, ge=0)
    parts_cost_pkr: Optional[float] = Field(None, ge=0)
    labor_cost_pkr: Optional[float] = Field(None, ge=0)
    city: Optional[str] = None
    source_platform: str = "owner_submission"
    source_url: Optional[str] = None
    language: Optional[str] = None
    consent_given: bool = True


class ReviewActionIn(BaseModel):
    status: str = Field(..., description="pending | needs_review | reviewed | approved | ml_ready | rejected")
    reviewer_notes: Optional[str] = None


class YouTubeCollectIn(BaseModel):
    api_key: Optional[str] = None
    queries: Optional[List[str]] = None
    max_results_per_query: int = Field(5, ge=1, le=25)


class CsvImportIn(BaseModel):
    source_type: str = Field(..., description="facebook | pakwheels | mechanic_interview | owner_submission")
    csv_text: str = Field(..., min_length=10)
    filename: Optional[str] = None


class MediaUploadIn(BaseModel):
    filename: str = Field(..., min_length=3, max_length=200)
    asset_type: str = Field(..., description="audio | images | videos")
    content_base64: str = Field(..., min_length=4)
    rights_basis: str = "explicit_consent"
    attribution: str = ""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/health")
def dataset_health() -> Dict[str, Any]:
    config = get_config()
    storage = StorageManager()
    return {
        "status": "ok",
        "service": "AI Auto Pakistan Dataset Engineering Platform",
        "has_youtube_key": bool(config.youtube_api_key or os.getenv("YOUTUBE_API_KEY", "").strip()),
        "has_facebook_token": bool(config.facebook_access_token or os.getenv("FACEBOOK_ACCESS_TOKEN", "").strip()),
        "metadata_only_default": config.metadata_only_default,
        "require_consent": config.require_consent_for_interviews,
        "anonymize_pii": config.anonymize_personal_identifiers,
        "db_path": str(storage.db_path),
    }


@router.get("/stats")
def dataset_stats() -> Dict[str, Any]:
    config = get_config()
    storage = StorageManager()
    stats = storage.get_dataset_statistics()
    audit_summary = get_audit_logger().get_summary()

    raw_counts = {}
    for sub in ["youtube", "facebook", "pakwheels", "mechanic_notes", "owner_reports", "manuals"]:
        p = config.raw_dir / sub
        raw_counts[sub] = len(list(p.glob("*"))) if p.exists() else 0

    real_src = stats["real_by_source"]
    all_src = stats["by_source"]

    return {
        "summary": {
            "total_records_in_db": stats["total_records"],
            "real_collected_records": stats["real_records_count"],
            "example_template_records": stats["example_records_count"],
            "youtube_records": real_src.get("youtube_official_api", 0),
            "facebook_real_records": real_src.get("facebook_research_import", 0),
            "pakwheels_real_records": real_src.get("pakwheels_research_import", 0),
            "blogs_real_records": real_src.get("automotive_blog_research", 0),
            "mechanic_real_records": real_src.get("mechanic_interviews", 0),
            "owner_real_records": real_src.get("owner_submissions", 0),
            "manuals_and_obd2_records": real_src.get("manuals_and_bulletins", 0),
            "symptom_corpus_records": real_src.get("starter_symptom_corpus", 0),
            "price_reference_records": real_src.get("pakistan_price_reference", 0),
            "total_vehicles_in_fleet": stats["total_vehicles_in_fleet"],
            "distinct_vehicle_models_covered": stats["distinct_vehicle_models_covered"],
            "fault_categories_covered": stats["fault_categories_covered"],
            "total_fault_categories": 18,
            "audio_samples": stats["media_counts"]["audio"],
            "image_samples": stats["media_counts"]["images"],
            "video_samples": stats["media_counts"]["videos"],
            "video_metadata_records": stats["media_counts"]["video_metadata_records"],
            "transcribed_records": stats["media_counts"]["transcribed"],
            "reviewed_records": stats["reviewed_count"],
            "ml_ready_records": stats["ml_ready_count"],
            "audit_events_logged": audit_summary["total_audit_events"],
        },
        "breakdowns": {
            "real_by_source": real_src,
            "all_by_source": all_src,
            "by_category": stats["by_category"],
            "by_make": stats["by_make"],
            "by_model": stats["by_model"],
            "by_language": stats["by_language"],
            "by_review_status": stats["by_review_status"],
            "raw_files_by_source": raw_counts,
        },
        "api_credentials": {
            "youtube_configured": bool(config.youtube_api_key or os.getenv("YOUTUBE_API_KEY", "").strip()),
            "facebook_configured": bool(config.facebook_access_token or os.getenv("FACEBOOK_ACCESS_TOKEN", "").strip()),
        },
    }


@router.get("/records")
def list_records(
    make: Optional[str] = None,
    model: Optional[str] = None,
    source: Optional[str] = None,
    category: Optional[str] = None,
    language: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
    include_examples: bool = True,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    storage = StorageManager()
    items, total = storage.query_records(
        make=make,
        model=model,
        source_id=source,
        category_id=category,
        language=language,
        status=status,
        search_text=q,
        include_examples=include_examples,
        limit=limit,
        offset=offset,
    )
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.post("/records")
def create_record(body: NewVehicleRecordIn) -> Dict[str, Any]:
    if body.source_platform in {"mechanic_interview", "owner_submission"} and not body.consent_given:
        raise HTTPException(status_code=422, detail="Explicit consent is required for field submissions.")

    make, model = normalize_make_model(body.make, body.model)
    make = make or body.make.strip().title()
    model = model or body.model.strip().title()

    clean_title = normalize_automotive_text(scrub_pii(body.problem_title))
    clean_desc = normalize_automotive_text(scrub_pii(body.problem_description))
    clean_solution = normalize_automotive_text(scrub_pii(body.recommended_solution)) if body.recommended_solution else None
    clean_symptoms = [normalize_automotive_text(scrub_pii(s)) for s in body.symptoms if s.strip()]

    lang = body.language or detect_language(f"{clean_title} {clean_desc}")
    cat_id = body.fault_category
    if not cat_id:
        matched = get_taxonomy_manager().match_category_from_text(f"{clean_title} {clean_desc} {' '.join(clean_symptoms)}")
        cat_id = matched.category_id if matched else None

    record = AutomotiveRecord(
        vehicle=VehicleInfo(
            make=make,
            model=model,
            variant=body.variant,
            manufacturing_year=body.manufacturing_year,
            engine_cc=body.engine_cc,
            fuel_type=body.fuel_type,
            transmission=body.transmission,
            mileage_km=body.mileage_km,
        ),
        problem=ProblemInfo(
            problem_title=clean_title,
            problem_description=clean_desc,
            symptoms=clean_symptoms or [clean_title],
            fault_category=cat_id,
            severity=body.severity,
            diagnosis_stage=body.diagnosis_stage,
        ),
        repair=RepairInfo(
            recommended_solution=clean_solution,
            required_parts=body.required_parts,
        ) if clean_solution or body.required_parts else None,
        cost=CostInfo(
            estimated_cost_pkr=body.estimated_cost_pkr,
            parts_cost_pkr=body.parts_cost_pkr,
            labor_cost_pkr=body.labor_cost_pkr,
            city=body.city,
            price_date=dt.date.today().isoformat(),
            price_source=body.source_platform,
        ) if body.estimated_cost_pkr is not None or body.city else None,
        source=SourceQualityInfo(
            source_platform=body.source_platform,
            source_url=body.source_url,
            source_id=f"ui_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d%H%M%S')}",
            language=lang,
            rights_basis="user_submission" if body.source_platform == "owner_submission" else "explicit_consent",
            permission_status="consent_signed",
            human_review_status="pending",
            confidence_score=0.75,
        ),
    )

    storage = StorageManager()
    storage.insert_record(record)
    get_audit_logger().log(
        AuditAction.RECORD_INGESTED,
        source_id=body.source_platform,
        record_id=record.record_id,
        status="SUCCESS",
        details={"via": "localhost_dashboard_form", "vehicle": f"{make} {model}", "category": cat_id},
    )
    return {"status": "created", "record_id": record.record_id, "record": record.model_dump()}


@router.post("/records/{record_id}/review")
def review_record(record_id: str, body: ReviewActionIn) -> Dict[str, Any]:
    storage = StorageManager()
    try:
        updated = storage.update_review_status(record_id, body.status, body.reviewer_notes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Record '{record_id}' not found.")
    return {"status": "updated", "record": updated}


@router.get("/categories")
def list_categories() -> Dict[str, Any]:
    storage = StorageManager()
    cats = storage.get_fault_categories_with_counts()
    return {"total": len(cats), "categories": cats}


@router.get("/vehicles")
def list_vehicles(make: Optional[str] = None) -> Dict[str, Any]:
    storage = StorageManager()
    vehicles = storage.get_fleet_vehicles(make=make)
    return {"total": len(vehicles), "vehicles": vehicles}


@router.get("/costs")
def list_costs(make: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    storage = StorageManager()
    items = storage.get_cost_records(make=make, model=model)
    return {"total": len(items), "items": items}


@router.get("/sources")
def list_sources() -> Dict[str, Any]:
    registry = create_default_source_registry()
    storage = StorageManager()
    stats = storage.get_dataset_statistics()
    out = []
    for s in registry.list_all():
        d = s.to_dict()
        d["real_records_count"] = stats["real_by_source"].get(s.source_id, 0)
        d["total_records_count"] = stats["by_source"].get(s.source_id, 0)
        out.append(d)
    return {"total": len(out), "sources": out}


@router.get("/queries")
def list_queries() -> Dict[str, Any]:
    collector = YouTubeCollector()
    queries = collector.load_search_queries()
    return {"total": len(queries), "queries": queries}


@router.get("/ml-splits")
def get_ml_splits() -> Dict[str, Any]:
    config = get_config()
    card_path = config.ml_ready_dir / "dataset_card.json"
    card = {}
    if card_path.exists():
        with open(card_path, "r", encoding="utf-8") as f:
            card = json.load(f)

    samples = {}
    for split in ["train", "val", "test"]:
        p = config.ml_ready_dir / f"{split}.jsonl"
        rows = []
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    if idx >= 5:
                        break
                    if line.strip():
                        rows.append(json.loads(line))
        samples[split] = rows
    return {"dataset_card": card, "preview_samples": samples}


@router.get("/audit-logs")
def get_audit_logs(limit: int = Query(100, ge=1, le=500)) -> Dict[str, Any]:
    logger = get_audit_logger()
    events = []
    if logger.log_path.exists():
        with open(logger.log_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        for line in reversed(lines[-limit:]):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return {"summary": logger.get_summary(), "recent_events": events}


@router.post("/collect/youtube")
def collect_youtube(body: YouTubeCollectIn) -> Dict[str, Any]:
    config = get_config()
    key = (body.api_key or config.youtube_api_key or os.getenv("YOUTUBE_API_KEY", "")).strip()
    if not key:
        raise HTTPException(
            status_code=400,
            detail="YouTube API key not configured. Enter your Google Cloud YouTube Data API v3 key or set YOUTUBE_API_KEY in backend/.env.",
        )

    collector = YouTubeCollector(api_key=key)
    queries_to_run = body.queries or [q["query"] for q in collector.load_search_queries()[:3]]
    if not queries_to_run:
        raise HTTPException(status_code=400, detail="No search queries provided.")

    all_raw: List[Dict[str, Any]] = []
    raw_files: List[str] = []
    try:
        for q in queries_to_run:
            items = collector.fetch_video_metadata(q, max_results=body.max_results_per_query)
            if items:
                raw_path = collector.save_raw_batch(q, items)
                raw_files.append(str(raw_path))
                all_raw.extend(items)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"YouTube API request failed: {exc}")

    records = collector.to_automotive_records(all_raw)
    clean_summary = CleaningPipeline().process_batch(records) if records else {"unique_processed": 0}
    StorageManager().insert_records(records)

    return {
        "status": "completed",
        "queries_executed": queries_to_run,
        "raw_records_fetched": len(all_raw),
        "raw_files_saved": raw_files,
        "cleaning_summary": clean_summary,
        "items": all_raw[:25],
    }


@router.post("/import/csv")
def import_research_csv(body: CsvImportIn) -> Dict[str, Any]:
    config = get_config()
    src = body.source_type.strip().lower()
    sub_map = {
        "facebook": ("facebook", FacebookResearchImporter().import_manual_csv),
        "pakwheels": ("pakwheels", PakWheelsResearchImporter().import_manual_csv),
        "automotive_blog": ("pakwheels", AutomotiveBlogImporter().import_manual_csv),
        "mechanic_interview": ("mechanic_notes", MechanicInterviewImporter().import_csv),
        "owner_submission": ("owner_reports", OwnerProblemReportImporter().import_csv),
    }
    if src not in sub_map:
        raise HTTPException(status_code=422, detail=f"Unsupported source_type '{src}'.")

    raw_subdir, loader_fn = sub_map[src]
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest_raw = config.raw_dir / raw_subdir / f"import_{ts}.csv"
    dest_raw.parent.mkdir(parents=True, exist_ok=True)
    dest_raw.write_text(body.csv_text, encoding="utf-8")

    try:
        records = loader_fn(dest_raw)
    except Exception as exc:
        dest_raw.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(exc))

    clean_summary = CleaningPipeline().process_batch(records) if records else {"unique_processed": 0}
    StorageManager().insert_records(records)

    return {
        "status": "imported",
        "source_type": src,
        "raw_file": str(dest_raw),
        "records_imported": len(records),
        "cleaning_summary": clean_summary,
    }


@router.post("/media/upload")
def upload_authorized_media(body: MediaUploadIn) -> Dict[str, Any]:
    try:
        raw_bytes = base64.b64decode(body.content_base64)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid base64 media payload.")

    if len(raw_bytes) > 15_000_000:
        raise HTTPException(status_code=413, detail="Media file exceeds 15 MB prototype upload limit.")

    suffix = Path(body.filename).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(raw_bytes)
        tmp_path = Path(tmp.name)

    try:
        vault = MediaVault()
        asset = vault.store_asset(
            source_file=tmp_path,
            asset_type=body.asset_type,
            rights_basis=body.rights_basis,
            attribution=body.attribution,
        )
        asset_id = StorageManager().register_media_asset(asset, body.asset_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        tmp_path.unlink(missing_ok=True)

    return {"status": "stored", "asset_id": asset_id, "asset": asset}


@router.post("/pipeline/consolidate")
def run_consolidation_pipeline() -> Dict[str, Any]:
    return LocalDatasetConsolidator().consolidate_all(include_examples=True)


@router.post("/pipeline/split")
def run_ml_split() -> Dict[str, Any]:
    storage = StorageManager()
    items, _ = storage.query_records(include_examples=False, limit=10000)
    recs: List[AutomotiveRecord] = []
    for it in items:
        recs.append(
            AutomotiveRecord(
                record_id=it["record_id"],
                vehicle=VehicleInfo(
                    make=it.get("make") or "Unknown",
                    model=it.get("model") or "Unknown",
                    variant=it.get("variant"),
                    manufacturing_year=it.get("manufacturing_year"),
                ),
                problem=ProblemInfo(
                    problem_title=it["problem_title"],
                    problem_description=it["problem_description"],
                    symptoms=it.get("symptoms", []),
                    fault_category=it.get("fault_category_id"),
                    severity=it.get("severity"),
                    diagnosis_stage=it.get("diagnosis_stage", "owner_reported_problem"),
                ),
                cost=CostInfo(
                    estimated_cost_pkr=it.get("estimated_cost_pkr"),
                    parts_cost_pkr=it.get("parts_cost_pkr"),
                    labor_cost_pkr=it.get("labor_cost_pkr"),
                    city=it.get("city"),
                    price_date=it.get("price_date"),
                    price_source=it.get("price_source"),
                ) if it.get("estimated_cost_pkr") is not None else None,
                source=SourceQualityInfo(
                    source_platform=it.get("source_id") or "unknown",
                    source_url=it.get("source_url"),
                    source_id=it["record_id"],
                    language=it.get("language") or "en",
                    rights_basis=it.get("rights_basis") or "unknown",
                    permission_status="verified",
                    human_review_status=it.get("human_review_status") or "pending",
                    confidence_score=it.get("confidence_score") or 0.5,
                ),
            )
        )
    splitter = GroupedMLSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    train, val, test = splitter.split_records(recs)
    outputs = splitter.export_splits(train, val, test)
    report_path = DatasetReportGenerator(storage=storage).export_markdown_report()
    return {
        "total_real_records": len(recs),
        "train": len(train),
        "val": len(val),
        "test": len(test),
        "outputs": outputs,
        "report_path": str(report_path),
    }


@router.get("/templates/{template_name}")
def download_template(template_name: str):
    allowed = {
        "facebook_research_template.csv",
        "pakwheels_research_template.csv",
        "automotive_blogs_research_template.csv",
        "mechanic_interview_template.csv",
        "owner_problem_report_template.csv",
    }
    if template_name not in allowed:
        raise HTTPException(status_code=404, detail="Template not found")
    path = get_config().templates_dir / template_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Template file missing on disk")
    return FileResponse(path, media_type="text/csv", filename=template_name)


@router.get("/export/{fmt}")
def export_dataset(fmt: str):
    fmt = fmt.lower().strip()
    if fmt not in {"csv", "json", "jsonl"}:
        raise HTTPException(status_code=422, detail="Format must be csv, json, or jsonl")

    items, _ = StorageManager().query_records(include_examples=False, limit=10000)
    if fmt == "json":
        return Response(
            content=json.dumps(items, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=ai_auto_pakistan_dataset.json"},
        )
    if fmt == "jsonl":
        content = "\n".join(json.dumps(it, ensure_ascii=False) for it in items)
        return Response(
            content=content,
            media_type="application/x-ndjson",
            headers={"Content-Disposition": "attachment; filename=ai_auto_pakistan_dataset.jsonl"},
        )

    # CSV
    buf = io.StringIO()
    if items:
        cols = [
            "record_id", "make", "model", "variant", "manufacturing_year",
            "fault_category_id", "category_name", "problem_title", "problem_description",
            "symptoms", "severity", "diagnosis_stage", "recommended_solution",
            "estimated_cost_pkr", "parts_cost_pkr", "labor_cost_pkr", "city",
            "source_id", "source_url", "language", "rights_basis", "human_review_status",
            "confidence_score", "collection_date",
        ]
        writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for it in items:
            row = dict(it)
            row["symptoms"] = "; ".join(it.get("symptoms") or [])
            writer.writerow(row)
    return Response(
        content=buf.getvalue().encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ai_auto_pakistan_dataset.csv"},
    )


# ---------------------------------------------------------------------------
# Standalone FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Auto Pakistan — Multi-Source Dataset Engineering Platform",
    version="2.0.0",
    description="Collect, normalize, review, audit, and prepare Pakistani automotive datasets for AI/ML.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/", include_in_schema=False)
def serve_dashboard():
    if not DASHBOARD_HTML_PATH.exists():
        return HTMLResponse("<h1>AI Auto Pakistan Data Engine API</h1><p>Open <a href='/docs'>/docs</a> for API documentation.</p>")
    return HTMLResponse(DASHBOARD_HTML_PATH.read_text(encoding="utf-8"))
