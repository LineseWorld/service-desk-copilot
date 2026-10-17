from typing import Any, Protocol

from pydantic import BaseModel

from service_desk.llm.models import ToolDefinition


class ToolResult(BaseModel):
    success: bool
    data: Any = None
    error_code: str | None = None
    message: str | None = None


class AgentTool(Protocol):
    @property
    def definition(self) -> ToolDefinition: ...

    def execute(self, arguments_json: str) -> ToolResult: ...
