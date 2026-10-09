from service_desk.domain.enums import CustomerStatus, TicketPriority, TicketSource, TicketStatus
from service_desk.domain.exceptions import (
    CustomerInactive,
    CustomerNotFound,
    TicketAlreadyExists,
    TicketNotFound,
)
from service_desk.domain.models import Ticket
from service_desk.repositories.interfaces import CustomerRepository, TicketRepository


class TicketService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        ticket_repository: TicketRepository,
    ) -> None:
        self._customer_repository = customer_repository
        self._ticket_repository = ticket_repository

    def create_ticket(
        self,
        *,
        ticket_id: str,
        customer_id: str,
        title: str,
        description: str,
        priority: TicketPriority,
        assignee: str | None,
        source: TicketSource,
    ) -> Ticket:
        ticket = self._ticket_repository.get_by_id(ticket_id)
        if ticket:
            raise TicketAlreadyExists(ticket_id)

        customer = self._customer_repository.get_by_id(customer_id)

        if customer is None:
            raise CustomerNotFound(customer_id)

        if customer.status != CustomerStatus.ACTIVE:
            raise CustomerInactive(customer_id)

        ticket = Ticket(
            id=ticket_id,
            customer_id=customer_id,
            title=title,
            description=description,
            priority=priority,
            status=TicketStatus.OPEN,
            assignee=assignee,
            source=source,
        )

        self._ticket_repository.add(ticket)

        return ticket

    def get_ticket(self, ticket_id: str) -> Ticket:
        ticket = self._ticket_repository.get_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFound(ticket_id)

        return ticket

    def list_tickets(
        self,
        customer_id: str | None,
        status: TicketStatus | None,
        priority: TicketPriority | None,
    ) -> list[Ticket]:
        return self._ticket_repository.list(customer_id, status, priority)

    def change_ticket_status(
        self,
        *,
        ticket_id: str,
        target_status: TicketStatus,
    ) -> Ticket:
        ticket = self._ticket_repository.get_by_id(ticket_id=ticket_id)

        if ticket is None:
            raise TicketNotFound(ticket_id)

        ticket.transition_to(target_status)

        self._ticket_repository.update(ticket)

        return ticket
