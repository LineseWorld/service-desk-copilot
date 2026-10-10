from abc import ABC, abstractmethod

from service_desk.domain.enums import TicketPriority, TicketStatus
from service_desk.domain.models import Conversation, Customer, Message, Ticket


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
    def update(self, ticket: Ticket) -> None: ...

    @abstractmethod
    def list(
        self,
        customer_id: str | None,
        status: TicketStatus | None,
        priority: TicketPriority | None,
    ) -> list[Ticket]: ...


class ConversationRepository(ABC):
    @abstractmethod
    def get_by_id(
        self,
        conversation_id: str,
    ) -> Conversation | None: ...

    @abstractmethod
    def add(self, conversation: Conversation) -> None: ...

    @abstractmethod
    def update(self, conversation: Conversation) -> None: ...


class MessageRepository(ABC):
    @abstractmethod
    def get_by_id(self, message_id: str) -> Message | None: ...

    @abstractmethod
    def add(self, message: Message) -> None: ...

    @abstractmethod
    def list_by_conversation(
        self,
        conversation_id: str,
        *,
        limit: int,
        offset: int,
    ) -> list[Message]: ...
