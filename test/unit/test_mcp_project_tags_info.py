#!/usr/bin/env python3
"""MCP接口: project_tags_info 完整边界测试 (新三层架构).

测试查询标签信息接口。

使用新架构：直接测试 business 层的 TagService
"""

import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService
from business.tag_service import TagService


class TestProjectTagsInfoBasic:
    """基础功能测试."""

    def _setup_project_with_tags(self):
        """创建带标签的测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        # 注册多个标签
        tag_service.register_tag(project_id, "api", "API接口标签")
        tag_service.register_tag(project_id, "backend", "后端标签")
        tag_service.register_tag(project_id, "frontend", "前端标签")

        # 添加使用标签的条目
        project_service.add_item(project_id, "features", "内容1", "API功能", status="pending", tags=["api", "backend"])
        project_service.add_item(project_id, "features", "内容2", "UI优化", status="pending", tags=["frontend"])

        return temp_dir, storage, project_service, tag_service, project_id

    def test_list_all_registered_tags(self):
        """测试列出所有已注册标签."""
        print("测试: 列出所有已注册标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_tags()
        try:
            result = tag_service.list_all_registered_tags(project_id)

            assert result["success"], f"列出标签失败: {result}"
            assert "tags" in result
            assert result["total_tags"] >= 3

            print("  ✓ 列出所有已注册标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_list_group_tags(self):
        """测试列出分组标签."""
        print("测试: 列出分组标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_tags()
        try:
            result = tag_service.list_group_tags(
                project_id=project_id,
                group_name="features"
            )

            assert result["success"], f"列出分组标签失败: {result}"
            assert "tags" in result

            print("  ✓ 列出分组标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectTagsInfoRequiredParams:
    """必填参数验证测试."""

    def _setup_project_with_tags(self):
        """创建带标签的测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_nonexistent_project(self):
        """测试不存在的项目."""
        print("测试: 不存在的项目...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_tags()
        try:
            result = tag_service.list_all_registered_tags(project_id="nonexistent")

            assert not result["success"], "不存在的项目应该失败"

            print("  ✓ 不存在的项目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectTagsInfoTagQuery:
    """标签查询测试."""

    def _setup_project_with_tags(self):
        """创建带标签的测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        # 注册标签
        tag_service.register_tag(project_id, "api", "API接口标签")
        tag_service.register_tag(project_id, "backend", "后端标签")

        # 添加使用标签的条目
        project_service.add_item(project_id, "features", "内容1", "API功能", status="pending", tags=["api"])
        project_service.add_item(project_id, "features", "内容2", "后端功能", status="pending", tags=["backend"])

        return temp_dir, storage, project_service, tag_service, project_id

    def test_query_by_tag(self):
        """测试查询标签下的条目."""
        print("测试: 查询标签下的条目...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_tags()
        try:
            result = tag_service.query_by_tag(
                project_id=project_id,
                group_name="features",
                tag="api"
            )

            assert result["success"], f"查询标签条目失败: {result}"
            assert "items" in result
            assert result["total"] >= 1

            print("  ✓ 查询标签下的条目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectTagsInfoEdgeCases:
    """边缘情况测试."""

    def _setup_project_with_tags(self):
        """创建带标签的测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_empty_project(self):
        """测试空项目."""
        print("测试: 空项目...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_tags()
        try:
            result = tag_service.list_all_registered_tags(project_id)

            assert result["success"], "空项目应该成功"
            assert result["total_tags"] >= 0

            print("  ✓ 空项目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: project_tags_info 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestProjectTagsInfoBasic,
        TestProjectTagsInfoRequiredParams,
        TestProjectTagsInfoTagQuery,
        TestProjectTagsInfoEdgeCases,
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
