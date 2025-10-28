from typing import List, Literal, Optional
from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant", "tool"]


class Message(BaseModel):
    role: Role
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = Field(default=None, alias="max_tokens")
    stream: Optional[bool] = False


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


