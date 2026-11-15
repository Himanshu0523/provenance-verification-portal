import uuid
from datetime import datetime, timezone

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    ConflictError, NotFoundError, PayloadTooLargeError,
    ValidationError, DomainError,
)
from app.core.security import verify_ed25519
from app.integrations.storage.base import StorageProvider
from app.modules.creators.repository import CreatorRepository
from app.modules.forensic_analysis.perceptual_hash import compute_perceptual_hash
from app.modules.media_assets.models import MediaAsset
from app.modules.media_assets.validators import (
    validate_bytes, validate_client_created_at, MIME_TO_EXT,
)
from app.modules.publishing.manifest_builder import build_canonical_payload
from app.modules.publishing.schemas import PublishResponse
from app.shared.hashing import sha256_hex

MAX_SKEW_SECONDS = 300

async def _read_capped(upload: UploadFile) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await upload.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > settings.max_upload_bytes:
            raise PayloadTooLargeError(
                f"file exceeds {settings.max_upload_bytes} bytes"
            )
        chunks.append(chunk)
    return b"".join(chunks)

def _check_skew(client_created_at: str) -> None:
    parsed = datetime.strptime(client_created_at, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    delta = abs((datetime.now(timezone.utc) - parsed).total_seconds())
    if delta > MAX_SKEW_SECONDS:
        raise ValidationError(
            f"client_created_at is {int(delta)}s away from server time "
            f"(max {MAX_SKEW_SECONDS}s)"
        )

class PublishingService:
    def __init__(self, db: AsyncSession, storage: StorageProvider):
        self.db = db
        self.storage = storage
        self.creators = CreatorRepository(db)

    async def publish(
        self,
        *,
        upload: UploadFile,
        creator_id: uuid.UUID,
        key_id: str,
        client_created_at: str,
        signature: str,
    ) -> PublishResponse:
        # 1. Form-field validation
        try:
            validate_client_created_at(client_created_at)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        _check_skew(client_created_at)

        # 2. Creator + key
        creator = await self.creators.get(creator_id)
        if creator is None:
            raise NotFoundError("creator not found")
        key = await self.creators.get_key(key_id)
        if key is None or key.creator_id != creator_id:
            raise NotFoundError("key not found for this creator")
        if key.status != "active":
            raise ValidationError("signing key is not active")

        # 3. Read + validate file
        data = await _read_capped(upload)
        try:
            mime = validate_bytes(data)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        original_filename = (upload.filename or "upload").strip() or "upload"

        # 4. Hashes
        sha256 = sha256_hex(data)
        phash = compute_perceptual_hash(data)

        # 5. Dedup within creator
        dup_stmt = (
            MediaAsset.__table__.select()
            .where(MediaAsset.creator_id == creator_id)
            .where(MediaAsset.sha256_hash == sha256)
        )
        existing = (await self.db.execute(dup_stmt)).first()
        if existing is not None:
            raise ConflictError(
                f"asset with this sha256 already published: {existing.id}"
            )

        # 6. Canonical payload + signature verification
        canonical = build_canonical_payload(
            asset_sha256=sha256,
            client_created_at=client_created_at,
            creator_id=creator_id,
            file_size=len(data),
            key_id=key_id,
            mime_type=mime,
            original_filename=original_filename,
        )
        if not verify_ed25519(key.public_key, canonical.encode("utf-8"), signature):
            raise ValidationError("signature does not match canonical payload")

        # 7. Upload to storage
        ext = MIME_TO_EXT[mime]
        storage_key = f"{creator_id}/{sha256}{ext}"
        await self.storage.upload(storage_key, data, mime)

        # 8. Persist
        asset = MediaAsset(
            creator_id=creator_id,
            original_filename=original_filename,
            mime_type=mime,
            file_size=len(data),
            sha256_hash=sha256,
            perceptual_hash=phash,
            storage_key=storage_key,
            storage_provider=settings.storage_provider,
            asset_status="published",
            client_created_at=datetime.fromisoformat(
                client_created_at.replace("Z", "+00:00")
            ),
            signed_payload=canonical,
            signature=signature,
            signer_key_id=key_id,
        )
        self.db.add(asset)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            await self.storage.delete(storage_key)
            raise ConflictError("asset already exists") from exc

        await self.db.refresh(asset)

        preview = await self.storage.get_url(storage_key)
        return PublishResponse(
            asset_id=asset.id,
            sha256=sha256,
            perceptual_hash=phash,
            status=asset.asset_status,
            verification_url=f"/verify?asset_id={asset.id}",
            preview_url=preview,
            canonical_payload=canonical,
            signature_verified=True,
        )