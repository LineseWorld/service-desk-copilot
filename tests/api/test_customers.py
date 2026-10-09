from fastapi.testclient import TestClient


def test_customer(client: TestClient) -> None:
    # 正常创建
    payload = {
        "id": "customer-001",
        "name": "测试企业",
        "plan": "ENTERPRISE",
        "products": ["IM", "MEETING"],
    }

    response = client.post("/api/v1/customers", json=payload)

    assert response.status_code == 201

    # 正常获取
    response = client.get("/api/v1/customers/customer-001")

    assert response.status_code == 200

    # 重复创建
    payload = {
        "id": "customer-001",
        "name": "测试企业",
        "plan": "ENTERPRISE",
        "products": ["IM", "MEETING"],
    }

    response = client.post("/api/v1/customers", json=payload)
    print(response.json())
    assert response.status_code == 409
    # 找不到
    response = client.get("/api/v1/customers/123")

    assert response.status_code == 404
