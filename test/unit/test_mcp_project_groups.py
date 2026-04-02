#!/usr/bin/env python3
"""MCP接口: project_groups 完整边界测试 (新三层架构).

测试分组管理接口。

使用新架构：直接测试 business 层的 ProjectService
"""

import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService
from business.tag_service import TagService


class TestProjectGroupsBasic:
    """基础功能测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        tag_service.register_tag(project_id, "test", "测试标签")

        # 添加一些条目
        project_service.add_item(project_id, "features", "内容", "功能", status="pending", tags=["test"])
        project_service.add_item(project_id, "notes", "笔记", "笔记", tags=["test"])

        return temp_dir, storage, project_service, tag_service, project_id

    def test_list_groups_success(self):
        """测试列出分组成功."""
        print("测试: 列出分组...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = project_service.list_groups(project_id=project_id)

            assert result["success"], f"列出分组失败: {result}"
            assert "groups" in result
            # 应该有4个内置分组
            assert len(result["groups"]) == 4

            print("  ✓ 列出分组测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_list_groups_nonexistent_project(self):
        """测试列出不存在项目的分组."""
        print("测试: 列出不存在项目的分组...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = project_service.list_groups(project_id="nonexistent")

            assert not result["success"], "不存在的项目应该失败"

            print("  ✓ 列出不存在项目的分组测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: project_groups 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestProjectGroupsBasic,
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
