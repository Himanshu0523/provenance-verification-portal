from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.media_assets.models import MediaAsset

class MediaAssetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> MediaAsset:
        asset = MediaAsset(**kwargs)
        self.db.add(asset)
        await self.db.flush()
        await self.db.refresh(asset)
        return asset

    async def get(self, asset_id: UUID) -> MediaAsset | None:
        return await self.db.get(MediaAsset, asset_id)

    async def find_by_sha256(self, sha256_hash: str) -> list[MediaAsset]:
        stmt = select(MediaAsset).where(MediaAsset.sha256_hash == sha256_hash)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())