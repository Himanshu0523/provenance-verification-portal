import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.creators.schemas import (
    CreatorCreate, CreatorRead, KeyRead, KeyRegister,
    SignatureVerifyRequest, SignatureVerifyResponse,
)
from app.modules.creators.service import CreatorService

router = APIRouter(prefix="/creators", tags=["creators"])

def _svc(db: AsyncSession = Depends(get_db)) -> CreatorService:
    return CreatorService(db)

@router.post("", response_model=CreatorRead, status_code=status.HTTP_201_CREATED)
async def register_creator(payload: CreatorCreate, svc: CreatorService = Depends(_svc)):
    return await svc.register(payload.display_name, payload.email)

@router.get("/{creator_id}", response_model=CreatorRead)
async def get_creator(creator_id: uuid.UUID, svc: CreatorService = Depends(_svc)):
    return await svc.get(creator_id)

@router.post(
    "/{creator_id}/keys", response_model=KeyRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_key(
    creator_id: uuid.UUID, payload: KeyRegister,
    svc: CreatorService = Depends(_svc),
):
    return await svc.register_key(
        creator_id, payload.public_key, payload.algorithm, payload.label
    )

@router.get("/{creator_id}/keys", response_model=list[KeyRead])
async def list_keys(creator_id: uuid.UUID, svc: CreatorService = Depends(_svc)):
    return await svc.list_keys(creator_id)

@router.post("/{creator_id}/keys/{key_id}/revoke", response_model=KeyRead)
async def revoke_key(
    creator_id: uuid.UUID, key_id: str,
    svc: CreatorService = Depends(_svc),
):
    return await svc.revoke_key(creator_id, key_id)

@router.post(
    "/{creator_id}/verify-signature", response_model=SignatureVerifyResponse,
)
async def verify_signature(
    creator_id: uuid.UUID, payload: SignatureVerifyRequest,
    svc: CreatorService = Depends(_svc),
):
    valid, key_id, reason = await svc.verify_signature(
        creator_id, payload.payload, payload.signature, payload.key_id
    )
    return SignatureVerifyResponse(valid=valid, key_id=key_id, reason=reason)