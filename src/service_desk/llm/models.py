from dataclasses import dataclass, field
from typing import Any, Literal

MessageRole = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments_json: str


@dataclass(frozen=True)
class ChatMessage:
    role: MessageRole
    content: str | None
    tool_calls: tuple[ToolCall, ...] = field(default_factory=tuple)
    tool_call_id: str | None = None

    @classmethod
    def system(cls, content: str) -> "ChatMessage":
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str) -> "ChatMessage":
        return cls(role="user", content=content)

    @classmethod
    def assistant(
        cls,
        content: str | None,
        *,
        tool_calls: tuple[ToolCall, ...] = (),
    ) -> "ChatMessage":
        return cls(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )

    @classmethod
    def tool(
        cls,
        *,
        tool_call_id: str,
        content: str,
    ) -> "ChatMessage":
        return cls(
            role="tool",
            content=content,
            tool_call_id=tool_call_id,
        )


@dataclass(frozen=True)
class ModelReply:
    message: ChatMessage
    finish_reason: str | None
