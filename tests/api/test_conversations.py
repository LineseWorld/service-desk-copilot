from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient


def assert_utc_datetime(value: str) -> None:
    parsed_value = datetime.fromisoformat(value)

    assert parsed_value.tzinfo is not None
    assert parsed_value.utcoffset() is not None
    assert parsed_value.utcoffset().total_seconds() == 0


def test_conversation_full_scenario(client: TestClient) -> None:
    # 不存在的客户不能创建会话。
    response = client.post(
        "/api/v1/conversations",
        json={
            "id": "conversation-missing-customer",
            "customer_id": "not-exist",
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["code"] == "customer_not_found"

    # 创建本场景使用的客户。
    response = client.post(
        "/api/v1/customers",
        json={
            "id": "customer-001",
            "name": "测试企业",
            "plan": "ENTERPRISE",
            "products": ["IM", "MEETING"],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text

    # 创建会话, 默认状态为 OPEN, 创建时间由服务端生成并使用 UTC。
    conversation_payload = {
        "id": "conversation-001",
        "customer_id": "customer-001",
    }
    response = client.post(
        "/api/v1/conversations",
        json=conversation_payload,
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    conversation = response.json()
    assert conversation["id"] == "conversation-001"
    assert conversation["customer_id"] == "customer-001"
    assert conversation["status"] == "OPEN"
    assert_utc_datetime(conversation["created_at"])

    # 查询刚创建的会话。
    response = client.get("/api/v1/conversations/conversation-001")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == conversation

    # 重复创建会话返回稳定的 409 业务错误。
    response = client.post(
        "/api/v1/conversations",
        json=conversation_payload,
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    assert response.json()["code"] == "conversation_already_exists"

    # 查询不存在的会话。
    response = client.get("/api/v1/conversations/not-exist")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["code"] == "conversation_not_found"

    # 添加三条客户消息。即使请求包含 role, 也不能伪造 SYSTEM 角色。
    message_payloads = [
        {
            "id": "message-001",
            "content": "  会议客户端无法加入会议  ",
            "role": "SYSTEM",
        },
        {
            "id": "message-002",
            "content": "客户端提示错误码 M-102",
        },
        {
            "id": "message-003",
            "content": "今天上午开始出现问题",
        },
    ]

    created_messages: list[dict[str, object]] = []
    for payload in message_payloads:
        response = client.post(
            "/api/v1/conversations/conversation-001/messages",
            json=payload,
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        message = response.json()
        assert message["conversation_id"] == "conversation-001"
        assert message["role"] == "USER"
        assert_utc_datetime(str(message["created_at"]))
        created_messages.append(message)

    # StringConstraints 会清除消息首尾空白。
    assert created_messages[0]["content"] == "会议客户端无法加入会议"

    # 查询消息历史, 顺序应稳定。
    response = client.get("/api/v1/conversations/conversation-001/messages")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert [message["id"] for message in response.json()] == [
        "message-001",
        "message-002",
        "message-003",
    ]

    # 验证 offset/limit 分页。
    response = client.get(
        "/api/v1/conversations/conversation-001/messages",
        params={"limit": 2, "offset": 1},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert [message["id"] for message in response.json()] == [
        "message-002",
        "message-003",
    ]

    # 重复消息 ID 返回 409。
    response = client.post(
        "/api/v1/conversations/conversation-001/messages",
        json={
            "id": "message-001",
            "content": "重复消息",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    assert response.json()["code"] == "message_already_exists"

    # 空消息和纯空白消息均被 Schema 拒绝。
    for content in ["", "   "]:
        response = client.post(
            "/api/v1/conversations/conversation-001/messages",
            json={
                "id": f"invalid-message-{len(content)}",
                "content": content,
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 不存在的会话不能添加或查询消息。
    response = client.post(
        "/api/v1/conversations/not-exist/messages",
        json={
            "id": "message-not-exist",
            "content": "测试消息",
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["code"] == "conversation_not_found"

    response = client.get("/api/v1/conversations/not-exist/messages")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["code"] == "conversation_not_found"

    # 分页参数由 FastAPI 进行边界校验。
    for params in [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ]:
        response = client.get(
            "/api/v1/conversations/conversation-001/messages",
            params=params,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 关闭会话。
    response = client.patch("/api/v1/conversations/conversation-001/close")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["status"] == "CLOSED"

    # 已关闭会话不能重复关闭。
    response = client.patch("/api/v1/conversations/conversation-001/close")
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    assert response.json()["code"] == "conversation_already_closed"

    # 已关闭会话不能继续接收消息。
    response = client.post(
        "/api/v1/conversations/conversation-001/messages",
        json={
            "id": "message-after-close",
            "content": "关闭后发送的消息",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    assert response.json()["code"] == "conversation_already_closed"
