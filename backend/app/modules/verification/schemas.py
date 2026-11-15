import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Verdict = Literal[
    "verified", "key_revoked", "signature_invalid", "invalid_manifest", "unknown",
]

class MatchDetail(BaseModel):
    asset_id: uuid.UUID
    creator_id: uuid.UUID
    creator_display_name: str
    key_id: str
    key_status: str
    signature_valid: bool
    manifest_ok: bool
    per_asset_verdict: Verdict
    signed_at: datetime
    original_filename: str
    mime_type: str
    file_size: int
    sha256: str
    preview_url: str
    signature_checked_against: str

class VerifyResponse(BaseModel):
    query_sha256: str
    verdict: Verdict
    total_matches: int
    audit_id: uuid.UUID | None
    matches: list[MatchDetail]