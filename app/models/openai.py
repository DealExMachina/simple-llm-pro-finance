from typing import List, Literal, Optional
from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant", "tool"]


class Message(BaseModel):
    role: Role
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None  # Optional, will use default from config
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0


class ChoiceMessage(BaseModel):
    role: Literal["assistant"]
    content: Optional[str] = None


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


