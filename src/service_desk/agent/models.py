from dataclasses import dataclass

from service_desk.agent.tools.base import ToolResult


@dataclass(frozen=True)
class ToolExecutionTrace:
    step: int
    tool_call_id: str
    tool_name: str
    arguments_json: str
    result: ToolResult


@dataclass(frozen=True)
class AgentRunResult:
    answer: str
    steps: int
    tool_executions: tuple[ToolExecutionTrace, ...]
