import uuid
from functools import lru_cache

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.integrations.storage import get_storage
from app.integrations.storage.base import StorageProvider
from app.modules.publishing.schemas import PublishResponse
from app.modules.publishing.service import PublishingService

router = APIRouter(tags=["publishing"])

def _svc(
    db: AsyncSession = Depends(get_db),
    storage: StorageProvider = Depends(get_storage),
) -> PublishingService:
    return PublishingService(db, storage)

@router.post(
    "/publish", response_model=PublishResponse,
    status_code=status.HTTP_201_CREATED,
)
async def publish(
    file: UploadFile = File(...),
    creator_id: uuid.UUID = Form(...),
    key_id: str = Form(...),
    client_created_at: str = Form(...),
    signature: str = Form(...),
    svc: PublishingService = Depends(_svc),
):
    return await svc.publish(
        upload=file,
        creator_id=creator_id,
        key_id=key_id,
        client_created_at=client_created_at,
        signature=signature,
    )