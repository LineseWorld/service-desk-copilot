from abc import ABC, abstractmethod

from service_desk.domain.enums import TicketPriority, TicketStatus
from service_desk.domain.models import Customer, Ticket


class CustomerRepository(ABC):
    @abstractmethod
    def get_by_id(self, customer_id: str) -> Customer | None: ...

    @abstractmethod
    def add(self, customer: Customer) -> None: ...


class TicketRepository(ABC):
    @abstractmethod
    def get_by_id(self, ticket_id: str) -> Ticket | None: ...

    @abstractmethod
    def add(self, ticket: Ticket) -> None: ...

    @abstractmethod
    def list(
        self,
        customer_id: str | None,
        status: TicketStatus | None,
        priority: TicketPriority | None,
    ) -> list[Ticket]: ...
