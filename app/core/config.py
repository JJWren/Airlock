import os
from pathlib import Path
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    """System configuration settings class."""

    # These fields match the .env keys (Pydantic is case-insensitive)
    app_name: Optional[str] = None
    api_v1_str: Optional[str] = None
    nvd_api_key: Optional[str] = None

    # This inner class tells Pydantic WHERE to look for the secrets
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance for use as a FastAPI dependency."""
    return Settings()
# test message