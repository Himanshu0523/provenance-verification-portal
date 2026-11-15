import json
import uuid

SCHEMA = "provenance/v1"

def build_canonical_payload(
    *,
    asset_sha256: str,
    client_created_at: str,
    creator_id: uuid.UUID | str,
    file_size: int,
    key_id: str,
    mime_type: str,
    original_filename: str,
) -> str:
    obj = {
        "schema": SCHEMA,
        "asset_sha256": asset_sha256,
        "creator_id": str(creator_id),
        "key_id": key_id,
        "original_filename": original_filename,
        "mime_type": mime_type,
        "file_size": int(file_size),
        "client_created_at": client_created_at,
    }
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)