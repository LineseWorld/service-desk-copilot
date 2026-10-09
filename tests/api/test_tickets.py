from fastapi import status
from fastapi.testclient import TestClient


def test_ticket_full_scenario(client: TestClient) -> None:
    # Arrange 阶段创建两个客户并为工单场景准备数据。
    customer_001 = {
        "id": "customer-001",
        "name": "测试企业一",
        "plan": "ENTERPRISE",
        "products": ["IM", "MEETING"],
    }
    customer_002 = {
        "id": "customer-002",
        "name": "测试企业二",
        "plan": "STANDARD",
        "products": ["IM"],
    }

    response = client.post("/api/v1/customers", json=customer_001)
    assert response.status_code == status.HTTP_201_CREATED, response.text

    response = client.post("/api/v1/customers", json=customer_002)
    assert response.status_code == status.HTTP_201_CREATED, response.text

    # 创建第一张工单。assignee 和 source 使用接口默认值。
    ticket_001 = {
        "id": "ticket-001",
        "customer_id": "customer-001",
        "title": "会议无法正常加入",
        "description": "用户加入会议时提示错误码 M-102",
        "priority": "HIGH",
    }

    response = client.post("/api/v1/tickets", json=ticket_001)

    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json() == {
        "id": "ticket-001",
        "customer_id": "customer-001",
        "title": "会议无法正常加入",
        "description": "用户加入会议时提示错误码 M-102",
        "priority": "HIGH",
        "status": "OPEN",
        "assignee": None,
        "source": "MANUAL",
    }

    # 查询刚创建的工单。
    response = client.get("/api/v1/tickets/ticket-001")

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "id": "ticket-001",
        "customer_id": "customer-001",
        "title": "会议无法正常加入",
        "description": "用户加入会议时提示错误码 M-102",
        "priority": "HIGH",
        "status": "OPEN",
        "assignee": None,
        "source": "MANUAL",
    }

    # 再创建两张工单用于列表过滤。
    ticket_002 = {
        "id": "ticket-002",
        "customer_id": "customer-001",
        "title": "消息发送接口失败",
        "description": "发送消息时接口返回超时",
        "priority": "LOW",
        "assignee": "im-team",
        "source": "MANUAL",
    }
    ticket_003 = {
        "id": "ticket-003",
        "customer_id": "customer-002",
        "title": "用户登录接口异常",
        "description": "用户登录时服务返回错误",
        "priority": "HIGH",
        "assignee": "account-team",
        "source": "MANUAL",
    }

    response = client.post("/api/v1/tickets", json=ticket_002)
    assert response.status_code == status.HTTP_201_CREATED, response.text

    response = client.post("/api/v1/tickets", json=ticket_003)
    assert response.status_code == status.HTTP_201_CREATED, response.text

    # 查询全部工单且不依赖返回顺序。
    response = client.get("/api/v1/tickets")

    assert response.status_code == status.HTTP_200_OK, response.text
    tickets = response.json()
    assert len(tickets) == 3
    assert {ticket["id"] for ticket in tickets} == {
        "ticket-001",
        "ticket-002",
        "ticket-003",
    }

    # 按客户过滤。
    response = client.get(
        "/api/v1/tickets",
        params={"customer_id": "customer-001"},
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    tickets = response.json()
    assert len(tickets) == 2
    assert {ticket["id"] for ticket in tickets} == {
        "ticket-001",
        "ticket-002",
    }
    assert all(ticket["customer_id"] == "customer-001" for ticket in tickets)

    # 按优先级过滤。
    response = client.get(
        "/api/v1/tickets",
        params={"priority": "HIGH"},
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    tickets = response.json()
    assert len(tickets) == 2
    assert {ticket["id"] for ticket in tickets} == {
        "ticket-001",
        "ticket-003",
    }
    assert all(ticket["priority"] == "HIGH" for ticket in tickets)

    # 组合过滤。
    response = client.get(
        "/api/v1/tickets",
        params={
            "customer_id": "customer-001",
            "status": "OPEN",
            "priority": "LOW",
        },
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    assert [ticket["id"] for ticket in response.json()] == ["ticket-002"]

    # 没有匹配结果时返回空列表。
    response = client.get(
        "/api/v1/tickets",
        params={"priority": "URGENT"},
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == []

    # 重复创建工单。
    response = client.post("/api/v1/tickets", json=ticket_001)

    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    assert response.json()["code"] == "ticket_already_exists"

    # 查询不存在的工单。
    response = client.get("/api/v1/tickets/not-exist")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["code"] == "ticket_not_found"

    # 使用不存在的客户创建工单。
    missing_customer_ticket = {
        "id": "ticket-004",
        "customer_id": "not-exist",
        "title": "不存在客户的测试工单",
        "description": "这个工单不能创建成功",
        "priority": "MEDIUM",
    }

    response = client.post("/api/v1/tickets", json=missing_customer_ticket)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["code"] == "customer_not_found"

    # 标题长度不足。
    invalid_title_ticket = {
        "id": "ticket-005",
        "customer_id": "customer-001",
        "title": "错误",
        "description": "标题长度不足五个字符",
        "priority": "LOW",
    }

    response = client.post("/api/v1/tickets", json=invalid_title_ticket)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text

    # description 为空。
    empty_description_ticket = {
        "id": "ticket-006",
        "customer_id": "customer-001",
        "title": "工单描述为空测试",
        "description": "",
        "priority": "LOW",
    }

    response = client.post("/api/v1/tickets", json=empty_description_ticket)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text

    # 非法优先级。
    invalid_priority_ticket = {
        "id": "ticket-007",
        "customer_id": "customer-001",
        "title": "非法优先级测试工单",
        "description": "优先级不在枚举范围中",
        "priority": "SUPER_HIGH",
    }

    response = client.post("/api/v1/tickets", json=invalid_priority_ticket)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text

    # 查询参数使用非法状态枚举。
    response = client.get(
        "/api/v1/tickets",
        params={"status": "UNKNOWN"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text
