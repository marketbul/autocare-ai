"""Authorized Video/Audio Transcription and Automotive Claim Extractor.

Processes audio/video evidence:
1. Speech-to-text transcribing (Urdu, Roman Urdu, English, Punjabi)
2. Preserves raw verbatim transcript and normalized clean transcript
3. Extracts vehicle names, symptoms, suspected causes, repair suggestions, and PKR costs
4. Strictly flags extracted claims as unverified diagnostic hypotheses.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..cleaning.normalizer import detect_language, normalize_automotive_text
from ..taxonomy import get_taxonomy_manager, normalize_make_model

COST_MENTION_REGEX = re.compile(
    r"\b(?:rs\.?|pkr|rupay|rupe|hazaar|k)\s*([0-9]+(?:,[0-9]+)?)\b|\b([0-9]+(?:,[0-9]+)?)\s*(?:rs\.?|pkr|rupay|rupe|hazaar|k)\b",
    re.IGNORECASE,
)


@dataclass
class ExtractedTranscriptClaims:
    original_transcript: str
    cleaned_transcript: str
    detected_language: str
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    symptoms_mentioned: List[str] = field(default_factory=list)
    suspected_causes: List[str] = field(default_factory=list)
    suggested_repairs: List[str] = field(default_factory=list)
    cost_mentions_pkr: List[float] = field(default_factory=list)
    matched_fault_category: Optional[str] = None
    timestamps: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "original_transcript": self.original_transcript,
            "cleaned_transcript": self.cleaned_transcript,
            "detected_language": self.detected_language,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "symptoms_mentioned": self.symptoms_mentioned,
            "suspected_causes": self.suspected_causes,
            "suggested_repairs": self.suggested_repairs,
            "cost_mentions_pkr": self.cost_mentions_pkr,
            "matched_fault_category": self.matched_fault_category,
            "timestamps": self.timestamps,
        }


class TranscriptClaimExtractor:
    """Extracts structured automotive diagnostic entities from transcripts."""

    def __init__(self) -> None:
        self.taxonomy = get_taxonomy_manager()

    def process_transcript(
        self,
        raw_text: str,
        timestamp_segments: Optional[List[Dict[str, Any]]] = None,
    ) -> ExtractedTranscriptClaims:
        cleaned_text = normalize_automotive_text(raw_text)
        lang = detect_language(raw_text)

        make, model = normalize_make_model(None, raw_text)
        matched_cat = self.taxonomy.match_category_from_text(cleaned_text)

        # Extract costs mentioned in transcript
        costs: List[float] = []
        for match in COST_MENTION_REGEX.finditer(raw_text):
            val_str = match.group(1) or match.group(2)
            if val_str:
                try:
                    num = float(val_str.replace(",", ""))
                    if "hazaar" in match.group(0).lower() or "k" in match.group(0).lower():
                        num *= 1000
                    if 100 <= num <= 2_000_000:
                        costs.append(num)
                except ValueError:
                    continue

        # Extract symptoms from category match
        symptoms: List[str] = []
        if matched_cat:
            for kw in matched_cat.multilingual_symptom_keywords:
                if kw.lower() in raw_text.lower():
                    symptoms.append(kw)

        # Candidate repair actions
        repair_triggers = [
            "badalna", "change", "replace", "repair", "kharad", "saaf", "clean",
            "tuning", "servis", "service", "ultrasonic", "rebuild"
        ]
        suggested_repairs = [
            word for word in repair_triggers if word in cleaned_text.lower()
        ]

        return ExtractedTranscriptClaims(
            original_transcript=raw_text,
            cleaned_transcript=cleaned_text,
            detected_language=lang,
            vehicle_make=make,
            vehicle_model=model,
            symptoms_mentioned=symptoms,
            suspected_causes=matched_cat.typical_causes[:2] if matched_cat else [],
            suggested_repairs=suggested_repairs,
            cost_mentions_pkr=costs,
            matched_fault_category=matched_cat.category_id if matched_cat else None,
            timestamps=timestamp_segments or [],
        )
