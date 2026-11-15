import base64
import binascii
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

RAW_PUBLIC_KEY_LEN = 32
RAW_SIGNATURE_LEN = 64

def b64decode_strict(value: str) -> bytes:
    """Accept standard or urlsafe base64, with or without padding."""
    if not isinstance(value, str) or not value:
        raise ValueError("empty value")
    v = value.strip().replace("-", "+").replace("_", "/")
    v += "=" * (-len(v) % 4)
    try:
        return base64.b64decode(v, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("invalid base64") from exc

def load_public_key(public_key_b64: str) -> Ed25519PublicKey:
    raw = b64decode_strict(public_key_b64)
    if len(raw) != RAW_PUBLIC_KEY_LEN:
        raise ValueError(
            f"Ed25519 public key must be {RAW_PUBLIC_KEY_LEN} raw bytes, "
            f"got {len(raw)}"
        )
    return Ed25519PublicKey.from_public_bytes(raw)

def verify_ed25519(public_key_b64: str, payload: bytes, signature_b64: str) -> bool:
    try:
        key = load_public_key(public_key_b64)
        sig = b64decode_strict(signature_b64)
    except ValueError:
        return False
    if len(sig) != RAW_SIGNATURE_LEN:
        return False
    try:
        key.verify(sig, payload)
        return True
    except InvalidSignature:
        return False