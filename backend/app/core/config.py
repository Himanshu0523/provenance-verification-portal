from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env" , env_file_encoding = "utf-8",
        case_sensitive=False , extra= "ignore",
    )
    
    app_name:str = "Provenace Verification Portal"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    
    database_url: str = (
        "postgresql+asyncpg://postgre:postgre@localhost:5432/provenance_db"
    )
    secret_key: str = "change_me"
    
    cors_origins: str = "http://localhost:3000"
    
    clip_model_name: str = "clip-ViT-B-32"
    clip_embedding_dim: int = 512
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
    
    
    # Uploads
    max_upload_bytes: int = 20 * 1024 * 1024
    allowed_mime_types: str = "image/png,image/jpeg,image/webp"
    app_public_base_url: str = "http://localhost:8000"

    # Storage
    storage_provider: str = "local"            # "local" | "r2"
    local_storage_dir: str = "storage"
    local_storage_public_base: str = "/media"
    
    # Verification
    verify_max_bytes: int = 20 * 1024 * 1024
    verify_audit_enabled: bool = True

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_endpoint_url: str = ""
    
    @property
    def allowed_mime_set(self) -> set[str]:
        return {m.strip() for m in self.allowed_mime_types.split(",") if m.strip()}    
    

settings = Settings()