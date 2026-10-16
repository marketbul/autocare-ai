"""Runtime settings, read from environment variables (see .env.example)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

# Vehicles this release accepts: (manufacturer, model) -> (first_year, last_year).
# All 3 in-scope vehicles from Proposal Section 4.2: Corolla, Civic, Swift (2015-2025).
DEFAULT_SUPPORTED = {
    ("toyota", "corolla"): (2015, 2025),
    ("honda", "civic"): (2015, 2025),
    ("suzuki", "swift"): (2015, 2025),
}


def _float(name: str, default: float) -> float:
    return float(os.getenv(name, default))


def _int(name: str, default: int) -> int:
    return int(os.getenv(name, default))


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///autocare.db"

    # "models" = BGE embeddings + BGE reranker (production).
    # "lite"   = lexical stand-ins, no downloads. Dev/tests only; NOT for evaluation.
    ml_backend: str = "models"
    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"

    # "llm" = OpenAI-compatible chat endpoint (OpenAI, Groq, Ollama, ...).
    # "extractive" = quote evidence sentences verbatim (English only; dev fallback).
    generation_mode: str = "llm"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_timeout_s: float = 60.0

    # Retrieval (proposal §6.4–6.6)
    candidate_k: int = 20          # hybrid candidates passed to the reranker
    final_k: int = 5               # evidence passages passed to generation (4–6)
    hybrid_alpha: float = 0.5      # weight of semantic score; (1 - alpha) for BM25

    # Gates — UNTUNED defaults. Set from the risk–coverage curve on the held-out set.
    min_evidence_score: float = 0.30   # reranker score a passage needs to count as evidence (AC5)
    min_claim_support: float = 0.25    # reranker(claim, cited passage) needed to keep a claim (AC2)

    max_query_chars: int = 1000

    # Story 4 / M2 classifier. Trained on first start if the file is missing or stale.
    triage_model_path: str = "models/triage.pkl"
    triage_data_path: str = ""      # "" = data/symptom_labels.csv, else the starter set

    # Story 3: reading a fault code from a scanner photo.
    # "vision" = vision model on the same OpenAI-compatible endpoint; "tesseract" = local OCR;
    # "off" = disabled.
    code_reader: str = "vision"
    vision_model: str = "qwen/qwen3.8-27b"     # Groq's vision model in Oct 2026; check console.groq.com/docs/vision
    max_image_bytes: int = 6_000_000
    # Story 12: "vision" (interim, zero-shot) or "off". The team's M10 CNN replaces it.
    damage_assessor: str = "vision"
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://localhost:3000")
    supported_vehicles: dict = field(default_factory=lambda: dict(DEFAULT_SUPPORTED))


def load_settings() -> Settings:
    return Settings(
        database_url=os.getenv("AUTOCARE_DATABASE_URL", Settings.database_url),
        ml_backend=os.getenv("AUTOCARE_ML_BACKEND", Settings.ml_backend),
        embedding_model=os.getenv("AUTOCARE_EMBEDDING_MODEL", Settings.embedding_model),
        reranker_model=os.getenv("AUTOCARE_RERANKER_MODEL", Settings.reranker_model),
        generation_mode=os.getenv("AUTOCARE_GENERATION_MODE", Settings.generation_mode),
        llm_base_url=os.getenv("AUTOCARE_LLM_BASE_URL", Settings.llm_base_url),
        llm_api_key=os.getenv("AUTOCARE_LLM_API_KEY", ""),
        llm_model=os.getenv("AUTOCARE_LLM_MODEL", Settings.llm_model),
        llm_timeout_s=_float("AUTOCARE_LLM_TIMEOUT_S", Settings.llm_timeout_s),
        candidate_k=_int("AUTOCARE_CANDIDATE_K", Settings.candidate_k),
        final_k=_int("AUTOCARE_FINAL_K", Settings.final_k),
        hybrid_alpha=_float("AUTOCARE_HYBRID_ALPHA", Settings.hybrid_alpha),
        min_evidence_score=_float("AUTOCARE_MIN_EVIDENCE_SCORE", Settings.min_evidence_score),
        min_claim_support=_float("AUTOCARE_MIN_CLAIM_SUPPORT", Settings.min_claim_support),
        triage_model_path=os.getenv("AUTOCARE_TRIAGE_MODEL", Settings.triage_model_path),
        triage_data_path=os.getenv("AUTOCARE_TRIAGE_DATA", ""),
        code_reader=os.getenv("AUTOCARE_CODE_READER", Settings.code_reader),
        vision_model=os.getenv("AUTOCARE_VISION_MODEL", Settings.vision_model),
        damage_assessor=os.getenv("AUTOCARE_DAMAGE_ASSESSOR", Settings.damage_assessor),
        cors_origins=tuple(
            o.strip()
            for o in os.getenv("AUTOCARE_CORS_ORIGINS", ",".join(Settings.cors_origins)).split(",")
            if o.strip()
        ),
    )


# The other in-scope models from the proposal (§4.2). Listed in the vehicle selector as
# "not supported in this release" until their manuals are loaded (Story 1 AC2).
PLANNED_MODELS = (("Honda", "Civic", 2015, 2025), ("Suzuki", "Swift", 2015, 2025))


def triage_data_path(settings: Settings) -> str:
    if settings.triage_data_path:
        return settings.triage_data_path
    here = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    real = os.path.join(here, "symptom_labels.csv")
    return real if os.path.exists(real) else os.path.join(here, "symptom_labels.starter.csv")


def is_supported(settings: Settings, manufacturer: str, model: str, year: int) -> bool:
    rng = settings.supported_vehicles.get((manufacturer.strip().lower(), model.strip().lower()))
    return rng is not None and rng[0] <= int(year) <= rng[1]


def supported_label(settings: Settings) -> str:
    return ", ".join(
        f"{m.title()} {mo.title()} {a}–{b}" for (m, mo), (a, b) in settings.supported_vehicles.items()
    )

# [2026-05-20] feat(retrieval): [AUT-104] imp

# [2026-05-22] feat(retrieval): [AUT-104] implemen by Danial Hameed
