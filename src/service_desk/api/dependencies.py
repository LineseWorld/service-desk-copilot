from typing import Annotated, cast

from fastapi import Depends, Request

from service_desk.repositories.interfaces import (
    ConversationRepository,
    CustomerRepository,
    MessageRepository,
    TicketRepository,
)
from service_desk.services.conversation_service import ConversationService
from service_desk.services.customer_service import CustomerService
from service_desk.services.ticket_service import TicketService


def get_customer_repository(request: Request) -> CustomerRepository:
    return cast(CustomerRepository, request.app.state.customer_repository)


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


def get_ticket_repository(request: Request) -> TicketRepository:
    return cast(TicketRepository, request.app.state.ticket_repository)


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


def get_conversation_service(
    request: Request,
) -> ConversationService:
    customer_repository = cast(
        CustomerRepository,
        request.app.state.customer_repository,
    )

    conversation_repository = cast(
        ConversationRepository,
        request.app.state.conversation_repository,
    )

    message_repository = cast(
        MessageRepository,
        request.app.state.message_repository,
    )

    return ConversationService(
        customer_repository=customer_repository,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
    )


ConversationServiceDep = Annotated[
    ConversationService,
    Depends(get_conversation_service),
]
