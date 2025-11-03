"""OpenAI-compatible API models using Pydantic."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant", "tool"]


class Message(BaseModel):
    """A single message in a conversation.
    
    Attributes:
        role: The role of the message sender
        content: The text content of the message
    """
    role: Role
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """Request model for chat completions endpoint.
    
    Attributes:
        model: Optional model identifier (uses default from config if not provided)
        messages: List of messages in the conversation
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response
        top_p: Nucleus sampling parameter
    """
    model: Optional[str] = Field(default=None, description="Model identifier")
    messages: List[Message] = Field(..., description="Conversation messages")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(default=False, description="Stream response")
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")


class ChoiceMessage(BaseModel):
    """Assistant message in a completion choice.
    
    Attributes:
        role: Always "assistant" for completion messages
        content: The generated message content
    """
    role: Literal["assistant"] = "assistant"
    content: Optional[str] = Field(default=None, description="Generated message content")


class Choice(BaseModel):
    """A single completion choice.
    
    Attributes:
        index: Choice index
        message: The generated message
        finish_reason: Reason why generation finished (stop, length, etc.)
    """
    index: int = Field(..., description="Choice index")
    message: ChoiceMessage = Field(..., description="Generated message")
    finish_reason: Optional[str] = Field(default=None, description="Reason for completion")


class Usage(BaseModel):
    """Token usage statistics.
    
    Attributes:
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Total tokens used
    """
    prompt_tokens: int = Field(..., ge=0, description="Tokens in prompt")
    completion_tokens: int = Field(..., ge=0, description="Tokens in completion")
    total_tokens: int = Field(..., ge=0, description="Total tokens used")


class ChatCompletionResponse(BaseModel):
    """Response model for chat completions endpoint.
    
    Attributes:
        id: Unique completion ID
        object: Always "chat.completion"
        created: Unix timestamp of creation
        model: Model identifier used
        choices: List of completion choices
        usage: Optional token usage statistics
    """
    id: str = Field(..., description="Completion ID")
    object: Literal["chat.completion"] = Field(default="chat.completion", description="Object type")
    created: int = Field(..., description="Unix timestamp")
    model: str = Field(..., description="Model identifier")
    choices: List[Choice] = Field(..., description="Completion choices")
    usage: Optional[Usage] = Field(default=None, description="Token usage statistics")


