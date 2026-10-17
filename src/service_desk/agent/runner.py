from service_desk.agent.exceptions import (
    AgentEmptyResponse,
    AgentMaxStepsExceeded,
)
from service_desk.agent.models import AgentRunResult, ToolExecutionTrace
from service_desk.agent.prompts import SYSTEM_PROMPT
from service_desk.agent.tools.registry import ToolRegistry
from service_desk.llm.interfaces import LLMClient
from service_desk.llm.models import ChatMessage


class AgentRunner:
    def __init__(
        self,
        *,
        llm_client: LLMClient,
        tool_registry: ToolRegistry,
        max_steps: int = 8,
    ) -> None:
        self._llm_client = llm_client
        self._tool_registry = tool_registry
        self._max_steps = max_steps

    def run(
        self,
        *,
        user_message: str,
        history: list[ChatMessage] | None = None,
    ) -> AgentRunResult:
        messages = [
            ChatMessage.system(SYSTEM_PROMPT),
            *(history or []),
            ChatMessage.user(user_message),
        ]

        traces: list[ToolExecutionTrace] = []

        for step in range(1, self._max_steps + 1):
            reply = self._llm_client.complete(
                messages=messages,
                tools=self._tool_registry.definitions,
            )

            messages.append(reply.message)

            if not reply.message.tool_calls:
                content = reply.message.content

                if content is None or not content.strip():
                    raise AgentEmptyResponse("模型没有返回文本或工具调用")

                return AgentRunResult(
                    answer=content,
                    steps=step,
                    tool_executions=tuple(traces),
                )

            for call in reply.message.tool_calls:
                result = self._tool_registry.execute(call)

                traces.append(
                    ToolExecutionTrace(
                        step=step,
                        tool_call_id=call.id,
                        tool_name=call.name,
                        arguments_json=call.arguments_json,
                        result=result,
                    )
                )

                messages.append(
                    ChatMessage.tool(
                        tool_call_id=call.id,
                        content=result.model_dump_json(),
                    )
                )
        raise AgentMaxStepsExceeded(f"Agent超过最大执行轮数: {self._max_steps}")
