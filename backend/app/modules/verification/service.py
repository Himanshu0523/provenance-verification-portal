import hashlib
import json
import uuid
from datetime import datetime, timezone

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import PayloadTooLargeError, ValidationError
from app.core.security import verify_ed25519
from app.integrations.storage import get_storage
from app.integrations.storage.base import StorageProvider
from app.modules.audit.repository import AuditRepository
from app.modules.creators.models import Creator, CreatorKey
from app.modules.media_assets.models import MediaAsset
from app.modules.media_assets.validators import validate_bytes
from app.modules.verification.result_classifier import (
    best_verdict, classify_asset,
)
from app.modules.verification.schemas import MatchDetail, VerifyResponse
from app.shared.hashing import sha256_hex

async def _read_capped(upload: UploadFile, cap: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await upload.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > cap:
            raise PayloadTooLargeError(f"file exceeds {cap} bytes")
        chunks.append(chunk)
    return b"".join(chunks)

def _manifest_ok(asset: MediaAsset) -> bool:
    """The stored signed_payload must be a well-formed provenance/v1 manifest
    whose asset_sha256 matches this asset's own sha256_hash."""
    if not asset.signed_payload:
        return False
    try:
        obj = json.loads(asset.signed_payload)
    except (ValueError, TypeError):
        return False
    if not isinstance(obj, dict):
        return False
    if obj.get("schema") != "provenance/v1":
        return False
    if obj.get("asset_sha256") != asset.sha256_hash:
        return False
    if obj.get("creator_id") != str(asset.creator_id):
        return False
    if obj.get("key_id") != (asset.signer_key_id or ""):
        return False
    return True

class VerificationService:
    def __init__(self, db: AsyncSession, storage: StorageProvider | None = None):
        self.db = db
        self.storage = storage or get_storage()
        self.audit = AuditRepository(db)

    async def verify(self, *, upload: UploadFile) -> VerifyResponse:
        data = await _read_capped(upload, settings.verify_max_bytes)
        try:
            validate_bytes(data)          # magic bytes + size + mime allow-list
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        query_sha = hashlib.sha256(data).hexdigest()

        stmt = select(MediaAsset).where(MediaAsset.sha256_hash == query_sha)
        assets = list((await self.db.execute(stmt)).scalars().all())

        matches: list[MatchDetail] = []
        for asset in assets:
            creator = await self.db.get(Creator, asset.creator_id)
            key = None
            if asset.signer_key_id:
                key_stmt = select(CreatorKey).where(
                    CreatorKey.key_id == asset.signer_key_id
                )
                key = (await self.db.execute(key_stmt)).scalar_one_or_none()

            manifest_ok = _manifest_ok(asset)
            signature_valid = False
            if key is not None and asset.signed_payload and asset.signature:
                signature_valid = verify_ed25519(
                    key.public_key,
                    asset.signed_payload.encode("utf-8"),
                    asset.signature,
                )
            key_status = key.status if key else "unknown"

            per_verdict = classify_asset(
                manifest_ok=manifest_ok,
                signature_valid=signature_valid,
                key_status=key_status,
            )

            preview = await self.storage.get_url(asset.storage_key)
            matches.append(
                MatchDetail(
                    asset_id=asset.id,
                    creator_id=asset.creator_id,
                    creator_display_name=creator.display_name if creator else "unknown",
                    key_id=asset.signer_key_id or "",
                    key_status=key_status,
                    signature_valid=signature_valid,
                    manifest_ok=manifest_ok,
                    per_asset_verdict=per_verdict,
                    signed_at=asset.client_created_at
                             or asset.created_at,
                    original_filename=asset.original_filename,
                    mime_type=asset.mime_type,
                    file_size=asset.file_size,
                    sha256=asset.sha256_hash,
                    preview_url=preview,
                    signature_checked_against="provenance/v1",
                )
            )

        verdict = best_verdict([m.per_asset_verdict for m in matches])

        audit_id: uuid.UUID | None = None
        if settings.verify_audit_enabled:
            entry = await self.audit.write(
                event_type="media.verify",
                actor_id=None,
                asset_id=matches[0].asset_id if matches else None,
                event_data={
                    "query_sha256": query_sha,
                    "verdict": verdict,
                    "match_count": len(matches),
                    "matched_asset_ids": [str(m.asset_id) for m in matches],
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            audit_id = entry.id

        await self.db.commit()

        return VerifyResponse(
            query_sha256=query_sha,
            verdict=verdict,
            total_matches=len(matches),
            audit_id=audit_id,
            matches=matches,
        )