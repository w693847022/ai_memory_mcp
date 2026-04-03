#!/usr/bin/env python3
"""API层版本控制集成测试."""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService
from business.tag_service import TagService
from business.api.projects import init_services, router
from fastapi.testclient import TestClient
from fastapi import FastAPI


def test_api_version_control():
    """测试API层版本控制功能."""
    print("测试: API层版本控制...")

    temp_dir = tempfile.mkdtemp()
    try:
        # 初始化存储和服务
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        # 初始化API服务
        init_services(storage, project_service, tag_service)

        # 创建测试应用
        app = FastAPI()
        app.include_router(router)

        # 创建测试客户端
        client = TestClient(app)

        # 注册测试项目
        register_response = client.post("/api/projects", params={
            "name": "版本控制测试项目",
            "summary": "用于测试版本控制功能的项目",
            "tags": "test,version"
        })
        print(f"注册响应状态码: {register_response.status_code}")
        if register_response.status_code != 200:
            print(f"注册响应内容: {register_response.text}")
        assert register_response.status_code == 200
        project_id = register_response.json()["data"]["project_id"]

        # 添加测试条目
        add_response = client.post(
            f"/api/projects/{project_id}/items",
            params={"group": "features"},
            json={
                "summary": "测试功能",
                "content": "这是一个测试功能",
                "status": "pending",  # features组需要status参数
                "tags": "test"
            }
        )
        print(f"添加条目响应状态码: {add_response.status_code}")
        if add_response.status_code != 200:
            print(f"添加条目响应内容: {add_response.text}")
        assert add_response.status_code == 200
        item_id = add_response.json()["data"]["item_id"]
        initial_version = add_response.json()["data"]["item"].get("version", 1)

        print(f"✓ 创建条目成功，初始版本: {initial_version}")

        # 测试1: 不带版本号的更新（应该成功）
        update_response = client.put(
            f"/api/projects/{project_id}/items/{item_id}",
            params={"group": "features"},
            json={"summary": "更新后的功能"}
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()["data"]
        new_version = updated_data["version"]
        assert new_version == initial_version + 1
        print(f"✓ 无版本检查更新成功，版本递增至: {new_version}")

        # 测试2: 带正确版本号的更新（应该成功）
        update_response = client.put(
            f"/api/projects/{project_id}/items/{item_id}",
            params={"group": "features"},
            json={
                "summary": "再次更新的功能",
                "version": new_version
            }
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()["data"]
        newer_version = updated_data["version"]
        assert newer_version == new_version + 1
        print(f"✓ 正确版本号更新成功，版本递增至: {newer_version}")

        # 测试3: 带错误版本号的更新（应该失败，返回409冲突）
        update_response = client.put(
            f"/api/projects/{project_id}/items/{item_id}",
            params={"group": "features"},
            json={
                "summary": "冲突的更新",
                "version": 999  # 错误的版本号
            }
        )
        assert update_response.status_code == 409
        conflict_data = update_response.json()["detail"]
        assert conflict_data["error"] == "version_conflict"
        assert conflict_data["current_version"] == newer_version
        assert conflict_data["expected_version"] == 999
        print(f"✓ 版本冲突检测成功，当前版本: {conflict_data['current_version']}")

        # 验证数据没有被修改
        get_response = client.get(f"/api/projects/{project_id}/items", params={
            "group_name": "features",
            "item_id": item_id
        })
        assert get_response.status_code == 200
        item_data = get_response.json()["data"]["item"]
        assert item_data["summary"] == "再次更新的功能"
        assert item_data["version"] == newer_version
        print(f"✓ 冲突后数据未被修改，版本保持: {newer_version}")

        print("✅ 所有API版本控制测试通过!")

    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_api_version_control()