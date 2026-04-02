#!/usr/bin/env python3
"""MCP接口: project_list 完整边界测试 (新三层架构).

测试列出项目接口的所有边界情况。

使用新架构：直接测试 business 层的 ProjectService
"""

import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService


class TestProjectListBasic:
    """基础功能测试."""

    def test_list_empty(self):
        """测试空项目列表."""
        print("测试: 空项目列表...")
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(storage_dir=temp_dir)
            project_service = ProjectService(storage)

            result = project_service.list_projects()

            assert result["success"], f"获取列表失败: {result}"
            assert result["total"] == 0
            assert result["projects"] == []

            print("  ✓ 空项目列表测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_list_with_projects(self):
        """测试有项目的列表."""
        print("测试: 有项目的列表...")
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(storage_dir=temp_dir)
            project_service = ProjectService(storage)

            # 创建项目
            project_service.register_project("项目1", "/path/project1", "项目1摘要", ["test"])
            project_service.register_project("项目2", "/path/project2", "项目2摘要", ["test"])
            project_service.register_project("项目3", "/path/project3", "项目3摘要", ["test"])

            result = project_service.list_projects()

            assert result["success"], f"获取列表失败: {result}"
            assert result["total"] == 3

            print("  ✓ 有项目的列表测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectListIncludeArchived:
    """归档项目测试."""

    def test_exclude_archived_default(self):
        """测试默认不包含归档项目."""
        print("测试: 默认不包含归档...")
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(storage_dir=temp_dir)
            project_service = ProjectService(storage)

            result1 = project_service.register_project("项目1", "/path/project1", "项目1摘要", ["test"])
            result2 = project_service.register_project("项目2", "/path/project2", "项目2摘要", ["test"])
            project_service.register_project("项目3", "/path/project3", "项目3摘要", ["test"])

            # 归档一个项目
            project_service.remove_project(result1["project_id"], mode="archive")

            result = project_service.list_projects(include_archived=False)

            assert result["success"], f"获取列表失败: {result}"
            assert result["total"] == 2  # 不包含归档

            print("  ✓ 默认不包含归档测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_include_archived_true(self):
        """测试包含归档项目."""
        print("测试: 包含归档...")
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(storage_dir=temp_dir)
            project_service = ProjectService(storage)

            result1 = project_service.register_project("项目1", "/path/project1", "项目1摘要", ["test"])
            result2 = project_service.register_project("项目2", "/path/project2", "项目2摘要", ["test"])
            project_service.register_project("项目3", "/path/project3", "项目3摘要", ["test"])

            # 归档一个项目
            project_service.remove_project(result1["project_id"], mode="archive")

            result = project_service.list_projects(include_archived=True)

            assert result["success"], f"获取列表失败: {result}"
            assert result["total"] == 3  # 包含归档

            print("  ✓ 包含归档测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: project_list 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestProjectListBasic,
        TestProjectListIncludeArchived,
    ]

    passed = 0
    failed = 0

    for test_class in test_classes:
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    method = getattr(instance, method_name)
                    method()
                    passed += 1
                except AssertionError as e:
                    failed += 1
                    print(f"  ✗ {method_name} 失败: {e}")
                except Exception as e:
                    failed += 1
                    print(f"  ✗ {method_name} 错误: {e}")

    print()
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
