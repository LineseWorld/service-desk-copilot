from dataclasses import dataclass

from service_desk.domain.enums import (
    CustomerPlan,
    CustomerStatus,
    TicketPriority,
    TicketSource,
    TicketStatus,
)
from service_desk.domain.exceptions import InvalidTicketTransition


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

    def transition_to(self, target_status: TicketStatus) -> None:
        allowed_statuses = ALLOWED_TICKET_TRANSITIONS[self.status]

        if target_status not in allowed_statuses:
            raise InvalidTicketTransition(
                ticket_id=self.id,
                current_status=self.status,
                target_status=target_status,
            )

        self.status = target_status


ALLOWED_TICKET_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.OPEN: {TicketStatus.IN_PROGRESS},
    TicketStatus.IN_PROGRESS: {
        TicketStatus.WAITING,
        TicketStatus.RESOLVED,
    },
    TicketStatus.WAITING: {
        TicketStatus.IN_PROGRESS,
    },
    TicketStatus.RESOLVED: {
        TicketStatus.CLOSED,
        TicketStatus.IN_PROGRESS,
    },
    TicketStatus.CLOSED: set(),
}
