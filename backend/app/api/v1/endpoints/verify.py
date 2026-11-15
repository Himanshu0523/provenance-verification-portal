from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.verification.schemas import VerifyResponse
from app.modules.verification.service import VerificationService

router = APIRouter(tags=["verification"])

def _svc(db: AsyncSession = Depends(get_db)) -> VerificationService:
    return VerificationService(db)

@router.post(
    "/verify", response_model=VerifyResponse,
    status_code=status.HTTP_200_OK,
)
async def verify(
    file: UploadFile = File(...),
    svc: VerificationService = Depends(_svc),
):
    return await svc.verify(upload=file)