"""Tests for Transformers provider."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import torch

from app.providers.transformers_provider import list_models, chat, is_model_ready, TransformersProvider


@pytest.mark.asyncio
async def test_list_models_success():
    """Test successful model listing."""
    result = await list_models()
    
    assert "object" in result
    assert result["object"] == "list"
    assert "data" in result
    assert len(result["data"]) > 0
    assert result["data"][0]["object"] == "model"


@pytest.mark.asyncio
async def test_list_models_structure():
    """Test model listing returns correct structure."""
    result = await list_models()
    
    model = result["data"][0]
    assert "id" in model
    assert "object" in model
    assert "owned_by" in model
    assert model["object"] == "model"


@pytest.mark.asyncio
async def test_chat_with_mock_model():
    """Test chat completion with mocked model."""
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "hello"}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    # Mock the global model and tokenizer
    mock_tokenizer = MagicMock()
    mock_tokenizer.apply_chat_template.return_value = "formatted prompt"
    mock_tokenizer.encode.return_value = [1, 2, 3]
    mock_tokenizer.decode.return_value = "test response"
    mock_tokenizer.__call__.return_value = {
        "input_ids": torch.tensor([[1, 2, 3]]),
        "attention_mask": torch.tensor([[1, 1, 1]])
    }
    
    mock_model = MagicMock()
    mock_outputs = MagicMock()
    mock_outputs[0] = torch.tensor([[1, 2, 3, 4, 5]])
    mock_model.generate.return_value = mock_outputs
    mock_model.get_input_embeddings.return_value.num_embeddings = 1000
    
    with patch('app.providers.transformers_provider.model', mock_model), \
         patch('app.providers.transformers_provider.tokenizer', mock_tokenizer), \
         patch('app.providers.transformers_provider.is_model_ready', return_value=True), \
         patch('app.providers.transformers_provider._initialized', True):
        
        result = await chat(payload, stream=False)
        
        assert "id" in result
        assert "object" in result
        assert result["object"] == "chat.completion"
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "usage" in result


@pytest.mark.asyncio
async def test_chat_streaming():
    """Test chat completion with streaming."""
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "hello"}],
        "stream": True
    }
    
    # Mock for streaming
    mock_tokenizer = MagicMock()
    mock_tokenizer.apply_chat_template.return_value = "formatted prompt"
    mock_tokenizer.__call__.return_value = {
        "input_ids": torch.tensor([[1, 2, 3]]),
        "attention_mask": torch.tensor([[1, 1, 1]])
    }
    
    with patch('app.providers.transformers_provider.model', MagicMock()), \
         patch('app.providers.transformers_provider.tokenizer', mock_tokenizer), \
         patch('app.providers.transformers_provider.is_model_ready', return_value=True), \
         patch('app.providers.transformers_provider._initialized', True):
        
        result = await chat(payload, stream=True)
        
        # Should return an async iterator
        assert hasattr(result, '__aiter__')


def test_is_model_ready_false_when_not_initialized():
    """Test is_model_ready returns False when model not initialized."""
    with patch('app.providers.transformers_provider._initialized', False), \
         patch('app.providers.transformers_provider.model', None), \
         patch('app.providers.transformers_provider.tokenizer', None):
        
        assert is_model_ready() is False


def test_is_model_ready_true_when_initialized():
    """Test is_model_ready returns True when model is initialized."""
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    
    with patch('app.providers.transformers_provider._initialized', True), \
         patch('app.providers.transformers_provider.model', mock_model), \
         patch('app.providers.transformers_provider.tokenizer', mock_tokenizer):
        
        assert is_model_ready() is True


def test_provider_format_tools_for_prompt():
    """Test tool formatting for prompt."""
    provider = TransformersProvider()
    tools = [
        {
            "function": {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {"type": "object", "properties": {}}
            }
        }
    ]
    
    result = provider._format_tools_for_prompt(tools)
    
    assert "test_tool" in result
    assert "CRITICAL" in result
    assert "<tool_call>" in result


def test_provider_remove_reasoning_tags():
    """Test reasoning tag removal."""
    provider = TransformersProvider()
    
    text_with_tags = "<think>Some reasoning</think>Actual answer"
    result = provider._remove_reasoning_tags(text_with_tags)
    
    assert "<think>" not in result
    assert "Actual answer" in result


def test_provider_extract_json_by_brace_matching():
    """Test JSON extraction by brace matching."""
    provider = TransformersProvider()
    
    text = "Some text {\"key\": \"value\"} more text"
    result = provider._extract_json_by_brace_matching(text)
    
    assert result is not None
    assert "key" in result
    assert "value" in result
