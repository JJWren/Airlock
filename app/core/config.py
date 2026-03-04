from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """System configuration settings class."""

    # These fields match the .env keys (Pydantic is case-insensitive)
    app_name: str = "Airlock"
    api_v1_str: str = "/api/v1"

    # This will be populated by NVD_API_KEY in your .env
    nvd_api_key: str

    # This inner class tells Pydantic WHERE to look for the secrets
    model_config = SettingsConfigDict(
        env_file=".env",    # Look for a file named .env
        env_file_encoding="utf-8",
        extra="ignore"      # Ignore extra variables in .env not defined here
    )

@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance for use as a FastAPI dependency."""
    return Settings()
