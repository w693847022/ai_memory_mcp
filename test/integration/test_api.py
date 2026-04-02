#!/usr/bin/env python3
"""MCP 工具接口集成测试."""

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


def test_project_list_integration():
    """测试项目列表接口集成."""
    print("测试: 项目列表接口集成...")

    temp_dir = tempfile.mkdtemp()
    try:
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)

        # 注册多个项目
        project_service.register_project("项目A", "/path/a", tags=["web"])
        project_service.register_project("项目B", "/path/b", tags=["api"])
        project_service.register_project("项目C", "/path/c", tags=["mobile"])

        # 获取项目列表
        result = project_service.list_projects()

        assert result["success"], f"获取项目列表失败: {result}"
        assert result["total"] == 3, f"项目数量不正确: {result['total']}"

        # 验证项目信息
        projects = result["projects"]
        names = [p["name"] for p in projects]
        assert "项目A" in names, "项目A 不在列表中"
        assert "项目B" in names, "项目B 不在列表中"
        assert "项目C" in names, "项目C 不在列表中"

        print(f"  ✓ 项目列表接口测试通过 (共 {result['total']} 个项目)")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_project_get_with_tags():
    """测试按标签查询接口."""
    print("测试: 按标签查询接口...")

    temp_dir = tempfile.mkdtemp()
    try:
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp/test")
        project_id = result["project_id"]

        # 注册标签
        tag_service.register_tag(project_id, "urgent", "紧急任务")
        tag_service.register_tag(project_id, "bug", "Bug相关")
        tag_service.register_tag(project_id, "api", "API相关")

        # 添加带标签的功能（使用 add_item 统一接口）
        project_service.add_item(
            project_id=project_id,
            group="features",
            content="修复登录bug的详细描述",
            summary="修复登录bug",
            status="pending",
            tags=["urgent", "bug"]
        )

        project_service.add_item(
            project_id=project_id,
            group="features",
            content="优化API性能的详细描述",
            summary="优化API性能",
            status="pending",
            tags=["api"]
        )

        # 查询所有数据并验证
        result = project_service.get_project(project_id)

        assert result is not None, "查询失败"
        assert len(result["data"]["features"]) == 2, f"功能数量不正确: {len(result['data']['features'])}"

        print(f"  ✓ 按标签查询测试通过 (找到 {len(result['data']['features'])} 个条目)")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_tag_operations_integration():
    """测试标签操作集成."""
    print("测试: 标签操作集成...")

    temp_dir = tempfile.mkdtemp()
    try:
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp/test")
        project_id = result["project_id"]

        # 注册标签
        result = tag_service.register_tag(project_id, "backend", "后端相关")
        assert result["success"], f"注册标签失败: {result}"

        # 查询标签信息 (使用 get_project 中的 tag_registry)
        project_data = project_service.get_project(project_id)
        tag_registry = project_data["data"].get("tag_registry", {})
        assert "backend" in tag_registry, "标签未正确注册"

        # 合并标签
        tag_service.register_tag(project_id, "server", "服务器端")
        result = tag_service.merge_tags(project_id, "server", "backend")
        assert result["success"], f"合并标签失败: {result}"

        print("  ✓ 标签操作集成测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_groups_list_integration():
    """测试分组列表接口."""
    print("测试: 分组列表接口...")

    temp_dir = tempfile.mkdtemp()
    try:
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)

        result = project_service.register_project("测试项目", "/tmp/test")
        project_id = result["project_id"]

        # 添加各分组内容（使用 add_item 统一接口）
        project_service.add_item(project_id=project_id, group="features", content="测试功能内容", summary="测试功能", status="pending", tags=[])
        project_service.add_item(project_id=project_id, group="notes", content="测试笔记", summary="笔记", tags=[])
        project_service.add_item(project_id=project_id, group="fixes", content="测试修复内容", summary="测试修复", status="pending", tags=[])
        project_service.add_item(project_id=project_id, group="standards", content="测试规范", summary="规范", tags=[])

        # 获取项目数据（包含所有分组）
        result = project_service.get_project(project_id)

        assert result is not None, "获取项目数据失败"

        # 验证分组数据
        data = result["data"]
        assert len(data["features"]) == 1, f"features 分组计数错误: {len(data['features'])}"
        assert len(data["notes"]) == 1, f"notes 分组计数错误: {len(data['notes'])}"
        assert len(data["fixes"]) == 1, f"fixes 分组计数错误: {len(data['fixes'])}"
        assert len(data["standards"]) == 1, f"standards 分组计数错误: {len(data['standards'])}"

        print("  ✓ 分组列表接口测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有集成测试."""
    print("=" * 60)
    print("MCP 工具接口集成测试")
    print("=" * 60)
    print()

    tests = [
        test_project_list_integration,
        test_project_get_with_tags,
        test_tag_operations_integration,
        test_groups_list_integration,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except AssertionError as e:
            failed += 1
            print(f"  ✗ 测试失败: {e}")
            print()
        except Exception as e:
            failed += 1
            print(f"  ✗ 测试错误: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
