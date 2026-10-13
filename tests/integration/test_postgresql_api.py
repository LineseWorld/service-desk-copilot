import os
from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from service_desk.database.session import engine, get_db_session
from service_desk.main import create_app

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_POSTGRES_TESTS") != "1",
        reason="set RUN_POSTGRES_TESTS=1 to run PostgreSQL integration tests",
    ),
]


@pytest.fixture
def postgres_client() -> Iterator[tuple[TestClient, Connection]]:
    connection = engine.connect()
    outer_transaction = connection.begin()
    app = create_app()

    def override_db_session() -> Iterator[Session]:
        with Session(
            bind=connection,
            autoflush=False,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        ) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_db_session

    try:
        with TestClient(app) as client:
            yield client, connection
    finally:
        app.dependency_overrides.clear()
        if outer_transaction.is_active:
            outer_transaction.rollback()
        connection.close()


def test_postgresql_full_persistence_scenario(
    postgres_client: tuple[TestClient, Connection],
) -> None:
    client, connection = postgres_client
    suffix = uuid4().hex
    customer_id = f"it-customer-{suffix}"
    ticket_id = f"it-ticket-{suffix}"
    conversation_id = f"it-conversation-{suffix}"
    first_message_id = f"it-message-a-{suffix}"
    second_message_id = f"it-message-b-{suffix}"

    response = client.post(
        "/api/v1/customers",
        json={
            "id": customer_id,
            "name": "PostgreSQL集成测试客户",
            "plan": "ENTERPRISE",
            "products": ["IM", "MEETING"],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text

    response = client.post(
        "/api/v1/tickets",
        json={
            "id": ticket_id,
            "customer_id": customer_id,
            "title": "PostgreSQL持久化测试工单",
            "description": "验证请求级Session、Repository和事务提交",
            "priority": "HIGH",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text

    response = client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "IN_PROGRESS"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["status"] == "IN_PROGRESS"

    response = client.post(
        "/api/v1/conversations",
        json={
            "id": conversation_id,
            "customer_id": customer_id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text

    for message_id, content in [
        (first_message_id, "第一条PostgreSQL测试消息"),
        (second_message_id, "第二条PostgreSQL测试消息"),
    ]:
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"id": message_id, "content": content},
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text

    response = client.get(
        f"/api/v1/conversations/{conversation_id}/messages",
        params={"limit": 1, "offset": 1},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert [message["id"] for message in response.json()] == [second_message_id]

    response = client.patch(f"/api/v1/conversations/{conversation_id}/close")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["status"] == "CLOSED"

    persisted = connection.execute(
        text(
            """
            SELECT
                (SELECT status::text FROM tickets WHERE id = :ticket_id),
                (SELECT status::text FROM conversations WHERE id = :conversation_id),
                (SELECT COUNT(*) FROM messages WHERE conversation_id = :conversation_id)
            """
        ),
        {
            "ticket_id": ticket_id,
            "conversation_id": conversation_id,
        },
    ).one()

    assert persisted == ("IN_PROGRESS", "CLOSED", 2)
