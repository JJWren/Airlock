import pytest
from app.core.config import settings

def test_settings_load_from_env():
    """Verify that NVD_API_KEY is actually being pulled from the .env file."""
    assert settings.nvd_api_key is not None
    assert len(settings.nvd_api_key) > 0
    # Add a check for your specific app name
    assert settings.app_name == "Airlock"
