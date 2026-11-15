from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import DomainError
from app.api.v1.router import api_router

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )

# Mount dev static files if using local storage
if settings.storage_provider == "local":
    Path(settings.local_storage_dir).mkdir(parents=True, exist_ok=True)
    app.mount(
        settings.local_storage_public_base,
        StaticFiles(directory=settings.local_storage_dir),
        name="media",
    )

app.include_router(api_router, prefix=settings.api_v1_prefix)