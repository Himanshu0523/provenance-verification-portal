from pathlib import Path
from app.core.config import settings
from .base import StorageProvider
from .local_provider import LocalStorageProvider
from .r2_provider import R2StorageProvider



def get_storage() -> StorageProvider:
    if settings.storage_provider == "r2":
        return R2StorageProvider(
            account_id=settings.r2_account_id,
            access_key_id=settings.r2_access_key_id,
            secret_access_key=settings.r2_secret_access_key,
            bucket=settings.r2_bucket_name,
            endpoint_url=settings.r2_endpoint_url,
        )
    return LocalStorageProvider(
        root=Path(settings.local_storage_dir),
        public_base=settings.local_storage_public_base,
        app_base=settings.app_public_base_url,
    )