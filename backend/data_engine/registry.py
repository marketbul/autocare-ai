"""Extensible Source Registry for AI Auto Pakistan.

Tracks collection methods, permission status, legal rights basis,
rate limits, and attribution requirements across all automotive sources.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SourceType(str, Enum):
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    PAKWHEELS = "pakwheels"
    MANUALS_AND_DOCS = "manuals_and_docs"
    MECHANIC_INTERVIEW = "mechanic_interview"
    CAR_OWNER_REPORT = "car_owner_report"
    AUTOMOTIVE_BLOG = "automotive_blog"
    RESEARCH_PAPER = "research_paper"


class RightsBasis(str, Enum):
    OFFICIAL_API_METADATA = "official_api_metadata"
    EXPLICIT_CONSENT = "explicit_consent"
    USER_SUBMISSION = "user_submission"
    PUBLIC_TECHNICAL_DOCUMENTATION = "public_technical_documentation"
    MANUAL_RESEARCH_SYNTHESIS = "manual_research_synthesis"
    OPEN_ACADEMIC_LICENSE = "open_academic_license"
    AUTHORIZED_PARTNER = "authorized_partner"


@dataclass
class DataSourceEntry:
    source_id: str
    name: str
    source_type: SourceType
    rights_basis: RightsBasis
    is_automated: bool
    requires_api_key: bool
    requires_permission: bool
    attribution_required: bool
    limitations: List[str] = field(default_factory=list)
    rate_limit_policy: str = "Standard conservative rate limiting"
    enabled: bool = True
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "name": self.name,
            "source_type": self.source_type.value,
            "rights_basis": self.rights_basis.value,
            "is_automated": self.is_automated,
            "requires_api_key": self.requires_api_key,
            "requires_permission": self.requires_permission,
            "attribution_required": self.attribution_required,
            "limitations": self.limitations,
            "rate_limit_policy": self.rate_limit_policy,
            "enabled": self.enabled,
            "description": self.description,
        }


class SourceRegistry:
    """Registry maintaining active and future automotive data sources."""

    def __init__(self) -> None:
        self._sources: Dict[str, DataSourceEntry] = {}

    def register(self, entry: DataSourceEntry) -> None:
        self._sources[entry.source_id] = entry

    def get(self, source_id: str) -> Optional[DataSourceEntry]:
        return self._sources.get(source_id)

    def list_all(self, enabled_only: bool = False) -> List[DataSourceEntry]:
        if enabled_only:
            return [s for s in self._sources.values() if s.enabled]
        return list(self._sources.values())

    def get_summary(self) -> List[dict]:
        return [s.to_dict() for s in self._sources.values()]


def create_default_source_registry() -> SourceRegistry:
    """Constructs the official source registry for AI Auto Pakistan."""
    registry = SourceRegistry()

    # 1. YouTube Data API v3
    registry.register(
        DataSourceEntry(
            source_id="youtube_official_api",
            name="YouTube Automotive Intelligence (Official Data API)",
            source_type=SourceType.YOUTUBE,
            rights_basis=RightsBasis.OFFICIAL_API_METADATA,
            is_automated=True,
            requires_api_key=True,
            requires_permission=False,
            attribution_required=True,
            rate_limit_policy="10,000 quota units/day default YouTube API quota",
            limitations=[
                "Collects metadata only (titles, descriptions, channel, statistics, tags).",
                "Does not automatically download copyrighted video/audio without lawful basis.",
                "API key required via YOUTUBE_API_KEY environment variable.",
            ],
            description="Collects verified metadata, Pakistani repair video descriptions, diagnostic symptoms, and channel provenance.",
        )
    )

    # 2. Facebook Authorized & Manual Research Import
    registry.register(
        DataSourceEntry(
            source_id="facebook_research_import",
            name="Facebook Automotive Research (Permitted API / Manual Import)",
            source_type=SourceType.FACEBOOK,
            rights_basis=RightsBasis.MANUAL_RESEARCH_SYNTHESIS,
            is_automated=False,
            requires_api_key=False,
            requires_permission=True,
            attribution_required=True,
            rate_limit_policy="Manual batch CSV import / Meta Graph API rate limits",
            limitations=[
                "No scraping of private profiles or private groups.",
                "Personal identifying information (names, phone numbers) must be sanitized.",
                "Automated access strictly via authorized Meta Graph API app or manual CSV template.",
            ],
            description="Structured acquisition of public automotive discussions, workshop case logs, and owner complaints.",
        )
    )

    # 3. PakWheels Manual Research Import
    registry.register(
        DataSourceEntry(
            source_id="pakwheels_research_import",
            name="PakWheels Automotive Knowledge (Manual Research Import)",
            source_type=SourceType.PAKWHEELS,
            rights_basis=RightsBasis.MANUAL_RESEARCH_SYNTHESIS,
            is_automated=False,
            requires_api_key=False,
            requires_permission=False,
            attribution_required=True,
            rate_limit_policy="Manual research template import; strictly no automated scraping",
            limitations=[
                "Automated scraping strictly forbidden in compliance with Terms of Service.",
                "Data ingested via human researcher curation into structured research CSV.",
                "Preserves original forum thread URL, publication date, and vehicle specs.",
            ],
            description="Curated forum threads, technical experiences, common fault reports, and workshop price reports.",
        )
    )

    # 4. Public Technical Documentation & Vehicle Manuals
    registry.register(
        DataSourceEntry(
            source_id="manuals_and_bulletins",
            name="OEM Workshop Manuals & Technical Service Bulletins",
            source_type=SourceType.MANUALS_AND_DOCS,
            rights_basis=RightsBasis.PUBLIC_TECHNICAL_DOCUMENTATION,
            is_automated=True,
            requires_api_key=False,
            requires_permission=False,
            attribution_required=True,
            rate_limit_policy="Local PDF parsing and structured chunking",
            limitations=[
                "Restricted to verified manufacturer service schedules and SAE J2012 DTC references.",
                "Cites exact document, section, and page number for every claim.",
            ],
            description="Official OEM diagnostic codes, torque specs, fluid intervals, and wiring schematics.",
        )
    )

    # 5. Mechanic Consent-Based Interviews
    registry.register(
        DataSourceEntry(
            source_id="mechanic_interviews",
            name="Consent-Based Pakistani Mechanic Field Interviews",
            source_type=SourceType.MECHANIC_INTERVIEW,
            rights_basis=RightsBasis.EXPLICIT_CONSENT,
            is_automated=False,
            requires_api_key=False,
            requires_permission=True,
            attribution_required=True,
            rate_limit_policy="Field survey batch ingestion",
            limitations=[
                "Explicit consent='yes' mandatory per respondent (refuses ingestion otherwise).",
                "Captures years of experience, city, workshop name, topic, and diagnostic advice.",
            ],
            description="Field-verified workshop diagnostics from Pakistani mechanics across Lahore, Karachi, Rawalpindi, Peshawar.",
        )
    )

    # 6. Car-Owner Problem Reports & Repair Logs
    registry.register(
        DataSourceEntry(
            source_id="owner_submissions",
            name="Pakistani Car Owner Problem Reports & Repair Logs",
            source_type=SourceType.CAR_OWNER_REPORT,
            rights_basis=RightsBasis.USER_SUBMISSION,
            is_automated=True,
            requires_api_key=False,
            requires_permission=True,
            attribution_required=False,
            rate_limit_policy="Web form and CSV batch ingestion",
            limitations=[
                "All personal identifiers (phone numbers, full names, CNICs, registration plates) automatically stripped.",
                "Distinguishes owner-reported symptoms from confirmed diagnoses.",
            ],
            description="Real-world driver experiences, repair bills in PKR, symptom descriptions, and verified repair outcomes.",
        )
    )

    return registry
