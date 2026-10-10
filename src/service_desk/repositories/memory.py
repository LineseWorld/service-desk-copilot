from copy import deepcopy

from service_desk.domain.enums import TicketPriority, TicketStatus
from service_desk.domain.models import Conversation, Customer, Message, Ticket
from service_desk.repositories.interfaces import (
    ConversationRepository,
    CustomerRepository,
    MessageRepository,
    TicketRepository,
)


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self) -> None:
        self._customers: dict[str, Customer] = {}

    def get_by_id(self, customer_id: str) -> Customer | None:
        customer = self._customers.get(customer_id)
        if customer is None:
            return None
        return deepcopy(customer)

    def add(self, customer: Customer) -> None:
        self._customers[customer.id] = deepcopy(customer)


class InMemoryTicketRepository(TicketRepository):
    def __init__(self):
        self._tickets: dict[str, Ticket] = {}

    def get_by_id(self, ticket_id: str) -> Ticket | None:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return None
        return deepcopy(ticket)

    def add(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = deepcopy(ticket)

    def update(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = deepcopy(ticket)

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
                result.append(deepcopy(ticket))
        return result


class InMemoryConversationRepository(ConversationRepository):
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}

    def get_by_id(self, conversation_id: str) -> Conversation | None:
        conversation = self._conversations.get(conversation_id)

        if conversation is None:
            return None

        return deepcopy(conversation)

    def add(self, conversation: Conversation) -> None:
        self._conversations[conversation.id] = deepcopy(conversation)

    def update(self, conversation: Conversation) -> None:
        self._conversations[conversation.id] = deepcopy(conversation)


class InMemoryMessageRepository(MessageRepository):
    def __init__(self) -> None:
        self._messages: dict[str, Message] = {}

    def get_by_id(self, message_id: str) -> Message | None:
        message = self._messages.get(message_id)
        if message is None:
            return None
        return deepcopy(message)

    def add(self, message: Message) -> None:
        self._messages[message.id] = deepcopy(message)

    def list_by_conversation(
        self,
        conversation_id: str,
        *,
        limit: int,
        offset: int,
    ) -> list[Message]:
        matched_messages = [
            deepcopy(message)
            for message in self._messages.values()
            if message.conversation_id == conversation_id
        ]

        matched_messages.sort(key=lambda message: (message.created_at, message.id))

        return matched_messages[offset : offset + limit]
