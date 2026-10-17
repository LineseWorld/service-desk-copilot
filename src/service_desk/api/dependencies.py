from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from service_desk.agent.runner import AgentRunner
from service_desk.agent.service import AgentService
from service_desk.agent.tools.customer import GetCustomerTool
from service_desk.agent.tools.registry import ToolRegistry
from service_desk.agent.tools.ticket import (
    CreateTicketTool,
    ListCustomerTicketsTool,
)
from service_desk.config import get_settings
from service_desk.database.session import get_db_session
from service_desk.llm.client import OpenAICompatibleLLMClient
from service_desk.llm.interfaces import LLMClient
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


@lru_cache
def get_llm_client() -> LLMClient:
    settings = get_settings()

    if settings.llm_api_key is None:
        raise RuntimeError("没有配置LLM_API_KEY")

    return OpenAICompatibleLLMClient(
        api_key=settings.llm_api_key.get_secret_value(),
        base_url=settings.llm_base_url,
        model=settings.llm_model,
    )


LLMClientDep = Annotated[
    LLMClient,
    Depends(get_llm_client),
]


def get_tool_registry(
    customer_service: CustomerServiceDep,
    ticket_service: TicketServiceDep,
) -> ToolRegistry:
    return ToolRegistry(
        [
            GetCustomerTool(customer_service),
            ListCustomerTicketsTool(ticket_service),
            CreateTicketTool(ticket_service),
        ]
    )


ToolRegistryDep = Annotated[
    ToolRegistry,
    Depends(get_tool_registry),
]


def get_agent_runner(
    llm_client: LLMClientDep,
    registry: ToolRegistryDep,
) -> AgentRunner:
    return AgentRunner(
        llm_client=llm_client,
        tool_registry=registry,
        max_steps=8,
    )


AgentRunnerDep = Annotated[
    AgentRunner,
    Depends(get_agent_runner),
]


def get_agent_service(
    runner: AgentRunnerDep,
    conversation_service: ConversationServiceDep,
) -> AgentService:
    return AgentService(
        runner=runner,
        conversation_service=conversation_service,
    )


AgentServiceDep = Annotated[
    AgentService,
    Depends(get_agent_service),
]
