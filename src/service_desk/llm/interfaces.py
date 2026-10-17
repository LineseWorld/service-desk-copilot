from collections.abc import Sequence
from typing import Protocol

from service_desk.llm.models import (
    ChatMessage,
    ModelReply,
    ToolDefinition,
)


class LLMClient(Protocol):
    def complete(
        self,
        *,
        messages: Sequence[ChatMessage],
        tools: Sequence[ToolDefinition],
    ) -> ModelReply: ...
