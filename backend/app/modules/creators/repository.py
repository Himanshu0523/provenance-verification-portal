import uuid
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.creators.models import Creator, CreatorKey

class CreatorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, display_name: str, email: str | None = None) -> Creator:
        creator = Creator(display_name=display_name, email=email)
        self.db.add(creator)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            raise ValueError("email already registered") from exc
        await self.db.refresh(creator)
        return creator

    async def get(self, creator_id: uuid.UUID) -> Creator | None:
        return await self.db.get(Creator, creator_id)

    async def list_keys(self, creator_id: uuid.UUID) -> list[CreatorKey]:
        stmt = (
            select(CreatorKey)
            .where(CreatorKey.creator_id == creator_id)
            .order_by(CreatorKey.created_at.desc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_key(self, key_id: str) -> CreatorKey | None:
        stmt = select(CreatorKey).where(CreatorKey.key_id == key_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def add_key(self, **kwargs) -> CreatorKey:
        key = CreatorKey(**kwargs)
        self.db.add(key)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            raise ValueError("public key already registered") from exc
        await self.db.refresh(key)
        return key