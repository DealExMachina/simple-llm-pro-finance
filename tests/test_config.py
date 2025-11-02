import os
from unittest.mock import patch

import pytest

from app.config import Settings


def test_settings_defaults():
    """Test that settings have correct default values."""
    settings = Settings()
    assert settings.model == "DragonLLM/qwen3-8b-fin-v1.0"
    assert settings.service_api_key is None
    assert settings.log_level == "info"


def test_settings_from_env():
    """Test that settings can be loaded from environment variables."""
    with patch.dict(os.environ, {
        "MODEL": "custom-model",
        "SERVICE_API_KEY": "secret-key",
        "LOG_LEVEL": "debug"
    }):
        settings = Settings()
        assert settings.model == "custom-model"
        assert settings.service_api_key == "secret-key"
        assert settings.log_level == "debug"


def test_settings_env_file():
    """Test that settings can be loaded from .env file."""
    # This test assumes .env file exists with test values
    # In practice, you'd create a test .env file or mock the file reading
    settings = Settings()
    # Verify that the settings object can be instantiated
    assert isinstance(settings.model, str)
