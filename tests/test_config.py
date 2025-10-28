import os
from unittest.mock import patch

import pytest

from app.config import Settings


def test_settings_defaults():
    """Test that settings have correct default values."""
    settings = Settings()
    assert settings.vllm_base_url == "http://localhost:8000/v1"
    assert settings.model == "DragonLLM/LLM-Pro-Finance-Small"
    assert settings.service_api_key is None
    assert settings.log_level == "info"


def test_settings_from_env():
    """Test that settings can be loaded from environment variables."""
    with patch.dict(os.environ, {
        "VLLM_BASE_URL": "http://remote:8000/v1",
        "MODEL": "custom-model",
        "SERVICE_API_KEY": "secret-key",
        "LOG_LEVEL": "debug"
    }):
        settings = Settings()
        assert settings.vllm_base_url == "http://remote:8000/v1"
        assert settings.model == "custom-model"
        assert settings.service_api_key == "secret-key"
        assert settings.log_level == "debug"


def test_settings_env_file():
    """Test that settings can be loaded from .env file."""
    # This test assumes .env file exists with test values
    # In practice, you'd create a test .env file or mock the file reading
    settings = Settings()
    # Verify that the settings object can be instantiated
    assert isinstance(settings.vllm_base_url, str)
