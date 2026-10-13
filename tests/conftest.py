import pytest
from fastapi.testclient import TestClient

from service_desk.api.dependencies import (
    get_conversation_repository,
    get_customer_repository,
    get_message_repository,
    get_ticket_repository,
)
from service_desk.main import create_app
from service_desk.repositories.memory import (
    InMemoryConversationRepository,
    InMemoryCustomerRepository,
    InMemoryMessageRepository,
    InMemoryTicketRepository,
)


@pytest.fixture
def client():
    app = create_app()
    customer_repository = InMemoryCustomerRepository()
    ticket_repository = InMemoryTicketRepository()
    conversation_repository = InMemoryConversationRepository()
    message_repository = InMemoryMessageRepository()

    app.dependency_overrides[get_customer_repository] = lambda: customer_repository

    app.dependency_overrides[get_ticket_repository] = lambda: ticket_repository

    app.dependency_overrides[get_conversation_repository] = lambda: conversation_repository

    app.dependency_overrides[get_message_repository] = lambda: message_repository
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
