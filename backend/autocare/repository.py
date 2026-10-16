"""All SQL used by User Story 2. Table/column names match the ER diagram."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .db import Database


@dataclass
class VehicleProfile:
    user_vehicle_id: str
    user_id: str
    vehicle_id: str
    manufacturer: str
    model: str
    variant: str | None
    year: int
    engine: str | None
    current_mileage: int | None

    @property
    def label(self) -> str:
        v = f" {self.variant}" if self.variant else ""
        return f"{self.manufacturer} {self.model}{v} {self.year}"


@dataclass(eq=False)
class ChunkRecord:
    chunk_id: str
    document_id: str
    document_name: str
    document_type: str
    version: str | None
    section: str | None
    page_number: int | None
    text: str
    chunk_type: str | None
    embedding: np.ndarray | None


def _decode_embedding(value) -> np.ndarray | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        arr = value
    elif isinstance(value, str):
        arr = json.loads(value)
    else:  # pgvector adapter registered -> numpy array already
        arr = value
    return np.asarray(arr, dtype=np.float32)


def encode_embedding(vec: Iterable[float] | None) -> str | None:
    if vec is None:
        return None
    return "[" + ",".join(f"{float(x):.6f}" for x in vec) + "]"


class Repository:
    def __init__(self, db: Database):
        self.db = db

    # -- reads used at query time ---------------------------------------------
    def list_vehicle_profiles(self) -> list[VehicleProfile]:
        rows = self.db.query("SELECT user_vehicle_id FROM uservehicle ORDER BY user_vehicle_id")
        return [p for r in rows if (p := self.get_vehicle_profile(r["user_vehicle_id"]))]

    def get_vehicle_profile(self, user_vehicle_id: str) -> VehicleProfile | None:
        rows = self.db.query(
            """
            SELECT uv.user_vehicle_id, uv.user_id, uv.vehicle_id, uv.current_mileage,
                   v.manufacturer, v.model, v.variant, v.year, v.engine
            FROM uservehicle uv
            JOIN vehicle v ON v.vehicle_id = uv.vehicle_id
            WHERE uv.user_vehicle_id = :uvid
            """,
            {"uvid": user_vehicle_id},
        )
        if not rows:
            return None
        r = rows[0]
        return VehicleProfile(
            user_vehicle_id=r["user_vehicle_id"], user_id=r["user_id"], vehicle_id=r["vehicle_id"],
            manufacturer=r["manufacturer"], model=r["model"], variant=r["variant"],
            year=int(r["year"]), engine=r["engine"], current_mileage=r["current_mileage"],
        )

    def chunks_in_scope(self, manufacturer: str, model: str, year: int) -> list[ChunkRecord]:
        """L2 metadata filter (proposal §6.5): only chunks whose document belongs to
        the same manufacturer + model + model-year, plus vehicle-independent
        documents (document.vehicle_id IS NULL, e.g. the OBD-II code reference)."""
        rows = self.db.query(
            """
            SELECT c.chunk_id, c.document_id, c.section, c.page_number, c.text,
                   c.embedding, c.chunk_type,
                   d.document_name, d.document_type, d.version
            FROM documentchunk c
            JOIN document d ON d.document_id = c.document_id
            LEFT JOIN vehicle v ON v.vehicle_id = d.vehicle_id
            WHERE d.document_type <> 'mechanic_note_pending'
              AND (d.vehicle_id IS NULL
                   OR (lower(v.manufacturer) = lower(:m) AND lower(v.model) = lower(:mo) AND v.year = :y))
            ORDER BY c.chunk_id
            """,
            {"m": manufacturer, "mo": model, "y": int(year)},
        )
        return [
            ChunkRecord(
                chunk_id=r["chunk_id"], document_id=r["document_id"],
                document_name=r["document_name"], document_type=r["document_type"],
                version=r["version"], section=r["section"], page_number=r["page_number"],
                text=r["text"], chunk_type=r["chunk_type"],
                embedding=_decode_embedding(r["embedding"]),
            )
            for r in rows
        ]

    def existing_codes(self, codes: list[str]) -> set[str]:
        found = set()
        for code in codes:
            if self.db.query("SELECT code FROM diagnosticcode WHERE code = :c", {"c": code}):
                found.add(code)
        return found

    def get_codes(self, codes: list[str]) -> list[dict]:
        out = []
        for code in codes:
            rows = self.db.query("""SELECT code, description, system, possible_causes, symptoms, severity
                                    FROM diagnosticcode WHERE code = :c""", {"c": code})
            out.extend(rows)
        return out

    # -- writes ----------------------------------------------------------------
    def insert_diagnostic_case(self, *, case_id: str, user_vehicle_id: str, symptom_text: str,
                               language: str, code: str | None, evidence_refs: list[str],
                               provenance: str = "real", predicted_category: str | None = None,
                               component_group: str | None = None, predicted_urgency: str | None = None,
                               confidence: float | None = None) -> None:
        # predicted_* come from M2 (Story 4). `confidence` holds the raw classifier
        # probability until M3 (Story 5) replaces it with the calibrated score.
        # outcome = the real-world resolution, unknown at query time.
        self.db.execute(
            """
            INSERT INTO diagnosticcase
                (case_id, user_vehicle_id, symptom_text, language, code,
                 predicted_category, component_group, predicted_urgency, confidence,
                 evidence_refs, outcome, provenance)
            VALUES (:case_id, :uvid, :symptom_text, :language, :code,
                    :predicted_category, :component_group, :predicted_urgency, :confidence,
                    :evidence_refs, NULL, :provenance)
            """,
            {
                "case_id": case_id, "uvid": user_vehicle_id, "symptom_text": symptom_text,
                "language": language, "code": code,
                "predicted_category": predicted_category, "component_group": component_group,
                "predicted_urgency": predicted_urgency, "confidence": confidence,
                "evidence_refs": json.dumps(evidence_refs), "provenance": provenance,
            },
        )

    # -- ingestion helpers -----------------------------------------------------
    def upsert_vehicle(self, row: dict) -> None:
        self.db.execute(
            """
            INSERT INTO vehicle (vehicle_id, manufacturer, model, variant, year, engine,
                                 transmission, fuel_type)
            VALUES (:vehicle_id, :manufacturer, :model, :variant, :year, :engine,
                    :transmission, :fuel_type)
            ON CONFLICT (vehicle_id) DO UPDATE SET
                manufacturer = excluded.manufacturer, model = excluded.model,
                variant = excluded.variant, year = excluded.year, engine = excluded.engine,
                transmission = excluded.transmission, fuel_type = excluded.fuel_type
            """,
            row,
        )

    def insert_user_vehicle(self, row: dict) -> None:
        self.db.execute(
            """
            INSERT INTO uservehicle (user_vehicle_id, user_id, vehicle_id, registration_year,
                                     current_mileage, last_reading_date, usage_profile)
            VALUES (:user_vehicle_id, :user_id, :vehicle_id, :registration_year,
                    :current_mileage, :last_reading_date, :usage_profile)
            """,
            row,
        )

    def find_vehicle_ids(self, manufacturer: str, model: str, year: int) -> list[str]:
        rows = self.db.query(
            """
            SELECT vehicle_id FROM vehicle
            WHERE lower(manufacturer) = lower(:m) AND lower(model) = lower(:mo) AND year = :y
            ORDER BY vehicle_id
            """,
            {"m": manufacturer, "mo": model, "y": int(year)},
        )
        return [r["vehicle_id"] for r in rows]

    def insert_document(self, row: dict) -> None:
        self.db.execute(
            """
            INSERT INTO document (document_id, vehicle_id, document_name, document_type,
                                  version, source, license_note, ingest_date)
            VALUES (:document_id, :vehicle_id, :document_name, :document_type,
                    :version, :source, :license_note, :ingest_date)
            """,
            row,
        )

    def delete_documents_by_type(self, document_type: str) -> None:
        self.db.execute(
            "DELETE FROM documentchunk WHERE document_id IN "
            "(SELECT document_id FROM document WHERE document_type = :t)", {"t": document_type})
        self.db.execute("DELETE FROM document WHERE document_type = :t", {"t": document_type})

    def insert_chunks(self, rows: list[dict]) -> None:
        emb = self.db.vector_param("embedding")
        self.db.executemany(
            f"""
            INSERT INTO documentchunk (chunk_id, document_id, section, page_number, text,
                                       embedding, chunk_type)
            VALUES (:chunk_id, :document_id, :section, :page_number, :text, {emb}, :chunk_type)
            """,
            rows,
        )

    def upsert_diagnostic_code(self, row: dict) -> None:
        self.db.execute(
            """
            INSERT INTO diagnosticcode (code, description, system, possible_causes, symptoms,
                                        severity, source_ref)
            VALUES (:code, :description, :system, :possible_causes, :symptoms,
                    :severity, :source_ref)
            ON CONFLICT (code) DO UPDATE SET
                description = excluded.description, system = excluded.system,
                possible_causes = excluded.possible_causes, symptoms = excluded.symptoms,
                severity = excluded.severity, source_ref = excluded.source_ref
            """,
            row,
        )
