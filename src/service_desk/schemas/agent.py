from pydantic import BaseModel, Field


class AgentTaskCreate(BaseModel):
    conversation_id: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=4000)


class ToolExecutionResponse(BaseModel):
    step: int
    tool_name: str
    success: bool
    error_code: str | None


class AgentTaskResponse(BaseModel):
    answer: str
    steps: int
    tool_executions: list[ToolExecutionResponse]
