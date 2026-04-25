from typing import Literal

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class AssistantRequest(BaseModel):
    user_utterance: str = Field(min_length=1)
    caller_phone: str | None = Field(default=None, max_length=20)
    conversation_history: list[ConversationMessage] = Field(default_factory=list)


class ToolResult(BaseModel):
    tool_name: str
    result: dict


class AssistantResponse(BaseModel):
    assistant_text: str
    tools_used: list[str]
    tool_results: list[ToolResult]
