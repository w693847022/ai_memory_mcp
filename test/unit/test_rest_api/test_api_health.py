"""健康检查和根路径 API 单元测试."""

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# 添加 src 目录到路径
src_dir = Path(__file__).parent.parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from rest_api.main import app


@pytest.fixture
def client():
    """创建测试客户端."""
    return TestClient(app)


class TestHealthCheck:
    """测试健康检查 API."""

    def test_health_check_success(self, client):
        """测试健康检查返回 healthy 状态."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert data["message"] == "Success"

    def test_health_check_response_format(self, client):
        """测试健康检查响应格式."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        # 验证响应包含必要字段
        assert "success" in data
        assert "data" in data
        assert "message" in data


class TestRoot:
    """测试根路径 API."""

    def test_root_success(self, client):
        """测试根路径返回正确信息."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Project Memory REST API"
        assert data["data"]["version"] == "1.0.0"
        assert data["data"]["docs"] == "/docs"
        assert data["data"]["health"] == "/health"
        assert data["message"] == "Success"

    def test_root_response_format(self, client):
        """测试根路径响应格式."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        # 验证响应包含必要字段
        assert "success" in data
        assert "data" in data
        assert "message" in data
        # 验证 data 中的字段
        assert "name" in data["data"]
        assert "version" in data["data"]
        assert "docs" in data["data"]
        assert "health" in data["data"]
