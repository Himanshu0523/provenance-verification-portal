import uuid
from datetime import datetime
from sqlalchemy import (
    String, BigInteger, DateTime, ForeignKey, func, UniqueConstraint, Index, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class MediaAsset(Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        UniqueConstraint("creator_id", "sha256_hash", name="uq_creator_sha256"),
        Index("ix_media_assets_sha256", "sha256_hash"),
        Index("ix_media_assets_perceptual", "perceptual_hash"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("creators.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    parent_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    perceptual_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(32), default="r2", nullable=False)
    asset_status: Mapped[str] = mapped_column(
        String(20), default="published", nullable=False
    )
    client_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    signed_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    signer_key_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, index=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    creator: Mapped["Creator"] = relationship(
        back_populates="assets", foreign_keys=[creator_id]
    )
    embedding: Mapped["MediaEmbedding | None"] = relationship(
        back_populates="asset", uselist=False, cascade="all, delete-orphan"
    )