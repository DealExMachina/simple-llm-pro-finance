import pytest
from unittest.mock import patch, AsyncMock
import httpx

from app.providers.vllm import list_models, chat


@pytest.mark.asyncio
async def test_list_models_success():
    """Test successful model listing."""
    mock_response = {"data": [{"id": "test-model"}]}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response_obj
        
        result = await list_models()
        assert result == mock_response


@pytest.mark.asyncio
async def test_chat_success():
    """Test successful chat completion."""
    payload = {"model": "test", "messages": [{"role": "user", "content": "hello"}]}
    mock_response = {"choices": [{"message": {"content": "hi"}}]}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response_obj
        
        result = await chat(payload, stream=False)
        assert result == mock_response


@pytest.mark.asyncio
async def test_chat_stream():
    """Test chat completion with streaming."""
    payload = {"model": "test", "messages": [{"role": "user", "content": "hello"}]}
    mock_stream = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.stream.return_value = mock_stream
        
        result = await chat(payload, stream=True)
        assert result == mock_stream
