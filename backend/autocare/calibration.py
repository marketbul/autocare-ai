"""M3: Confidence Calibration and Selective Abstention Layer (Story 5).

Estimates calibrated reliability from multi-modal signals:
1. Classifier posterior probability (with temperature scaling / Platt scaling).
2. Retrieval evidence strength (reranker top score and margin).
3. Citation validation claim support ratio.
4. OBD-II code recognition status.
5. Visual damage agreement (when accident photos provided).

Computes:
- Calibrated confidence score in [0.0, 1.0].
- Expected Calibration Error (ECE) across reliability bins.
- Selective abstention gate: abstains conservatively on Critical-urgency paths.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class CalibrationSignals:
    classifier_prob: float = 0.5
    classifier_margin: float = 0.0
    is_critical_path: bool = False
    top_evidence_score: float = 0.0
    evidence_margin: float = 0.0
    citation_support_ratio: float = 1.0
    code_recognized: bool = True
    image_agreement: float | None = None
    temperature: float = 1.25


@dataclass
class ConfidenceReport:
    calibrated_confidence: float
    raw_confidence: float
    should_abstain: bool
    abstention_reason: str | None
    is_critical: bool
    threshold_applied: float
    signal_breakdown: dict[str, float] = field(default_factory=dict)


class ConfidenceCalibrator:
    def __init__(self,
                 base_abstention_threshold: float = 0.55,
                 critical_abstention_threshold: float = 0.70,
                 default_temperature: float = 1.25):
        self.base_threshold = base_abstention_threshold
        self.critical_threshold = critical_abstention_threshold
        self.temperature = default_temperature

    def calibrate_probability(self, prob: float, temperature: float | None = None) -> float:
        """Applies temperature scaling to raw softmax/logistic probability."""
        t = temperature or self.temperature
        p = max(1e-6, min(1.0 - 1e-6, prob))
        logit = math.log(p / (1.0 - p))
        scaled_logit = logit / t
        return 1.0 / (1.0 + math.exp(-scaled_logit))

    def evaluate(self, signals: CalibrationSignals) -> ConfidenceReport:
        # 1. Calibrated classifier signal
        scaled_clf = self.calibrate_probability(signals.classifier_prob, signals.temperature)

        # 2. Retrieval strength signal (normalize reranker score 0.0 to 1.0)
        retrieval_sig = max(0.0, min(1.0, signals.top_evidence_score))

        # 3. Citation validation signal
        citation_sig = max(0.0, min(1.0, signals.citation_support_ratio))

        # 4. DTC code penalty if unrecognised
        code_sig = 1.0 if signals.code_recognized else 0.65

        # 5. Visual damage agreement if present
        if signals.image_agreement is not None:
            vision_sig = max(0.0, min(1.0, signals.image_agreement))
            # Weighted average across all 5 signals
            composite = (
                scaled_clf * 0.35 +
                retrieval_sig * 0.30 +
                citation_sig * 0.15 +
                code_sig * 0.10 +
                vision_sig * 0.10
            )
        else:
            # Weighted average across 4 signals
            composite = (
                scaled_clf * 0.40 +
                retrieval_sig * 0.35 +
                citation_sig * 0.15 +
                code_sig * 0.10
            )

        calibrated = round(max(0.05, min(0.98, composite)), 3)
        raw = round(signals.classifier_prob, 3)

        # Apply selective abstention gate
        threshold = self.critical_threshold if signals.is_critical_path else self.base_threshold
        should_abstain = calibrated < threshold

        reason = None
        if should_abstain:
            if signals.is_critical_path:
                reason = "Potential safety-critical issue with insufficient evidence grounding; deferring to physical inspection."
            elif signals.top_evidence_score < 0.30:
                reason = "No authoritative manufacturer manual passages found matching these symptoms."
            elif not signals.code_recognized:
                reason = "Diagnostic trouble code not recognized in reference database."
            else:
                reason = "Overall confidence below reliability threshold for automated diagnostic guidance."

        return ConfidenceReport(
            calibrated_confidence=calibrated,
            raw_confidence=raw,
            should_abstain=should_abstain,
            abstention_reason=reason,
            is_critical=signals.is_critical_path,
            threshold_applied=threshold,
            signal_breakdown={
                "calibrated_classifier": round(scaled_clf, 3),
                "retrieval_strength": round(retrieval_sig, 3),
                "citation_ratio": round(citation_sig, 3),
                "code_penalty": round(code_sig, 3),
                "visual_agreement": round(signals.image_agreement, 3) if signals.image_agreement is not None else 1.0,
            }
        )

    @staticmethod
    def compute_ece(probs: Sequence[float], labels: Sequence[int], num_bins: int = 10) -> float:
        """Computes Expected Calibration Error (ECE) for evaluation (proposal §11.4)."""
        if not probs or len(probs) != len(labels):
            return 0.0

        n = len(probs)
        bin_boundaries = [i / num_bins for i in range(num_bins + 1)]
        ece = 0.0

        for b in range(num_bins):
            low, high = bin_boundaries[b], bin_boundaries[b + 1]
            in_bin = [i for i, p in enumerate(probs) if (low <= p < high or (b == num_bins - 1 and p == high))]
            if not in_bin:
                continue

            bin_conf = sum(probs[i] for i in in_bin) / len(in_bin)
            bin_acc = sum(labels[i] for i in in_bin) / len(in_bin)
            ece += (len(in_bin) / n) * abs(bin_acc - bin_conf)

        return round(ece, 4)
