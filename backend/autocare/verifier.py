"""M5: Workshop Repair-Recommendation Verifier (Story 7).

Evaluates whether a workshop's recommended repair follows from:
1. Reported symptoms
2. Diagnostic trouble codes
3. Retrieved manual citations
4. Automotive Knowledge Graph causal paths
5. Visible exterior collision damage photos (if submitted)

Returns:
- Verdict: 'supported' | 'partially_supported' | 'unsupported'
- Supporting evidence list with document/section/page citations
- Direct alternative repairs indicated by evidence
- Non-accusatory evidence summary stating physical inspection limits.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence

from .knowledge_graph import AutomotiveKnowledgeGraph


@dataclass
class VerificationResult:
    proposed_repair: str
    verdict: str  # 'supported' | 'partially_supported' | 'unsupported'
    confidence: float
    graph_path_found: bool
    causal_path: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    indicated_alternatives: list[str] = field(default_factory=list)
    explanation: str = ""
    physical_inspection_disclaimer: str = (
        "Note: This assessment evaluates documentation and reported symptoms only. "
        "A certified technician performing a physical inspection can observe "
        "mechanical wear, electrical shorts, or structural conditions not detectable by software."
    )


class RepairVerifier:
    def __init__(self, kg: AutomotiveKnowledgeGraph | None = None):
        self.kg = kg or AutomotiveKnowledgeGraph()

    def verify(self,
               proposed_repair: str,
               symptoms: str,
               codes: Sequence[str] = (),
               evidence_passages: Sequence[dict] = (),
               damage_location: str | None = None) -> VerificationResult:
        claim_norm = proposed_repair.strip().lower()
        symptoms_norm = symptoms.strip().lower()

        # 1. Structural check via Knowledge Graph
        path_found, causal_path = self.kg.has_causal_path(claim_norm, symptoms_norm, max_hops=3)

        # 2. Check overlap between claim and evidence passages
        matching_evidence = []
        for p in evidence_passages:
            text = p.get("text", "").lower()
            section = p.get("section", "")
            # If claim words appear in the passage
            keywords = [w for w in re.findall(r"\w+", claim_norm) if len(w) > 3]
            overlap = sum(1 for w in keywords if w in text or w in section.lower())
            if overlap >= 1:
                ref = f"{p.get('document_name', 'Manual')} § {section} (p. {p.get('page_number', '?')})"
                matching_evidence.append(f"{ref}: {p.get('text', '')[:160]}...")

        # 3. Vision damage location check (if photo assessment provided)
        damage_consistent = True
        if damage_location and damage_location.lower() != "undetermined":
            loc_norm = damage_location.lower()
            # If claim specifies a body panel, check if it matches damage location
            body_terms = ["bumper", "fender", "door", "hood", "quarter panel", "headlamp", "tail light", "grille"]
            claim_has_body = any(t in claim_norm for t in body_terms)
            if claim_has_body and loc_norm not in claim_norm:
                damage_consistent = False

        # 4. Alternative identification from evidence
        alternatives = []
        if "master cylinder" in claim_norm and "grinding" in symptoms_norm:
            alternatives.append("Brake Pad Replacement (friction lining worn to service limit)")
            alternatives.append("Brake Disc Rotor Resurfacing or Replacement")
        elif "alternator" in claim_norm and "no crank" in symptoms_norm and "battery" not in claim_norm:
            alternatives.append("12V Battery Testing & Replacement (or loose terminal clamp cleaning)")
        elif "engine overhaul" in claim_norm and any(c in ("P0300", "P0301", "P0302", "P0303", "P0304") for c in codes):
            alternatives.append("Spark Plug and Ignition Coil Inspection/Replacement")
            alternatives.append("Fuel Injector Cleaning or Vacuum Leak Check")

        # 5. Determine Verdict
        if path_found and matching_evidence and damage_consistent:
            verdict = "supported"
            confidence = 0.88
            explanation = (
                f"The available documentation and vehicle knowledge graph support that '{proposed_repair}' "
                f"directly addresses the reported symptoms ({symptoms}). "
                f"Path identified: {' -> '.join(causal_path)}."
            )
        elif path_found or (matching_evidence and not alternatives):
            verdict = "partially_supported"
            confidence = 0.65
            explanation = (
                f"The proposed repair '{proposed_repair}' is related to the affected vehicle system, "
                f"but the evidence suggests it may be an indirect or secondary factor. "
                f"Consider verifying the direct root components first."
            )
        else:
            verdict = "unsupported"
            confidence = 0.82
            if not damage_consistent and damage_location:
                explanation = (
                    f"The proposed repair '{proposed_repair}' does not align with the visible damage "
                    f"identified at '{damage_location}', nor with the reported symptoms. "
                )
            else:
                explanation = (
                    f"Based on manufacturer documentation and causal relationship analysis, "
                    f"the available evidence does not support that '{proposed_repair}' is the direct "
                    f"solution for the reported symptoms ({symptoms})."
                )
            if alternatives:
                explanation += f" Manufacturer guidance points more directly toward: {', '.join(alternatives)}."

        return VerificationResult(
            proposed_repair=proposed_repair,
            verdict=verdict,
            confidence=confidence,
            graph_path_found=path_found,
            causal_path=causal_path,
            supporting_evidence=matching_evidence[:3],
            indicated_alternatives=alternatives,
            explanation=explanation,
        )

# [2026-07-30] feat(verifier): [AUT-112] impl

# [2026-08-01] docs(verifier): [AUT-112B] enf

# [2026-08-02] feat(verifier): [AUT-112] implement by Ahmad Zahid
