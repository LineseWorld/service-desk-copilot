from sqlalchemy import select
from sqlalchemy.orm import Session

from service_desk.database.models import (
    ConversationRecord,
    CustomerRecord,
    MessageRecord,
    TicketRecord,
)
from service_desk.domain.enums import TicketPriority, TicketStatus
from service_desk.domain.models import Conversation, Customer, Message, Ticket
from service_desk.repositories.interfaces import (
    ConversationRepository,
    CustomerRepository,
    MessageRepository,
    TicketRepository,
)


def customer_to_domain(record: CustomerRecord) -> Customer:
    return Customer(
        id=record.id,
        name=record.name,
        plan=record.plan,
        products=list(record.products),
        status=record.status,
    )


def customer_to_record(customer: Customer) -> CustomerRecord:
    return CustomerRecord(
        id=customer.id,
        name=customer.name,
        plan=customer.plan,
        products=list(customer.products),
        status=customer.status,
    )


def ticket_to_domain(record: TicketRecord) -> Ticket:
    return Ticket(
        id=record.id,
        customer_id=record.customer_id,
        title=record.title,
        description=record.description,
        priority=record.priority,
        status=record.status,
        assignee=record.assignee,
        source=record.source,
    )


def ticket_to_record(ticket: Ticket) -> TicketRecord:
    return TicketRecord(
        id=ticket.id,
        customer_id=ticket.customer_id,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        assignee=ticket.assignee,
        source=ticket.source,
    )


def conversation_to_domain(record: ConversationRecord) -> Conversation:
    return Conversation(
        id=record.id,
        customer_id=record.customer_id,
        status=record.status,
        created_at=record.created_at,
    )


def conversation_to_record(conversation: Conversation) -> ConversationRecord:
    return ConversationRecord(
        id=conversation.id,
        customer_id=conversation.customer_id,
        status=conversation.status,
        created_at=conversation.created_at,
    )


def message_to_domain(record: MessageRecord) -> Message:
    return Message(
        id=record.id,
        conversation_id=record.conversation_id,
        role=record.role,
        content=record.content,
        created_at=record.created_at,
    )


def message_to_record(message: Message) -> MessageRecord:
    return MessageRecord(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )


class SqlAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, customer_id: str) -> Customer | None:
        record = self._session.get(
            CustomerRecord,
            customer_id,
        )

        if record is None:
            return None

        return customer_to_domain(record)

    def add(self, customer: Customer) -> None:
        self._session.add(customer_to_record(customer))


class SqlAlchemyTicketRepository(TicketRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, ticket_id: str) -> Ticket | None:
        record = self._session.get(
            TicketRecord,
            ticket_id,
        )

        if record is None:
            return None

        return ticket_to_domain(record)

    def add(self, ticket: Ticket) -> None:
        self._session.add(ticket_to_record(ticket))

    def update(self, ticket: Ticket) -> None:
        record = self._session.get(
            TicketRecord,
            ticket.id,
        )

        if record is None:
            return

        record.title = ticket.title
        record.description = ticket.description
        record.priority = ticket.priority
        record.status = ticket.status
        record.assignee = ticket.assignee
        record.source = ticket.source

    def list(
        self,
        customer_id: str | None,
        status: TicketStatus | None,
        priority: TicketPriority | None,
    ) -> list[Ticket]:
        statement = select(TicketRecord)

        if customer_id is not None:
            statement = statement.where(TicketRecord.customer_id == customer_id)

        if status is not None:
            statement = statement.where(TicketRecord.status == status)

        if priority is not None:
            statement = statement.where(TicketRecord.priority == priority)

        statement = statement.order_by(TicketRecord.id)

        records = self._session.scalars(statement).all()

        return [ticket_to_domain(record) for record in records]


class SqlAlchemyConversationRepository(ConversationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, conversation_id: str) -> Conversation | None:
        record = self._session.get(
            ConversationRecord,
            conversation_id,
        )

        if record is None:
            return None

        return conversation_to_domain(record)

    def add(self, conversation: Conversation) -> None:
        self._session.add(conversation_to_record(conversation))

    def update(self, conversation: Conversation) -> None:
        record = self._session.get(
            ConversationRecord,
            conversation.id,
        )

        if record is None:
            return

        record.status = conversation.status


class SqlAlchemyMessageRepository(MessageRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, message_id: str) -> Message | None:
        record = self._session.get(
            MessageRecord,
            message_id,
        )
        if record is None:
            return None

        return message_to_domain(record)

    def add(self, message: Message) -> None:
        self._session.add(message_to_record(message))

    def list_by_conversation(
        self,
        conversation_id: str,
        *,
        limit: int,
        offset: int,
    ) -> list[Message]:
        statement = (
            select(MessageRecord)
            .where(MessageRecord.conversation_id == conversation_id)
            .order_by(MessageRecord.created_at, MessageRecord.id)
            .offset(offset)
            .limit(limit)
        )

        records = self._session.scalars(statement).all()

        return [message_to_domain(record) for record in records]
