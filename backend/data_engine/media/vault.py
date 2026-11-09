"""Media Asset Vault for AI Auto Pakistan.

Manages authorized media assets (audio recordings, vehicle images, video clips)
with relative database referencing, SHA-256 integrity hashing, and rights attribution.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import get_config
from ..logger import AuditAction, get_audit_logger


class MediaVault:
    """Stores authorized media files with immutable cryptographic hashes."""

    def __init__(self, vault_dir: Optional[Path] = None) -> None:
        config = get_config()
        self.vault_dir = vault_dir or config.media_vault_dir
        self.audio_dir = self.vault_dir / "audio"
        self.images_dir = self.vault_dir / "images"
        self.videos_dir = self.vault_dir / "videos"
        self.logger = get_audit_logger()

        for p in [self.audio_dir, self.images_dir, self.videos_dir]:
            p.mkdir(parents=True, exist_ok=True)

    def compute_sha256(self, file_path: Path) -> str:
        """Calculates SHA-256 checksum for media file integrity."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def store_asset(
        self,
        source_file: Path | str,
        asset_type: str,  # "audio", "images", "videos"
        rights_basis: str,
        attribution: str = "",
    ) -> Dict[str, Any]:
        """Copies permitted media file into the vault and returns asset reference dict."""
        src = Path(source_file)
        if not src.exists():
            raise FileNotFoundError(f"Source media file not found: {src}")

        if asset_type not in {"audio", "images", "videos"}:
            raise ValueError(f"Invalid asset_type '{asset_type}'. Must be audio, images, or videos.")

        dest_dir = self.vault_dir / asset_type
        sha256 = self.compute_sha256(src)
        ext = src.suffix.lower()
        vault_filename = f"{sha256[:16]}{ext}"
        dest_path = dest_dir / vault_filename

        shutil.copy2(src, dest_path)

        relative_ref = f"media_vault/{asset_type}/{vault_filename}"

        self.logger.log(
            AuditAction.MEDIA_EXTRACTED,
            source_id="media_vault",
            record_id=vault_filename,
            status="SUCCESS",
            details={
                "asset_type": asset_type,
                "relative_ref": relative_ref,
                "sha256": sha256,
                "rights_basis": rights_basis,
            },
        )

        return {
            "relative_reference": relative_ref,
            "absolute_path": str(dest_path),
            "sha256": sha256,
            "size_bytes": dest_path.stat().st_size,
            "rights_basis": rights_basis,
            "attribution": attribution,
        }
