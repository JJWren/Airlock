from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/health", tags=["System"])
async def health_check():
    """Returns the system status and version from the central settings."""
    return {
        "status": "online",
        "version": settings.app_version
    }