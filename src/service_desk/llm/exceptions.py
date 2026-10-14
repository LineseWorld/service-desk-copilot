class LLMError(Exception):
    """模型调用基础异常。"""


class LLMConfigurationError(LLMError):
    """模型配置不完整。"""


class LLMAuthenticationError(LLMError):
    """模型服务认证失败。"""


class LLMRateLimitError(LLMError):
    """模型服务达到速率或额度限制。"""


class LLMConnectionError(LLMError):
    """无法连接模型服务。"""


class LLMResponseError(LLMError):
    """模型服务返回异常响应。"""
