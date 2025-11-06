"""
API 测试
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_items():
    """测试获取项目列表"""
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_item():
    """测试创建项目"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    response = client.post("/api/v1/items", json=item_data)
    assert response.status_code == 201
    assert response.json()["name"] == item_data["name"]


# 更多测试用例...

