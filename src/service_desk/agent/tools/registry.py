import logging
from collections.abc import Iterable

from pydantic import ValidationError

from service_desk.agent.tools.base import AgentTool, ToolResult
from service_desk.domain.exceptions import BusinessError
from service_desk.llm.models import ToolCall, ToolDefinition

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self, tools: Iterable[AgentTool]) -> None:
        self._tools: dict[str, AgentTool] = {}

        for tool in tools:
            name = tool.definition.name

            if name in self._tools:
                raise ValueError(f"工具重复注册: {name}")

            self._tools[name] = tool

    @property
    def definitions(self) -> list[ToolDefinition]:
        return [tool.definition for tool in self._tools.values()]

    def execute(self, call: ToolCall) -> ToolResult:
        tool = self._tools.get(call.name)

        if tool is None:
            return ToolResult(
                success=False,
                error_code="TOOL_NOT_FOUND",
                message=f"未注册工具: {call.name}",
            )

        try:
            return tool.execute(call.arguments_json)
        except ValidationError as exc:
            return ToolResult(
                success=False,
                error_code="INVALID_TOOL_ARGUMENTS",
                message="工具参数校验失败",
                data={"errors": exc.errors()},
            )
        except BusinessError as exc:
            return ToolResult(
                success=False,
                error_code=type(exc).__name__,
                message=str(exc),
            )
        except Exception:
            logger.exception("工具执行发生未预期异常", extra={"tool": call.name})

            return ToolResult(
                success=False,
                error_code="TOOL_INTERNAL_ERROR",
                message="工具执行失败",
            )
