import uuid
from pydantic import BaseModel

class PublishResponse(BaseModel):
    asset_id: uuid.UUID
    sha256: str
    perceptual_hash: str | None
    status: str
    verification_url: str
    preview_url: str
    canonical_payload: str
    signature_verified: bool