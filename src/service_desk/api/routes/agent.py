from fastapi import APIRouter

from service_desk.api.dependencies import AgentServiceDep
from service_desk.schemas.agent import (
    AgentTaskCreate,
    AgentTaskResponse,
    ToolExecutionResponse,
)

router = APIRouter(
    prefix="/api/v1/agent",
    tags=["agent"],
)


@router.post("/tasks", response_model=AgentTaskResponse)
def run_agent_task(
    command: AgentTaskCreate,
    svc: AgentServiceDep,
) -> AgentTaskResponse:
    result = svc.run(
        conversation_id=command.conversation_id,
        user_message=command.message,
    )

    return AgentTaskResponse(
        answer=result.answer,
        steps=result.steps,
        tool_executions=[
            ToolExecutionResponse(
                step=trace.step,
                tool_name=trace.tool_name,
                success=trace.result.success,
                error_code=trace.result.error_code,
            )
            for trace in result.tool_executions
        ],
    )
