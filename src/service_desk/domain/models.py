from dataclasses import dataclass

from service_desk.domain.enums import (
    CustomerPlan,
    CustomerStatus,
    TicketPriority,
    TicketSource,
    TicketStatus,
)


@dataclass
class Customer:
    id: str
    name: str
    plan: CustomerPlan
    products: list[str]
    status: CustomerStatus


@dataclass
class Ticket:
    id: str
    customer_id: str
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    assignee: str | None
    source: TicketSource
