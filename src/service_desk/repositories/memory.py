from service_desk.domain.enums import TicketPriority, TicketStatus
from service_desk.domain.models import Customer, Ticket
from service_desk.repositories.interfaces import CustomerRepository, TicketRepository


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self) -> None:
        self._customers: dict[str, Customer] = {}

    def get_by_id(self, customer_id: str) -> Customer | None:
        customer = self._customers.get(customer_id)
        if not customer:
            return None
        return customer

    def add(self, customer: Customer) -> None:
        self._customers[customer.id] = customer


class InMemoryTicketRepository(TicketRepository):
    def __init__(self):
        self._tickets: dict[str, Ticket] = {}

    def get_by_id(self, ticket_id: str) -> Ticket | None:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return None
        return ticket

    def add(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    def list(
        self,
        customer_id: str | None,
        status: TicketStatus | None,
        priority: TicketPriority | None,
    ) -> list[Ticket]:
        result: list[Ticket] = []
        for ticket in self._tickets.values():
            is_add = True
            if customer_id is not None:
                is_add = is_add and ticket.customer_id == customer_id
            if status is not None:
                is_add = is_add and ticket.status == status
            if priority is not None:
                is_add = is_add and ticket.priority == priority

            if is_add:
                result.append(ticket)
        return result
