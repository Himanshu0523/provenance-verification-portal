import io
import re
from app.core.config import settings

RFC3339_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}

def detect_mime(head: bytes) -> str | None:
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if len(head) >= 12 and head[0:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    return None

def validate_bytes(data: bytes) -> str:
    """Returns the canonical mime_type. Raises ValueError on failure."""
    if not data:
        raise ValueError("empty file")
    if len(data) > settings.max_upload_bytes:
        raise ValueError(f"file exceeds {settings.max_upload_bytes} bytes")
    mime = detect_mime(data[:16])
    if mime is None:
        raise ValueError("unsupported or unrecognized file type")
    if mime not in settings.allowed_mime_set:
        raise ValueError(f"mime type {mime} is not allowed")
    return mime

def validate_client_created_at(value: str) -> None:
    if not RFC3339_Z.match(value):
        raise ValueError("client_created_at must be RFC 3339 with Z suffix")