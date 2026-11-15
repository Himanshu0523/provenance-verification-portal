from fastapi import APIRouter
from app.api.v1.endpoints import health, creators, publish

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(creators.router)
api_router.include_router(publish.router)