from fastapi import status
from fastapi.testclient import TestClient


def create_customer_and_ticket(client: TestClient) -> None:
    customer_response = client.post(
        "/api/v1/customers",
        json={
            "id": "customer-001",
            "name": "测试企业",
            "plan": "ENTERPRISE",
            "products": ["IM", "MEETING"],
        },
    )
    assert customer_response.status_code == status.HTTP_201_CREATED

    ticket_response = client.post(
        "/api/v1/tickets",
        json={
            "id": "ticket-001",
            "customer_id": "customer-001",
            "title": "会议无法正常加入",
            "description": "用户加入会议时提示错误码 M-102",
            "priority": "HIGH",
        },
    )
    assert ticket_response.status_code == status.HTTP_201_CREATED


def test_ticket_status_full_scenario(client: TestClient) -> None:
    create_customer_and_ticket(client)

    for target_status in [
        "IN_PROGRESS",
        "WAITING",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED",
    ]:
        response = client.patch(
            "/api/v1/tickets/ticket-001/status",
            json={"status": target_status},
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json()["status"] == target_status

    response = client.get("/api/v1/tickets/ticket-001")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["status"] == "CLOSED"

    response = client.patch(
        "/api/v1/tickets/ticket-001/status",
        json={"status": "IN_PROGRESS"},
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    assert response.json() == {
        "code": "invalid_ticket_transition",
        "message": ("Ticket 'ticket-001' cannot transition from 'CLOSED' to 'IN_PROGRESS'"),
    }

    response = client.patch(
        "/api/v1/tickets/not-exist/status",
        json={"status": "IN_PROGRESS"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["code"] == "ticket_not_found"

    response = client.patch(
        "/api/v1/tickets/ticket-001/status",
        json={"status": "UNKNOWN"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text

    response = client.patch(
        "/api/v1/tickets/ticket-001/status",
        json={},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text
