"""L5 FastAPI service: diagnostic questions (Story 2) plus sign-in and role-based screens.

Run:  python -m uvicorn autocare.api:app --reload

Roles (see auth.py):
  owner     /me/*  and  /diagnose/query (only for vehicles in their own garage)
  mechanic  /mechanic/*  (submitted notes wait for admin approval)
  admin     /admin/*
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .accounts import Accounts, Forbidden, Invalid, NotFound
from .auth import ROLES, make_token, read_token
from .config import load_settings, triage_data_path
from .db import Database
from .generation import build_generator
from .ml import build_models
from .repository import Repository
from .retrieval import Retriever
import logging

from .damage import MAX_PHOTOS, DamageService, build_damage_assessor
from .scan import ImageRejected, build_code_reader, friendly_provider_error, read_codes
from .schemas import (DiagnoseRequest, DiagnoseResponse, ErrorResponse,
                      HealthIndexResponse, NextServiceResponse,
                      RootCauseRequest, RootCauseResponse,
                      SimilarCasesRequest, SimilarCasesResponse,
                      VerifyRepairRequest, VerifyRepairResponse)
from .triage import TriageClassifier, load_or_train
from .service import (DiagnoseError, DiagnoseService, GenerationFailed, UnsupportedVehicle,
                      VehicleProfileRequired)

STATUS = {VehicleProfileRequired: 428, UnsupportedVehicle: 422, GenerationFailed: 502}


def build_service(settings=None) -> tuple[DiagnoseService, Accounts]:
    settings = settings or load_settings()
    db = Database(settings.database_url)
    db.create_schema()          # idempotent (CREATE ... IF NOT EXISTS)
    repo = Repository(db)
    embedder, reranker = build_models(settings)
    retriever = Retriever(repo, embedder, reranker, settings)
    emb_name = settings.embedding_model if settings.ml_backend == "models" else "lite"
    triage_model = load_or_train(settings.triage_model_path, triage_data_path(settings), embedder, emb_name)
    service = DiagnoseService(repo, retriever, build_generator(settings), reranker, settings,
                              triage=TriageClassifier(triage_model, embedder))
    service.code_reader = build_code_reader(settings)
    assessor = build_damage_assessor(settings)
    service.damage = DamageService(db, repo, assessor, settings.max_image_bytes) if assessor else None
    return service, Accounts(db, settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service, app.state.accounts = build_service()   # loads models once
    yield


settings = load_settings()
app = FastAPI(title="AutoCare AI", version="0.2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
                   allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["*"])


# ---------------------------------------------------------------- errors
@app.exception_handler(DiagnoseError)
async def _diagnose_error(_: Request, exc: DiagnoseError):
    body = ErrorResponse(error=exc.code, message=exc.message, language=exc.language)
    return JSONResponse(status_code=STATUS.get(type(exc), 400), content=body.model_dump())


@app.exception_handler(Invalid)
async def _invalid(_: Request, exc: Invalid):
    return JSONResponse(status_code=422, content={"error": "invalid", "message": str(exc)})


@app.exception_handler(NotFound)
async def _not_found(_: Request, exc: NotFound):
    return JSONResponse(status_code=404, content={"error": "not_found", "message": str(exc)})


@app.exception_handler(Forbidden)
async def _forbidden(_: Request, exc: Forbidden):
    return JSONResponse(status_code=403, content={"error": "forbidden", "message": str(exc)})


# ---------------------------------------------------------------- auth helpers
def accounts(request: Request) -> Accounts:
    return request.app.state.accounts


def current_user(request: Request, authorization: Optional[str] = Header(None)) -> dict:
    token = (authorization or "").removeprefix("Bearer ").strip()
    data = read_token(token) if token else None
    user = accounts(request).get_user(data["sub"]) if data else None
    if not user:
        raise HTTPException(401, detail={"error": "signed_out", "message": "Please sign in again."})
    return user          # role is read fresh from the database, not trusted from the token


def require(*roles: str):
    def check(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(403, detail={"error": "forbidden",
                                             "message": "Your account doesn't have access to this page."})
        return user
    return check


# ---------------------------------------------------------------- public
class SignUp(BaseModel):
    full_name: str = Field(..., max_length=120)
    email: str = Field(..., max_length=200)
    password: str = Field(..., max_length=200)


class SignIn(BaseModel):
    email: str
    password: str


def _session(user: dict) -> dict:
    return {"token": make_token(user["user_id"], user["role"]), "user": user}


@app.get("/api/v1/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/auth/register")
async def register(body: SignUp, request: Request) -> dict:
    return _session(accounts(request).register_owner(body.full_name, body.email, body.password))


@app.post("/api/v1/auth/login")
async def login(body: SignIn, request: Request) -> dict:
    user = await run_in_threadpool(accounts(request).authenticate, body.email, body.password)
    if not user:
        raise HTTPException(401, detail={"error": "bad_login", "message": "Email or password is incorrect."})
    return _session(user)


@app.get("/api/v1/auth/me")
async def me(user: dict = Depends(current_user)) -> dict:
    return user


# ---------------------------------------------------------------- owner
class NewVehicle(BaseModel):
    vehicle_id: str
    current_mileage: Optional[int] = None
    registration_year: Optional[int] = None
    usage_profile: Optional[str] = None


class VehicleUpdate(BaseModel):
    current_mileage: Optional[int] = None
    correction: bool = False          # allow a lower reading (typo fix)
    usage_profile: Optional[str] = None


class Photo(BaseModel):
    image: str = Field(..., max_length=9_000_000, description="data:image/jpeg;base64,...")
    language: str = "en"


@app.get("/api/v1/catalog/vehicles")
async def catalog(request: Request, user: dict = Depends(current_user)) -> list[dict]:
    return accounts(request).catalog()


@app.get("/api/v1/me/vehicles")
async def my_vehicles(request: Request, user: dict = Depends(require("owner", "admin"))) -> list[dict]:
    return accounts(request).my_vehicles(user["user_id"])


@app.post("/api/v1/me/vehicles")
async def add_vehicle(body: NewVehicle, request: Request, user: dict = Depends(require("owner", "admin"))) -> dict:
    return accounts(request).add_vehicle(user["user_id"], body.vehicle_id, body.current_mileage,
                                         body.registration_year, body.usage_profile)


@app.patch("/api/v1/me/vehicles/{user_vehicle_id}")
async def update_vehicle(user_vehicle_id: str, body: VehicleUpdate, request: Request,
                         user: dict = Depends(require("owner", "admin"))) -> dict:
    return accounts(request).update_vehicle(user["user_id"], user_vehicle_id, mileage=body.current_mileage,
                                            correction=body.correction, usage_profile=body.usage_profile)


@app.get("/api/v1/me/cases")
async def my_cases(request: Request, user: dict = Depends(require("owner", "admin"))) -> list[dict]:
    return accounts(request).my_cases(user["user_id"])


@app.post(
    "/api/v1/diagnose/query",
    response_model=DiagnoseResponse,
    responses={428: {"model": ErrorResponse, "description": "No active vehicle profile (AC0)"},
               422: {"model": ErrorResponse, "description": "Vehicle not supported"},
               502: {"model": ErrorResponse, "description": "LLM provider error"}},
)
async def diagnose_query(body: DiagnoseRequest, request: Request,
                         user: dict = Depends(require("owner", "admin"))) -> DiagnoseResponse:
    if body.user_vehicle_id and not accounts(request).owns_vehicle(user["user_id"], body.user_vehicle_id):
        raise Forbidden("That vehicle is not in your garage.")
    service: DiagnoseService = request.app.state.service
    # Retrieval + model inference are CPU-bound / blocking: keep them off the event loop.
    return await run_in_threadpool(service.diagnose, body.user_vehicle_id, body.query, body.code_source)


@app.post("/api/v1/diagnose/read-code")
async def read_code(body: Photo, request: Request, user: dict = Depends(require("owner", "admin"))) -> dict:
    """Story 3: read fault codes from a scanner photo. The photo is not stored."""
    service: DiagnoseService = request.app.state.service
    reader = getattr(service, "code_reader", None)
    if reader is None:
        raise HTTPException(503, detail={"error": "reader_off",
                                         "message": "Reading codes from photos is not set up on this server. Type the code instead."})
    lang = body.language if body.language in ("en", "ur", "roman_ur") else "en"
    try:
        return await run_in_threadpool(read_codes, reader, service.repo, body.image,
                                       service.s.max_image_bytes, lang)
    except ImageRejected as exc:
        raise Invalid(str(exc))
    except Exception as exc:   # provider / OCR failure: ask the owner to type instead
        logging.getLogger("autocare.api").exception("code photo read failed")
        raise HTTPException(502, detail={"error": "reader_failed",
                                         "message": friendly_provider_error(exc) + " You can type the code instead."})


class DamagePhotos(BaseModel):
    user_vehicle_id: Optional[str] = None
    images: list[str] = Field(..., min_length=1, max_length=MAX_PHOTOS)
    note: str = Field("", max_length=1000)
    language: str = "en"


@app.post("/api/v1/damage/assess")
async def assess_damage(body: DamagePhotos, request: Request, user: dict = Depends(require("owner", "admin"))) -> dict:
    """Story 12 / M10: severity + body area of visible damage. Photos are not stored."""
    service: DiagnoseService = request.app.state.service
    if getattr(service, "damage", None) is None:
        raise HTTPException(503, detail={"error": "assessor_off",
                                         "message": "Damage photo checks are not set up on this server."})
    if not body.user_vehicle_id or not accounts(request).owns_vehicle(user["user_id"], body.user_vehicle_id):
        raise HTTPException(428, detail={"error": "vehicle_profile_required",
                                         "message": "Choose one of your cars first."})
    lang = body.language if body.language in ("en", "ur", "roman_ur") else "en"
    try:
        return await run_in_threadpool(service.damage.assess, body.user_vehicle_id, body.images, body.note, lang)
    except ImageRejected as exc:
        raise Invalid(str(exc))
    except ValueError as exc:
        raise Invalid(str(exc))
    except Exception as exc:
        logging.getLogger("autocare.api").exception("damage assessment failed")
        raise HTTPException(502, detail={"error": "assessor_failed", "message": friendly_provider_error(exc)})


# ---------------------------------------------------------------- intelligent modules (M5-M9)
@app.post("/api/v1/diagnose/verify-repair", response_model=VerifyRepairResponse)
async def verify_repair(body: VerifyRepairRequest, request: Request,
                        user: dict = Depends(require("owner", "admin"))) -> dict:
    """Story 7 / M5: Verify workshop recommendation against symptoms, DTC, manual & KG."""
    service: DiagnoseService = request.app.state.service
    return await run_in_threadpool(service.verify_repair, body.user_vehicle_id, body.proposed_repair,
                                   body.symptoms, body.code, body.damage_location)


@app.post("/api/v1/diagnose/root-cause", response_model=RootCauseResponse)
async def root_cause(body: RootCauseRequest, request: Request,
                     user: dict = Depends(require("owner", "admin"))) -> dict:
    """Story 8 / M6: Multi-hop root-cause causal chain inference."""
    service: DiagnoseService = request.app.state.service
    chains = await run_in_threadpool(service.get_root_causes, body.symptom, body.max_depth)
    return {"symptom": body.symptom, "chains": chains}


@app.post("/api/v1/diagnose/similar-cases", response_model=SimilarCasesResponse)
async def similar_cases(body: SimilarCasesRequest, request: Request,
                        user: dict = Depends(require("owner", "admin"))) -> dict:
    """Story 9 / M8: Find prior resolved cases matching vehicle and symptoms."""
    service: DiagnoseService = request.app.state.service
    cases = await run_in_threadpool(service.get_similar_cases, body.user_vehicle_id, body.symptom,
                                    body.code, body.top_k)
    return {"cases": cases}


@app.get("/api/v1/vehicle/{user_vehicle_id}/health", response_model=HealthIndexResponse)
async def vehicle_health(user_vehicle_id: str, request: Request,
                         user: dict = Depends(require("owner", "admin"))) -> dict:
    """Story 10 / M7.1: Vehicle Health Index across 6 component groups."""
    service: DiagnoseService = request.app.state.service
    return await run_in_threadpool(service.get_vehicle_health, user_vehicle_id)


@app.get("/api/v1/vehicle/{user_vehicle_id}/maintenance-prediction", response_model=NextServiceResponse)
async def maintenance_prediction(user_vehicle_id: str, request: Request,
                                 user: dict = Depends(require("owner", "admin"))) -> dict:
    """Story 11 / M7.2: Predict next due service item and mileage window."""
    service: DiagnoseService = request.app.state.service
    return await run_in_threadpool(service.predict_next_service, user_vehicle_id)


class ReportPdfRequest(BaseModel):
    user_vehicle_id: str
    query: str
    diagnosis: DiagnoseResponse


@app.post("/api/v1/diagnose/report/pdf")
async def download_report_pdf(body: ReportPdfRequest, request: Request,
                              user: dict = Depends(require("owner", "admin"))):
    """Story 13 / M9: Downloadable PDF service report."""
    service: DiagnoseService = request.app.state.service
    pdf_bytes = await run_in_threadpool(service.generate_report_pdf, body.user_vehicle_id,
                                        body.query, body.diagnosis)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=autocare-report-{body.diagnosis.case_id or 'export'}.pdf"}
    )


# ---------------------------------------------------------------- mechanic
class NoteIn(BaseModel):
    topic: str = Field(..., max_length=120)
    advice: str = Field(..., max_length=1500)
    manufacturer: str = ""
    model: str = ""
    years: str = ""
    experience_years: str = ""
    workshop: str = ""
    city: str = ""
    consent: bool = False


@app.post("/api/v1/mechanic/notes")
async def submit_note(body: NoteIn, request: Request, user: dict = Depends(require("mechanic", "admin"))) -> dict:
    return accounts(request).submit_note(user, **body.model_dump())


@app.get("/api/v1/mechanic/notes")
async def my_notes(request: Request, user: dict = Depends(require("mechanic", "admin"))) -> list[dict]:
    return accounts(request).my_notes(user["user_id"])


# ---------------------------------------------------------------- admin
class RoleIn(BaseModel):
    role: str


@app.get("/api/v1/admin/stats")
async def admin_stats(request: Request, user: dict = Depends(require("admin"))) -> dict:
    return accounts(request).stats()


@app.get("/api/v1/admin/documents")
async def admin_documents(request: Request, user: dict = Depends(require("admin"))) -> list[dict]:
    return accounts(request).documents()


@app.get("/api/v1/admin/notes")
async def admin_notes(request: Request, status: Optional[str] = None,
                      user: dict = Depends(require("admin"))) -> list[dict]:
    return accounts(request).notes_for_review(status)


@app.post("/api/v1/admin/notes/{group_id}/approve")
async def approve_note(group_id: str, request: Request, user: dict = Depends(require("admin"))) -> dict:
    service: DiagnoseService = request.app.state.service
    out = await run_in_threadpool(accounts(request).approve_note, group_id, service.retriever.embedder)
    service.retriever.invalidate()          # make the note searchable now
    return out


@app.post("/api/v1/admin/notes/{group_id}/reject", status_code=204)
async def reject_note(group_id: str, request: Request, user: dict = Depends(require("admin"))) -> None:
    accounts(request).reject_note(group_id)


@app.get("/api/v1/admin/users")
async def admin_users(request: Request, user: dict = Depends(require("admin"))) -> list[dict]:
    return accounts(request).list_users()


@app.patch("/api/v1/admin/users/{user_id}")
async def admin_set_role(user_id: str, body: RoleIn, request: Request,
                         user: dict = Depends(require("admin"))) -> dict:
    return accounts(request).set_role(user["user_id"], user_id, body.role)


@app.post("/api/v1/admin/reindex", status_code=204)
async def reindex(request: Request, user: dict = Depends(require("admin"))) -> None:
    """Drop cached per-vehicle indexes after new documents are loaded from the command line."""
    request.app.state.service.retriever.invalidate()


# -- Serve the built React app (frontend/dist) at /app, if it exists -------------
_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/app", StaticFiles(directory=_DIST, html=True), name="app")

    @app.get("/", include_in_schema=False)
    async def _root() -> RedirectResponse:
        return RedirectResponse("/app/")


__all__ = ["app", "build_service", "ROLES"]

# [2026-05-29] feat(ocr): [AUT-106] camera fa

# [2026-06-01] feat(ocr): [AUT-106] camera fault c by Danial Hameed
