import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class CreatorCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None

class CreatorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    display_name: str
    email: str | None
    status: str
    created_at: datetime

class KeyRegister(BaseModel):
    public_key: str = Field(min_length=32, max_length=512)
    algorithm: str = "ed25519"
    label: str | None = Field(default=None, max_length=120)

    @field_validator("algorithm")
    @classmethod
    def _algo_only_ed25519(cls, v: str) -> str:
        if v.lower() != "ed25519":
            raise ValueError("only 'ed25519' is supported")
        return "ed25519"

class KeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    key_id: str
    algorithm: str
    status: str
    label: str | None = None
    created_at: datetime
    revoked_at: datetime | None

class SignatureVerifyRequest(BaseModel):
    payload: str = Field(min_length=1, max_length=65536)
    signature: str = Field(min_length=64, max_length=256)
    key_id: str | None = None

class SignatureVerifyResponse(BaseModel):
    valid: bool
    key_id: str
    reason: str | None = None