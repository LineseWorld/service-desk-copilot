from service_desk.config import get_settings
from service_desk.llm.client import OpenAICompatibleLLMClient
from service_desk.llm.exceptions import LLMConfigurationError, LLMError


def main() -> None:
    settings = get_settings()
    if settings.llm_api_key is None:
        raise LLMConfigurationError("没有配置LLM_API_KEY，请检查项目根目录下的.env文件")

    client = OpenAICompatibleLLMClient(
        api_key=settings.llm_api_key.get_secret_value(),
        base_url=settings.llm_base_url,
        model=settings.llm_model,
    )

    try:
        answer = client.complete(
            system_prompt=(
                "你是Service Desk Copilot，"
                "负责协助企业客户查询客户资料和处理工单。"
                "请使用简洁、专业的中文回答。"
            ),
            user_message="请用两句话介绍你的职责。",
        )
    except LLMError as exc:
        print(f"调用失败: {exc}")
        raise SystemExit(1) from exc

    print(f"模型: {client.model}")
    print(f"回答: {answer}")


if __name__ == "__main__":
    main()
