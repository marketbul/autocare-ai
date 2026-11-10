"""Configuration management for AI Auto Pakistan Data Engineering System.

Loads environment variables with robust defaults, absolute directory resolution,
API credential protection, and ethical/legal safety flags.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


# Root directory is the backend folder
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if load_dotenv is not None and (BACKEND_ROOT / ".env").exists():
    load_dotenv(BACKEND_ROOT / ".env", override=False)


@dataclass
class DataEngineConfig:
    # --- Base Paths ---
    backend_root: Path = BACKEND_ROOT
    data_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data")
    raw_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "raw")
    processed_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "processed")
    validated_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "validated")
    ml_ready_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "ml_ready")
    templates_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "templates")
    media_vault_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "media_vault")
    queries_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "queries")
    reports_dir: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "reports")
    audit_log_path: Path = field(default_factory=lambda: BACKEND_ROOT / "data" / "audit_log.jsonl")

    # --- API Credentials ---
    youtube_api_key: str = field(
        default_factory=lambda: os.getenv("YOUTUBE_API_KEY", "").strip()
    )
    facebook_access_token: str = field(
        default_factory=lambda: os.getenv("FACEBOOK_ACCESS_TOKEN", "").strip()
    )
    facebook_page_id: str = field(
        default_factory=lambda: os.getenv("FACEBOOK_PAGE_ID", "").strip()
    )

    # --- Database Settings ---
    database_url: str = field(
        default_factory=lambda: os.getenv("AUTOCARE_DATABASE_URL", "sqlite:///autocare.db")
    )

    # --- Collection & Rate Limiting Settings ---
    youtube_max_results_per_query: int = field(
        default_factory=lambda: int(os.getenv("YOUTUBE_MAX_RESULTS_PER_QUERY", "25"))
    )
    request_timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("DATA_ENGINE_TIMEOUT_SECONDS", "30.0"))
    )
    rate_limit_delay_seconds: float = field(
        default_factory=lambda: float(os.getenv("DATA_ENGINE_RATE_LIMIT_DELAY", "1.0"))
    )

    # --- Legal & Ethical Constraints ---
    metadata_only_default: bool = True
    require_consent_for_interviews: bool = True
    anonymize_personal_identifiers: bool = True
    allow_unauthorized_scraping: bool = False  # Strictly False: Respect ToS and robots.txt

    # --- Supported Pakistani Vehicle Ecosystem Focus ---
    supported_makes: tuple[str, ...] = (
        "Suzuki",
        "Toyota",
        "Honda",
        "Hyundai",
        "KIA",
        "Changan",
        "Daihatsu",
        "Nissan",
        "MG",
        "Proton",
        "Prince / DFSK",
        "United",
    )

    supported_languages: tuple[str, ...] = (
        "en",         # English
        "ur",         # Urdu (Nastaliq / Arabic script)
        "roman_ur",   # Roman Urdu (Urdu typed in Latin script)
        "punjabi",    # Punjabi (Shahmukhi or Roman script)
    )

    def ensure_directories(self) -> None:
        """Create all required data and logging directories if they do not exist."""
        for path in [
            self.data_dir,
            self.raw_dir,
            self.raw_dir / "youtube",
            self.raw_dir / "facebook",
            self.raw_dir / "pakwheels",
            self.raw_dir / "mechanic_notes",
            self.raw_dir / "owner_reports",
            self.raw_dir / "manuals",
            self.processed_dir,
            self.validated_dir,
            self.ml_ready_dir,
            self.templates_dir,
            self.media_vault_dir,
            self.queries_dir,
            self.reports_dir,
            self.audit_log_path.parent,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        """Safe dictionary representation with masked API keys."""
        return {
            "backend_root": str(self.backend_root),
            "data_dir": str(self.data_dir),
            "database_url": self.database_url,
            "has_youtube_key": bool(self.youtube_api_key),
            "has_facebook_token": bool(self.facebook_access_token),
            "metadata_only_default": self.metadata_only_default,
            "require_consent": self.require_consent_for_interviews,
            "anonymize_personal_data": self.anonymize_personal_identifiers,
            "supported_languages": list(self.supported_languages),
            "supported_makes_count": len(self.supported_makes),
        }


_CONFIG_INSTANCE: DataEngineConfig | None = None


def get_config() -> DataEngineConfig:
    """Singleton getter for DataEngineConfig."""
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is None:
        _CONFIG_INSTANCE = DataEngineConfig()
        _CONFIG_INSTANCE.ensure_directories()
    return _CONFIG_INSTANCE
