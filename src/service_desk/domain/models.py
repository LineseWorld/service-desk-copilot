from dataclasses import dataclass
from datetime import datetime

from service_desk.domain.enums import (
    ConversationStatus,
    CustomerPlan,
    CustomerStatus,
    MessageRole,
    TicketPriority,
    TicketSource,
    TicketStatus,
)
from service_desk.domain.exceptions import ConversationAlreadyClosed, InvalidTicketTransition


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


@dataclass
class Conversation:
    id: str
    customer_id: str
    status: ConversationStatus
    created_at: datetime

    def close(self) -> None:
        if self.status == ConversationStatus.CLOSED:
            raise ConversationAlreadyClosed(self.id)

        self.status = ConversationStatus.CLOSED

    def ensure_accepts_message(self) -> None:
        if self.status == ConversationStatus.CLOSED:
            raise ConversationAlreadyClosed(self.id)


@dataclass
class Message:
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    created_at: datetime
