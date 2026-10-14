from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from service_desk.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMResponseError,
)


class OpenAICompatibleLLMClient:
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

    def complete(self, *, system_prompt: str, user_message: str) -> str:
        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_message,
                    },
                ],
            )
        except AuthenticationError as exc:
            raise LLMAuthenticationError("模型API认证失败，请检查API Key") from exc

        except RateLimitError as exc:
            raise LLMRateLimitError("模型API达到频率或额度限制") from exc
        except APIConnectionError as exc:
            raise LLMConnectionError("无法连接模型API，请检查网络和Base URL") from exc
        except APIStatusError as exc:
            raise LLMResponseError(f"模型API返回错误状态码: {exc.status_code}") from exc

        content = completion.choices[0].message.content

        if content is None or not content.strip():
            raise LLMResponseError("模型没有返回有效文本")

        return content
