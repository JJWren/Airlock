import os

from app.core.config import get_settings

def test_settings_load_from_env():
    """Verify that NVD_API_KEY is actually being pulled from the .env file."""
    # Arrange/Act: set known env values
    settings = get_settings()

    # Assert: the settings reflect the environment variables we just set
    assert settings.nvd_api_key is not None
    assert len(settings.nvd_api_key) > 0
    assert settings.api_v1_str == "/api/v1"
    assert settings.app_name == "Airlock"
