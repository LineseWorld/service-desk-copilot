class AgentError(Exception):
    pass


class AgentEmptyResponse(AgentError):
    pass


class AgentMaxStepsExceeded(AgentError):
    pass
