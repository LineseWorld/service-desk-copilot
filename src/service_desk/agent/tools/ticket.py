from dataclasses import asdict
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from service_desk.agent.tools.base import ToolResult
from service_desk.domain.enums import TicketPriority, TicketSource
from service_desk.llm.models import ToolDefinition
from service_desk.services.ticket_service import TicketService


class ListCustomerTicketsArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1, max_length=50)


class CreateTicketArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)
    priority: TicketPriority


class ListCustomerTicketsTool:
    def __init__(self, ticket_service: TicketService) -> None:
        self._ticket_service = ticket_service

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="list_customer_tickets",
            description="查询指定客户的全部工单，用于避免重复创建工单。",
            parameters=ListCustomerTicketsArguments.model_json_schema(),
        )

    def execute(self, arguments_json: str) -> ToolResult:
        arguments = ListCustomerTicketsArguments.model_validate_json(arguments_json)

        tickets = self._ticket_service.list_tickets(
            customer_id=arguments.customer_id,
            status=None,
            priority=None,
        )

        return ToolResult(
            success=True,
            data=[asdict(ticket) for ticket in tickets],
        )


class CreateTicketTool:
    def __init__(self, ticket_service: TicketService) -> None:
        self._ticket_service = ticket_service

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="create_ticket",
            description=("为客户创建新工单。调用前必须确认客户存在并查询现有工单，避免重复创建。"),
            parameters=CreateTicketArguments.model_json_schema(),
        )

    def execute(self, arguments_json: str) -> ToolResult:
        arguments = CreateTicketArguments.model_validate_json(arguments_json)

        if arguments.priority == TicketPriority.URGENT:
            return ToolResult(
                success=False,
                error_code="APPROVAL_REQUIRED",
                message="创建URGENT工单需要人工确认",
            )

        ticket = self._ticket_service.create_ticket(
            ticket_id=str(uuid4()),
            customer_id=arguments.customer_id,
            title=arguments.title,
            description=arguments.description,
            priority=arguments.priority,
            assignee=None,
            source=TicketSource.AGENT,
        )

        return ToolResult(
            success=True,
            data=asdict(ticket),
        )
