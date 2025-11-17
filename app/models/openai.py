from typing import List, Literal, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant", "tool"]


class Message(BaseModel):
    role: Role
    content: str


class Function(BaseModel):
    """Function definition for tool calls."""
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Tool(BaseModel):
    """Tool definition for OpenAI-compatible API."""
    type: Literal["function"] = "function"
    function: Function


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None  # Optional, will use default from config
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    tools: Optional[List[Tool]] = None  # ✅ Tool definitions
    tool_choice: Optional[Union[Literal["none", "auto"], Dict[str, Any]]] = None  # ✅ Tool choice


class FunctionCall(BaseModel):
    """Function call in tool call."""
    name: str
    arguments: str  # JSON string


class ToolCall(BaseModel):
    """Tool call in assistant message."""
    id: str
    type: Literal["function"] = "function"
    function: FunctionCall


class ChoiceMessage(BaseModel):
    role: Literal["assistant"]
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None  # ✅ Tool calls support


class Choice(BaseModel):
    index: int
    message: ChoiceMessage
    finish_reason: Optional[str] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None


