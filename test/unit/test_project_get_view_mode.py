#!/usr/bin/env python3
"""project_get view_mode 参数单元测试（简化版）."""

import sys
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from features.project import ProjectMemory

# 预先导入 api.tools 以避免模块缓存问题
import api.tools


def test_view_mode_default():
    """测试 view_mode 默认值为 summary."""
    print("测试: view_mode 默认值...")

    test_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=test_dir)
        result = memory.register_project("test_project", test_dir, "测试项目", ["test"])
        project_id = result["project_id"]

        for i in range(25):
            memory.add_item(
                project_id=project_id,
                group="features",
                summary=f"测试功能 {i+1}",
                content=f"测试功能内容 {i+1}",
                status="pending",
                tags=["test"]
            )

        # Mock api.tools 中的 memory 引用
        with patch.object(api.tools, 'memory', memory):
            result = api.tools.project_get(project_id=project_id, group_name="features")
            data = json.loads(result)

            assert data["success"], f"请求失败: {data.get('error')}"
            assert len(data["data"]["items"]) == 20, f"默认应返回20条，实际返回 {len(data['data']['items'])} 条"
            assert data["data"]["filtered_total"] == 25, f"过滤总数应该是25，实际是 {data['data']['filtered_total']}"

            items = data["data"]["items"]
            assert len(items) > 0, "应该返回至少一条数据"
            item = items[0]
            assert "id" in item, "summary 模式应包含 id 字段"
            assert "summary" in item, "summary 模式应包含 summary 字段"
            assert "tags" in item, "summary 模式应包含 tags 字段"
            assert "status" not in item, "summary 模式不应包含 status 字段"
            assert "created_at" not in item, "summary 模式不应包含 created_at 字段"

        print("  ✓ view_mode 默认值测试通过")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_view_mode_summary():
    """测试 view_mode=summary 只返回核心字段."""
    print("测试: view_mode=summary 返回字段...")

    test_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=test_dir)
        result = memory.register_project("test_project", test_dir, "测试项目", ["test"])
        project_id = result["project_id"]

        for i in range(5):
            memory.add_item(
                project_id=project_id,
                group="features",
                summary=f"测试功能 {i+1}",
                content=f"测试功能内容 {i+1}",
                status="pending",
                tags=["test"]
            )

        with patch.object(api.tools, 'memory', memory):
            result = api.tools.project_get(project_id=project_id, group_name="features", view_mode="summary")
            data = json.loads(result)

            assert data["success"], f"请求失败: {data.get('error')}"

            items = data["data"]["items"]
            assert len(items) > 0, "应该返回至少一条数据"
            item = items[0]

            expected_keys = {"id", "summary", "tags"}
            actual_keys = set(item.keys())
            assert actual_keys == expected_keys, f"summary 模式应只返回 {expected_keys}，实际返回 {actual_keys}"

        print("  ✓ view_mode=summary 返回字段测试通过")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_view_mode_detail():
    """测试 view_mode=detail 返回完整字段."""
    print("测试: view_mode=detail 返回字段...")

    test_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=test_dir)
        result = memory.register_project("test_project", test_dir, "测试项目", ["test"])
        project_id = result["project_id"]

        memory.add_item(
            project_id=project_id,
            group="features",
            summary="测试功能",
            content="测试功能内容",
            status="pending",
            tags=["test"]
        )

        with patch.object(api.tools, 'memory', memory):
            result = api.tools.project_get(project_id=project_id, group_name="features", view_mode="detail")
            data = json.loads(result)

            assert data["success"], f"请求失败: {data.get('error')}"

            items = data["data"]["items"]
            assert len(items) > 0, "应该返回至少一条数据"
            item = items[0]

            assert "id" in item, "detail 模式应包含 id 字段"
            assert "summary" in item, "detail 模式应包含 summary 字段"
            assert "tags" in item, "detail 模式应包含 tags 字段"
            assert "status" in item, "detail 模式应包含 status 字段"
            assert "created_at" in item, "detail 模式应包含 created_at 字段"
            assert "content" not in item, "detail 模式不应包含 content 字段"

        print("  ✓ view_mode=detail 返回字段测试通过")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_view_mode_invalid():
    """测试无效的 view_mode 值."""
    print("测试: 无效的 view_mode 值...")

    test_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=test_dir)
        result = memory.register_project("test_project", test_dir, "测试项目", ["test"])
        project_id = result["project_id"]

        with patch.object(api.tools, 'memory', memory):
            result = api.tools.project_get(project_id=project_id, group_name="features", view_mode="invalid")
            data = json.loads(result)

            assert not data["success"], "无效的 view_mode 应该返回失败"
            assert "无效的 view_mode" in data.get("error", ""), f"错误信息应包含'无效的 view_mode'，实际: {data.get('error')}"

        print("  ✓ 无效的 view_mode 值测试通过")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_size_default_with_view_mode():
    """测试 size 根据 view_mode 自动设置默认值."""
    print("测试: size 根据 view_mode 自动设置...")

    test_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=test_dir)
        result = memory.register_project("test_project", test_dir, "测试项目", ["test"])
        project_id = result["project_id"]

        for i in range(25):
            memory.add_item(
                project_id=project_id,
                group="features",
                summary=f"测试功能 {i+1}",
                content=f"测试功能内容 {i+1}",
                status="pending",
                tags=["test"]
            )

        with patch.object(api.tools, 'memory', memory):
            # summary 模式默认 size=20
            result1 = api.tools.project_get(project_id=project_id, group_name="features", view_mode="summary")
            data1 = json.loads(result1)
            assert data1["success"], f"请求失败: {data1.get('error')}"
            assert len(data1["data"]["items"]) == 20, f"summary 模式默认应返回20条，实际返回 {len(data1['data']['items'])} 条"
            assert data1["data"]["filtered_total"] == 25, f"过滤总数应该是25，实际是 {data1['data']['filtered_total']}"

            # detail 模式默认 size=0（全部）
            result2 = api.tools.project_get(project_id=project_id, group_name="features", view_mode="detail")
            data2 = json.loads(result2)
            assert data2["success"], f"请求失败: {data2.get('error')}"
            assert len(data2["data"]["items"]) == 25, f"detail 模式默认应返回全部25条，实际返回 {len(data2['data']['items'])} 条"

        print("  ✓ size 根据 view_mode 自动设置测试通过")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_size_override_view_mode():
    """测试显式传入 size 覆盖 view_mode 默认值."""
    print("测试: size 覆盖 view_mode 默认值...")

    test_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=test_dir)
        result = memory.register_project("test_project", test_dir, "测试项目", ["test"])
        project_id = result["project_id"]

        for i in range(15):
            memory.add_item(
                project_id=project_id,
                group="features",
                summary=f"测试功能 {i+1}",
                content=f"测试功能内容 {i+1}",
                status="pending",
                tags=["test"]
            )

        with patch.object(api.tools, 'memory', memory):
            # summary 模式，显式指定 size=10
            result = api.tools.project_get(project_id=project_id, group_name="features", view_mode="summary", size=10)
            data = json.loads(result)
            assert data["success"], f"请求失败: {data.get('error')}"
            assert len(data["data"]["items"]) == 10, f"显式指定 size=10 应返回10条，实际返回 {len(data['data']['items'])} 条"

        print("  ✓ size 覆盖 view_mode 默认值测试通过")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_detail_mode_backward_compatible():
    """测试详情模式（有 item_id）不受 view_mode 影响."""
    print("测试: 详情模式向后兼容...")

    test_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=test_dir)
        result = memory.register_project("test_project", test_dir, "测试项目", ["test"])
        project_id = result["project_id"]

        memory.add_item(
            project_id=project_id,
            group="features",
            summary="测试功能",
            content="测试功能内容",
            status="pending",
            tags=["test"]
        )

        with patch.object(api.tools, 'memory', memory):
            # 获取一个 item_id
            list_result = api.tools.project_get(project_id=project_id, group_name="features", view_mode="summary", size=1)
            list_data = json.loads(list_result)
            item_id = list_data["data"]["items"][0]["id"]

            # 详情模式应该返回完整数据，不受 view_mode 影响
            result = api.tools.project_get(project_id=project_id, group_name="features", item_id=item_id, view_mode="summary")
            data = json.loads(result)

            assert data["success"], f"请求失败: {data.get('error')}"
            item = data["data"]["item"]
            # 详情模式应包含完整字段，包括 content
            assert "content" in item, "详情模式应包含 content 字段，不受 view_mode 影响"

        print("  ✓ 详情模式向后兼容测试通过")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)