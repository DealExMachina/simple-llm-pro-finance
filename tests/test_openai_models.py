import pytest
from unittest.mock import patch, AsyncMock

from app.models.openai import (
    Message, ChatCompletionRequest, ChoiceMessage, 
    Choice, Usage, ChatCompletionResponse
)


def test_message_model():
    """Test Message Pydantic model."""
    message = Message(role="user", content="Hello")
    
    assert message.role == "user"
    assert message.content == "Hello"


def test_message_invalid_role():
    """Test Message with invalid role."""
    with pytest.raises(ValueError):
        Message(role="invalid", content="Hello")


def test_chat_completion_request_model():
    """Test ChatCompletionRequest Pydantic model."""
    messages = [
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Hello")
    ]
    
    request = ChatCompletionRequest(
        model="test-model",
        messages=messages,
        temperature=0.7,
        max_tokens=100,
        stream=False
    )
    
    assert request.model == "test-model"
    assert len(request.messages) == 2
    assert request.temperature == 0.7
    assert request.max_tokens == 100
    assert request.stream is False


def test_chat_completion_request_defaults():
    """Test ChatCompletionRequest with default values."""
    messages = [Message(role="user", content="Hello")]
    
    request = ChatCompletionRequest(
        model="test-model",
        messages=messages
    )
    
    assert request.model == "test-model"
    assert request.temperature == 0.2
    assert request.max_tokens is None
    assert request.stream is False


def test_choice_message_model():
    """Test ChoiceMessage Pydantic model."""
    message = ChoiceMessage(role="assistant", content="Hi there!")
    
    assert message.role == "assistant"
    assert message.content == "Hi there!"


def test_choice_message_optional_content():
    """Test ChoiceMessage with optional content."""
    message = ChoiceMessage(role="assistant")
    
    assert message.role == "assistant"
    assert message.content is None


def test_choice_model():
    """Test Choice Pydantic model."""
    message = ChoiceMessage(role="assistant", content="Response")
    choice = Choice(
        index=0,
        message=message,
        finish_reason="stop"
    )
    
    assert choice.index == 0
    assert choice.message == message
    assert choice.finish_reason == "stop"


def test_choice_optional_finish_reason():
    """Test Choice with optional finish_reason."""
    message = ChoiceMessage(role="assistant", content="Response")
    choice = Choice(index=0, message=message)
    
    assert choice.index == 0
    assert choice.message == message
    assert choice.finish_reason is None


def test_usage_model():
    """Test Usage Pydantic model."""
    usage = Usage(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15
    )
    
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 5
    assert usage.total_tokens == 15


def test_chat_completion_response_model():
    """Test ChatCompletionResponse Pydantic model."""
    message = ChoiceMessage(role="assistant", content="Response")
    choice = Choice(index=0, message=message, finish_reason="stop")
    usage = Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    
    response = ChatCompletionResponse(
        id="cmpl-123",
        created=1234567890,
        model="test-model",
        choices=[choice],
        usage=usage
    )
    
    assert response.id == "cmpl-123"
    assert response.object == "chat.completion"
    assert response.created == 1234567890
    assert response.model == "test-model"
    assert len(response.choices) == 1
    assert response.usage == usage


def test_chat_completion_response_optional_usage():
    """Test ChatCompletionResponse with optional usage."""
    message = ChoiceMessage(role="assistant", content="Response")
    choice = Choice(index=0, message=message, finish_reason="stop")
    
    response = ChatCompletionResponse(
        id="cmpl-123",
        created=1234567890,
        model="test-model",
        choices=[choice]
    )
    
    assert response.id == "cmpl-123"
    assert response.usage is None


def test_model_serialization():
    """Test model serialization to dict."""
    messages = [Message(role="user", content="Hello")]
    request = ChatCompletionRequest(
        model="test-model",
        messages=messages,
        temperature=0.5
    )
    
    data = request.model_dump()
    
    assert data["model"] == "test-model"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][0]["content"] == "Hello"
    assert data["temperature"] == 0.5
