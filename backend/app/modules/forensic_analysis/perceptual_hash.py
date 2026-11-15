import io

try:
    from PIL import Image
    import imagehash as _imagehash
except ImportError:                       # pragma: no cover
    Image = None
    _imagehash = None

def compute_perceptual_hash(data: bytes) -> str | None:
    if _imagehash is None:
        return None
    try:
        with Image.open(io.BytesIO(data)) as im:
            return str(_imagehash.phash(im))
    except Exception:
        return None