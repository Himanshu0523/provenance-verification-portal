import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.models import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def write(
        self, *,
        event_type: str,
        actor_id: uuid.UUID | None,
        asset_id: uuid.UUID | None,
        event_data: dict,
    ) -> AuditLog:
        entry = AuditLog(
            event_type=event_type,
            actor_id=actor_id,
            asset_id=asset_id,
            event_data=event_data,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry