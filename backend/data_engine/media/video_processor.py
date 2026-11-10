"""Authorized Video Audio-Extraction, Screenshot & Transcription Pipeline.

Strictly enforces licensing and permission before processing any media file:
- Permits only: 'explicit_consent', 'creative_common', 'user_submission', 'owned'.
- Rejects standard copyrighted YouTube streams without explicit authorization.
- Extracts 16kHz mono WAV audio and timestamped JPG diagnostic screenshots via ffmpeg.
- Uses faster-whisper / whisper when installed; otherwise extracts audio + parses provided transcript text.
"""
from __future__ import annotations

import datetime as dt
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..cleaning import CleaningPipeline
from ..config import get_config
from ..logger import AuditAction, get_audit_logger
from ..schema import (
    AudioInfo,
    AutomotiveRecord,
    CostInfo,
    ImageVideoInfo,
    ProblemInfo,
    RepairInfo,
    SourceQualityInfo,
    VehicleInfo,
)
from ..storage import StorageManager
from ..taxonomy import DiagnosisStage, normalize_make_model
from .transcription import TranscriptClaimExtractor
from .vault import MediaVault

PERMITTED_RIGHTS_BASES = frozenset({
    "explicit_consent",
    "creative_common",
    "user_submission",
    "owned",
})


def get_ffmpeg_binary() -> str:
    """Returns bundled ffmpeg executable via imageio_ffmpeg."""
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


class AuthorizedMediaPipeline:
    """Extracts audio, screenshots, and diagnostic claims from permitted videos."""

    def __init__(self, vault: Optional[MediaVault] = None) -> None:
        self.config = get_config()
        self.logger = get_audit_logger()
        self.vault = vault or MediaVault()
        self.extractor = TranscriptClaimExtractor()

    def check_permission(self, rights_basis: str) -> None:
        if (rights_basis or "").strip().lower() not in PERMITTED_RIGHTS_BASES:
            self.logger.log(
                AuditAction.RECORD_REJECTED,
                source_id="media_pipeline",
                status="REJECTED",
                details={"reason": "Insufficient rights basis for media extraction", "rights_basis": rights_basis},
            )
            raise PermissionError(
                f"Media extraction blocked: rights_basis='{rights_basis}' is not permitted. "
                f"Must be one of {sorted(PERMITTED_RIGHTS_BASES)}."
            )

    def extract_audio_wav(self, video_path: Path | str, rights_basis: str, attribution: str = "") -> Dict[str, Any]:
        """Extracts 16kHz mono PCM WAV audio using ffmpeg and stores it in MediaVault."""
        self.check_permission(rights_basis)
        src = Path(video_path)
        if not src.exists():
            raise FileNotFoundError(f"Video file not found: {src}")

        ffmpeg_exe = get_ffmpeg_binary()
        with tempfile.TemporaryDirectory() as tmpdir:
            wav_out = Path(tmpdir) / f"{src.stem}_16k.wav"
            cmd = [
                ffmpeg_exe, "-y", "-i", str(src),
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                str(wav_out),
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0 or not wav_out.exists():
                raise RuntimeError(f"ffmpeg audio extraction failed: {proc.stderr[-300:]}")

            return self.vault.store_asset(
                source_file=wav_out,
                asset_type="audio",
                rights_basis=rights_basis,
                attribution=attribution,
            )

    def extract_screenshots(
        self,
        video_path: Path | str,
        rights_basis: str,
        timestamps_sec: Optional[List[float]] = None,
        attribution: str = "",
    ) -> List[Dict[str, Any]]:
        """Extracts JPG diagnostic screenshots at given timestamps and stores them in MediaVault."""
        self.check_permission(rights_basis)
        src = Path(video_path)
        if not src.exists():
            raise FileNotFoundError(f"Video file not found: {src}")

        timestamps = timestamps_sec or [1.0, 5.0, 15.0]
        ffmpeg_exe = get_ffmpeg_binary()
        stored_frames: List[Dict[str, Any]] = []

        with tempfile.TemporaryDirectory() as tmpdir:
            for ts in timestamps:
                img_out = Path(tmpdir) / f"frame_{int(ts)}s.jpg"
                cmd = [
                    ffmpeg_exe, "-y", "-ss", str(ts), "-i", str(src),
                    "-frames:v", "1", "-q:v", "3", str(img_out),
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.returncode == 0 and img_out.exists() and img_out.stat().st_size > 0:
                    asset = self.vault.store_asset(
                        source_file=img_out,
                        asset_type="images",
                        rights_basis=rights_basis,
                        attribution=f"{attribution} (t={ts}s)".strip(),
                    )
                    asset["video_timestamp_sec"] = ts
                    stored_frames.append(asset)

        return stored_frames

    def transcribe_if_available(self, audio_path: Path | str) -> Dict[str, Any]:
        """Runs faster-whisper or openai-whisper if installed; returns clean status otherwise."""
        p = Path(audio_path)
        try:
            from faster_whisper import WhisperModel  # type: ignore
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, info = model.transcribe(str(p))
            segs = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]
            return {
                "engine": "faster-whisper",
                "language": info.language,
                "text": " ".join(s["text"] for s in segs),
                "segments": segs,
            }
        except ImportError:
            pass

        try:
            import whisper  # type: ignore
            model = whisper.load_model("base")
            res = model.transcribe(str(p))
            return {
                "engine": "openai-whisper",
                "language": res.get("language", "unknown"),
                "text": (res.get("text") or "").strip(),
                "segments": res.get("segments", []),
            }
        except ImportError:
            pass

        return {
            "engine": "none",
            "status": "whisper_not_installed",
            "text": "",
            "segments": [],
            "note": "Audio extracted cleanly to MediaVault. Install 'faster-whisper' or supply transcript_text to transcribe.",
        }

    def process_authorized_video(
        self,
        video_path: Path | str,
        rights_basis: str,
        make: str = "Unknown",
        model: str = "Unknown",
        title: str = "Authorized Video Diagnostic Recording",
        timestamps_sec: Optional[List[float]] = None,
        transcript_text: Optional[str] = None,
        attribution: str = "",
        source_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """End-to-end processing of an authorized video: audio + screenshots + claims + DB storage."""
        self.check_permission(rights_basis)
        storage = StorageManager()

        # 1. Store original permitted video + extract audio & screenshots
        video_asset = self.vault.store_asset(video_path, "videos", rights_basis, attribution)
        storage.register_media_asset(video_asset, "videos")

        audio_asset = self.extract_audio_wav(video_path, rights_basis, attribution)
        storage.register_media_asset(audio_asset, "audio")

        screenshots = self.extract_screenshots(video_path, rights_basis, timestamps_sec, attribution)
        for sc in screenshots:
            storage.register_media_asset(sc, "images")

        # 2. Speech-to-text or provided transcript
        stt_result = {"engine": "provided_transcript", "text": transcript_text or "", "segments": []}
        if not transcript_text:
            stt_result = self.transcribe_if_available(audio_asset["absolute_path"])

        raw_transcript = stt_result.get("text") or title
        claims = self.extractor.process_transcript(raw_transcript, stt_result.get("segments"))

        norm_make, norm_model = normalize_make_model(make, model)
        final_make = claims.vehicle_make or norm_make or make
        final_model = claims.vehicle_model or norm_model or model

        primary_img = screenshots[0]["relative_reference"] if screenshots else None
        ts_str = ", ".join(f"{s['video_timestamp_sec']}s" for s in screenshots) if screenshots else None

        rec = AutomotiveRecord(
            vehicle=VehicleInfo(make=final_make, model=final_model),
            problem=ProblemInfo(
                problem_title=title,
                problem_description=claims.cleaned_transcript or title,
                symptoms=claims.symptoms_mentioned or [title],
                fault_category=claims.matched_fault_category,
                suspected_causes=claims.suspected_causes,
                diagnosis_stage=DiagnosisStage.OWNER_REPORTED_PROBLEM.value,
            ),
            audio=AudioInfo(
                audio_file_reference=audio_asset["relative_reference"],
                audio_type="video_extracted_16k_wav",
                sound_description=f"Extracted from {Path(video_path).name}",
            ),
            media=ImageVideoInfo(
                image_reference=primary_img,
                video_reference=video_asset["relative_reference"],
                media_type="video_clip_with_screenshots",
                video_timestamp=ts_str,
                image_description=f"{len(screenshots)} diagnostic screenshot(s) extracted",
                annotation_status="unannotated",
            ),
            repair=RepairInfo(
                recommended_solution=", ".join(claims.suggested_repairs) if claims.suggested_repairs else None,
                verification_status="unverified",
            ) if claims.suggested_repairs else None,
            cost=CostInfo(
                estimated_cost_pkr=claims.cost_mentions_pkr[0],
                price_source="video_transcript_mention",
            ) if claims.cost_mentions_pkr else None,
            source=SourceQualityInfo(
                source_platform="youtube" if source_url and "youtube" in source_url else "owner_submission",
                source_url=source_url,
                source_id=f"vid_{video_asset['sha256'][:12]}",
                language=claims.detected_language,
                evidence_reference=f"screenshots={len(screenshots)}; stt={stt_result.get('engine')}",
                rights_basis=rights_basis,
                permission_status="permitted",
                human_review_status="pending",
                confidence_score=0.70,
            ),
        )

        clean_summary = CleaningPipeline().process_batch([rec])
        storage.insert_record(rec)

        return {
            "record_id": rec.record_id,
            "audio_asset": audio_asset,
            "video_asset": video_asset,
            "screenshots": screenshots,
            "stt_status": stt_result.get("engine"),
            "extracted_claims": claims.to_dict(),
            "cleaning_summary": clean_summary,
        }
