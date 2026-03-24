import os
from pathlib import Path
from functools import lru_cache
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    """System configuration settings class."""

    # These fields match the .env keys (Pydantic is case-insensitive)
    app_name: Optional[str] = None
    app_version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    nvd_api_key: Optional[str] = None
    syft_binary_path: Optional[str] = None
    allowed_hosts: list[str] = ["http://localhost:8000"]

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Allows ALLOWED_HOSTS to be a comma-separated string in .env."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

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
