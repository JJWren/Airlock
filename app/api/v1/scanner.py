from fastapi import APIRouter
from app.api.v1.endpoints import scan, system

# This becomes the single entry point for all V1 routes
api_router = APIRouter()

# System/Utility routes (no prefix needed, stays at /api/v1/health)
api_router.include_router(system.router)

# Scanning routes (stays at /api/v1/scan)
api_router.include_router(scan.router, tags=["Vulnerability Scanning"])

# If you add more endpoints later (e.g., /reports, /users, etc.),
# you just add them here!
