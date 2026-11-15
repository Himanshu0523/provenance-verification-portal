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
    

settings = Settings()