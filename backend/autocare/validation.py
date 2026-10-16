"""Citation validation (proposal §6.7, AC2).

A claim survives only if
  (a) it cites at least one evidence id that was actually retrieved, and
  (b) at least one cited passage supports it: reranker(claim, passage) >= min_claim_support.
For Urdu / Roman-Urdu answers the LLM also returns an English rendering of each
claim ("text_en"), which is what gets checked against the English passage.

Claims that fail are removed — never shown — and counted; the count feeds M3.
"""
from __future__ import annotations

from dataclasses import dataclass

from .ml import Reranker
from .retrieval import Evidence


@dataclass
class ValidatedClaim:
    text: str
    evidence: list[Evidence]
    support_score: float


@dataclass
class DroppedClaim:
    text: str
    reason: str                 # no_citation | unknown_citation | unsupported
    support_score: float | None = None


def validate_claims(raw_claims: list[dict], evidence: list[Evidence], reranker: Reranker,
                    min_support: float) -> tuple[list[ValidatedClaim], list[DroppedClaim]]:
    by_label = {e.label: e for e in evidence}
    kept: list[ValidatedClaim] = []
    dropped: list[DroppedClaim] = []
    for c in raw_claims:
        text = (c.get("text") or "").strip()
        if not text:
            continue
        ids = [i.upper() for i in c.get("evidence_ids", [])]
        if not ids:
            dropped.append(DroppedClaim(text, "no_citation"))
            continue
        cited = [by_label[i] for i in dict.fromkeys(ids) if i in by_label]
        if not cited:
            dropped.append(DroppedClaim(text, "unknown_citation"))
            continue
        # Verify the English rendering when present: the corpus is English, and the
        # reranker scores English-English pairs far more reliably than Roman Urdu-English.
        check = (c.get("text_en") or "").strip() or text
        scores = reranker.score(check, [e.chunk.text for e in cited])
        supporting = [(e, s) for e, s in zip(cited, scores) if s >= min_support]
        if not supporting:
            dropped.append(DroppedClaim(text, "unsupported", round(max(scores), 4)))
            continue
        # Keep only the citations that actually support the claim.
        kept.append(ValidatedClaim(text, [e for e, _ in supporting],
                                   round(max(s for _, s in supporting), 4)))
    return kept, dropped
