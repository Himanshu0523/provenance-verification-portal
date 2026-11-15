import asyncio
from pathlib import Path

class LocalStorageProvider:
    """Dev-only provider writing under LOCAL_STORAGE_DIR and served by FastAPI."""

    def __init__(self, root: Path, public_base: str, app_base: str):
        self.root = root
        self.public_base = public_base.rstrip("/")
        self.app_base = app_base.rstrip("/")
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        p = (self.root / key).resolve()
        if not str(p).startswith(str(self.root.resolve())):
            raise ValueError("path traversal")
        return p

    async def upload(self, key: str, data: bytes, content_type: str) -> None:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(p.write_bytes, data)

    async def delete(self, key: str) -> None:
        p = self._path(key)
        await asyncio.to_thread(lambda: p.unlink(missing_ok=True))

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        return f"{self.app_base}{self.public_base}/{key}"