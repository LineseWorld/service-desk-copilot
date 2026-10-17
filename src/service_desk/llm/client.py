from collections.abc import Sequence
from typing import Any, cast

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)
from openai.types.chat import ChatCompletionMessageParam

from service_desk.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMResponseError,
)
from service_desk.llm.interfaces import LLMClient
from service_desk.llm.models import (
    ChatMessage,
    ModelReply,
    ToolCall,
    ToolDefinition,
)


class OpenAICompatibleLLMClient(LLMClient):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
    ) -> None:
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,
            max_retries=0,
        )

        self._model = model

    @property
    def model(self) -> str:
        return self._model

    def complete(
        self,
        *,
        messages: Sequence[ChatMessage],
        tools: Sequence[ToolDefinition],
    ) -> ModelReply:

        provider_message = cast(
            list[ChatCompletionMessageParam],
            [self._serialize_message(message) for message in messages],
        )

        provider_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools
        ]
        try:
            if provider_tools:
                completion = self._client.chat.completions.create(
                    model=self._model,
                    messages=provider_message,
                    tools=provider_tools,
                    tool_choice="auto",
                )
            else:
                completion = self._client.chat.completions.create(
                    model=self._model,
                    messages=provider_message,
                )

            if not completion.choices:
                raise LLMResponseError("模型API没有返回choices")

            message = completion.choices[0].message

            tool_calls = tuple(
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments_json=call.function.arguments,
                )
                for call in message.tool_calls or []
            )

            return ModelReply(
                message=ChatMessage.assistant(
                    message.content,
                    tool_calls=tool_calls,
                ),
                finish_reason=completion.choices[0].finish_reason,
            )
        except AuthenticationError as exc:
            raise LLMAuthenticationError("模型API认证失败，请检查API Key") from exc
        except RateLimitError as exc:
            raise LLMRateLimitError("模型API达到频率或额度限制") from exc
        except APIConnectionError as exc:
            raise LLMConnectionError("无法连接模型API，请检查网络和Base URL") from exc
        except APIStatusError as exc:
            raise LLMResponseError(f"模型API返回错误状态码: {exc.status_code}") from exc

    def _serialize_message(
        self,
        message: ChatMessage,
    ) -> dict[str, Any]:
        if message.role in {"system", "user"}:
            return {"role": message.role, "content": message.content or ""}

        if message.role == "assistant":
            result: dict[str, Any] = {
                "role": "assistant",
                "content": message.content,
            }

            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": call.arguments_json,
                        },
                    }
                    for call in message.tool_calls
                ]

            return result

        if message.role == "tool":
            if message.tool_call_id is None:
                raise ValueError("tool消息缺少tool_call_id")

            return {
                "role": "tool",
                "tool_call_id": message.tool_call_id,
                "content": message.content or "",
            }

        raise ValueError(f"不支持的消息角色: {message.role}")
