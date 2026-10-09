from pydantic import BaseModel, Field

from service_desk.domain.enums import TicketPriority, TicketSource, TicketStatus


class TicketCreate(BaseModel):
    id: str = Field(min_length=1, max_length=50)
    customer_id: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=1)
    priority: TicketPriority
    assignee: str | None = Field(default=None)
    source: TicketSource = Field(default=TicketSource.MANUAL)


class TicketResponse(BaseModel):
    id: str
    customer_id: str
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    assignee: str | None
    source: TicketSource
