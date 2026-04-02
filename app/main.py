from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.scanner import api_router
from app.core.config import get_settings

settings = get_settings()

def get_application() -> FastAPI:
    """Factory function to initialize the FastAPI app."""
    _app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    # 1. Set up Middleware (Essential for modern APIs)
    _app.add_middleware(
        CORSMiddleware,
        # allow_origins=settings.allowed_hosts,
        allow_origins=["http://localhost","http://localhost:3000","http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Include Routers
    _app.include_router(api_router, prefix=settings.api_v1_str)

    return _app

app = get_application()
