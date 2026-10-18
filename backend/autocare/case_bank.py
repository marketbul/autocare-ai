"""M8: Similar-Case Retrieval and Diagnostic Case Bank (Story 9).

Stores completed diagnostic sessions and allows owners to find prior cases
with matching vehicle patterns, symptoms, and trouble codes, along with their
recorded resolutions. Clearly labels 'seeded' cases vs 'real' cases.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


@dataclass
class SimilarCase:
    case_id: str
    vehicle_model: str
    vehicle_year: int | None
    symptom_text: str
    code: str | None
    category: str | None
    urgency: str | None
    resolution: str
    provenance: str  # 'seeded' | 'real'
    similarity: float


class CaseBank:
    def __init__(self, db, embedder=None):
        self.db = db
        self.embedder = embedder

    def search(self,
               symptom_text: str,
               vehicle_model: str | None = None,
               year: int | None = None,
               code: str | None = None,
               category: str | None = None,
               top_k: int = 3,
               min_similarity: float = 0.25) -> list[SimilarCase]:
        # Query cases with recorded outcomes
        query = """
            SELECT dc.case_id, dc.symptom_text, dc.code, dc.predicted_category,
                   dc.predicted_urgency, dc.outcome, dc.provenance,
                   v.model, v.year
            FROM diagnosticcase dc
            LEFT JOIN uservehicle uv ON uv.user_vehicle_id = dc.user_vehicle_id
            LEFT JOIN vehicle v ON v.vehicle_id = uv.vehicle_id
            WHERE dc.outcome IS NOT NULL AND length(trim(dc.outcome)) > 0
        """
        rows = self.db.query(query)
        if not rows:
            return []

        scored = []
        q_norm = symptom_text.strip().lower()

        for r in rows:
            score = 0.0
            # Lexical / keyword overlap
            s_norm = (r["symptom_text"] or "").lower()
            q_words = set(q_norm.split())
            s_words = set(s_norm.split())
            if q_words and s_words:
                overlap = len(q_words & s_words)
                token_recall = overlap / len(q_words)
                jaccard = overlap / len(q_words | s_words)
                score += (token_recall * 0.45 + jaccard * 0.35)

            # Model match boost
            if r.get("model") and vehicle_model and r["model"].lower() == vehicle_model.lower():
                score += 0.20

            # Exact DTC code match boost
            if code and r.get("code") and code.strip().upper() == r["code"].strip().upper():
                score += 0.30

            # Category match boost
            if category and r.get("predicted_category") and category.lower() == r["predicted_category"].lower():
                score += 0.10

            if score >= min_similarity:
                scored.append(SimilarCase(
                    case_id=r["case_id"],
                    vehicle_model=r.get("model") or (vehicle_model or "Standard"),
                    vehicle_year=r.get("year"),
                    symptom_text=r["symptom_text"],
                    code=r.get("code"),
                    category=r.get("predicted_category"),
                    urgency=r.get("predicted_urgency"),
                    resolution=r["outcome"],
                    provenance=r.get("provenance") or "seeded",
                    similarity=round(min(0.99, score), 2),
                ))

        scored.sort(key=lambda x: -x.similarity)
        return scored[:top_k]

    def record_outcome(self, case_id: str, resolution_text: str) -> bool:
        """Stores user's real resolution after repair to inform future similar-case retrieval."""
        self.db.execute(
            "UPDATE diagnosticcase SET outcome = :o WHERE case_id = :c",
            {"o": resolution_text.strip(), "c": case_id}
        )
        return True

# [2026-08-24] feat(casebank): [AUT-114] impl

# [2026-08-26] feat(casebank): [AUT-114] add 

# [2026-08-17] feat(casebank): [AUT-114] implement by Danial Hameed
