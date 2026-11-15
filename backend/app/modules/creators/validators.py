import hashlib
from app.core.security import b64decode_strict, load_public_key, RAW_PUBLIC_KEY_LEN

def validate_and_fingerprint(public_key_b64: str) -> tuple[bytes, str]:
    """Validate key format and return (raw_bytes, key_id_hex)."""
    try:
        raw = b64decode_strict(public_key_b64)
    except ValueError as exc:
        raise ValueError(f"public_key is not valid base64: {exc}") from exc
    if len(raw) != RAW_PUBLIC_KEY_LEN:
        raise ValueError(
            f"public_key must decode to {RAW_PUBLIC_KEY_LEN} bytes, got {len(raw)}"
        )
    load_public_key(public_key_b64)  # raises ValueError on bad point
    key_id = hashlib.sha256(raw).hexdigest()
    return raw, key_id