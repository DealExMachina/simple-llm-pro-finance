import pytest
from unittest.mock import AsyncMock, patch

from app.middleware import api_key_guard
from app.config import settings


@pytest.mark.asyncio
async def test_api_key_guard_no_key_configured():
    """Test middleware allows requests when no API key is configured."""
    request = AsyncMock()
    request.headers = {}
    call_next = AsyncMock()
    
    with patch.object(settings, 'service_api_key', None):
        response = await api_key_guard(request, call_next)
        call_next.assert_called_once_with(request)
        assert response == call_next.return_value


@pytest.mark.asyncio
async def test_api_key_guard_valid_x_api_key():
    """Test middleware allows requests with valid x-api-key header."""
    request = AsyncMock()
    request.headers = {"x-api-key": "secret-key"}
    call_next = AsyncMock()
    
    with patch.object(settings, 'service_api_key', 'secret-key'):
        response = await api_key_guard(request, call_next)
        call_next.assert_called_once_with(request)
        assert response == call_next.return_value


@pytest.mark.asyncio
async def test_api_key_guard_valid_authorization():
    """Test middleware allows requests with valid Authorization header."""
    request = AsyncMock()
    request.headers = {"authorization": "Bearer secret-key"}
    call_next = AsyncMock()
    
    with patch.object(settings, 'service_api_key', 'secret-key'):
        response = await api_key_guard(request, call_next)
        call_next.assert_called_once_with(request)
        assert response == call_next.return_value


@pytest.mark.asyncio
async def test_api_key_guard_invalid_key():
    """Test middleware rejects requests with invalid API key."""
    request = AsyncMock()
    request.headers = {"x-api-key": "wrong-key"}
    call_next = AsyncMock()
    
    with patch.object(settings, 'service_api_key', 'secret-key'):
        response = await api_key_guard(request, call_next)
        call_next.assert_not_called()
        assert response.status_code == 401
        assert response.body.decode() == '{"error":"unauthorized"}'


@pytest.mark.asyncio
async def test_api_key_guard_no_headers():
    """Test middleware rejects requests with no API key headers."""
    request = AsyncMock()
    request.headers = {}
    call_next = AsyncMock()
    
    with patch.object(settings, 'service_api_key', 'secret-key'):
        response = await api_key_guard(request, call_next)
        call_next.assert_not_called()
        assert response.status_code == 401
