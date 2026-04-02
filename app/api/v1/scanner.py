from fastapi import APIRouter
from app.api.v1.endpoints import scan, system, logs, report

# This becomes the single entry point for all V1 routes
api_router = APIRouter()

api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(scan.router, prefix="/scan", tags=["Scanning"])
api_router.include_router(logs.router, prefix="/logs", tags=["Telemetry"])
api_router.include_router(report.router, prefix="/report", tags=["Reporting"])
