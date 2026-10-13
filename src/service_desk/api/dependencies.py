from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from service_desk.database.session import get_db_session
from service_desk.repositories.interfaces import (
    ConversationRepository,
    CustomerRepository,
    MessageRepository,
    TicketRepository,
)
from service_desk.repositories.sqlalchemy import (
    SqlAlchemyConversationRepository,
    SqlAlchemyCustomerRepository,
    SqlAlchemyMessageRepository,
    SqlAlchemyTicketRepository,
)
from service_desk.services.conversation_service import ConversationService
from service_desk.services.customer_service import CustomerService
from service_desk.services.ticket_service import TicketService

DbSessionDep = Annotated[
    Session,
    Depends(
        get_db_session,
        scope="function",
    ),
]


def get_customer_repository(session: DbSessionDep) -> CustomerRepository:
    return SqlAlchemyCustomerRepository(session)


CustomerRepositoryDep = Annotated[
    CustomerRepository,
    Depends(get_customer_repository),
]


def get_customer_service(repository: CustomerRepositoryDep) -> CustomerService:
    return CustomerService(repository=repository)


CustomerServiceDep = Annotated[
    CustomerService,
    Depends(get_customer_service),
]


def get_ticket_repository(session: DbSessionDep) -> TicketRepository:
    return SqlAlchemyTicketRepository(session)


TicketRepositoryDep = Annotated[
    TicketRepository,
    Depends(get_ticket_repository),
]


def get_ticket_service(
    customer_repository: CustomerRepositoryDep, ticket_repository: TicketRepositoryDep
) -> TicketService:
    return TicketService(customer_repository, ticket_repository)


TicketServiceDep = Annotated[
    TicketService,
    Depends(get_ticket_service),
]


def get_conversation_repository(session: DbSessionDep) -> ConversationRepository:
    return SqlAlchemyConversationRepository(session)


ConversationRepositoryDep = Annotated[
    ConversationRepository,
    Depends(get_conversation_repository),
]


def get_message_repository(session: DbSessionDep) -> MessageRepository:
    return SqlAlchemyMessageRepository(session)


MessageRepositoryDep = Annotated[
    MessageRepository,
    Depends(get_message_repository),
]


def get_conversation_service(
    customer_repository: CustomerRepositoryDep,
    conversation_repository: ConversationRepositoryDep,
    message_repository: MessageRepositoryDep,
) -> ConversationService:
    return ConversationService(
        customer_repository=customer_repository,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
    )


ConversationServiceDep = Annotated[
    ConversationService,
    Depends(get_conversation_service),
]
