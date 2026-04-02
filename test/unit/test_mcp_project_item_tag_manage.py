#!/usr/bin/env python3
"""MCP接口: project_item_tag_manage 完整边界测试 (新三层架构).

测试管理条目标签接口的所有边界情况。

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


class TestProjectItemTagManageSet:
    """operation=set 测试."""

    def _setup_project_with_item(self):
        """创建带条目的测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        # 注册标签
        tag_service.register_tag(project_id, "test", "测试标签")
        tag_service.register_tag(project_id, "api", "API标签")
        tag_service.register_tag(project_id, "backend", "后端标签")

        # 添加带标签的条目
        result = project_service.add_item(
            project_id=project_id,
            group="features",
            content="功能内容",
            summary="功能测试",
            status="pending",
            tags=["test"]
        )
        item_id = result["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id

    def test_set_tags_success(self):
        """测试设置标签成功."""
        print("测试: 设置标签成功...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_item()
        try:
            # 使用 update_item 来设置标签
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id=item_id,
                tags=["api", "backend"]
            )

            assert result["success"], f"设置标签失败: {result}"

            print("  ✓ 设置标签成功测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectItemTagManageAdd:
    """operation=add 测试."""

    def _setup_project_with_item(self):
        """创建带条目的测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        # 注册标签
        tag_service.register_tag(project_id, "test", "测试标签")
        tag_service.register_tag(project_id, "api", "API标签")

        # 添加带标签的条目
        result = project_service.add_item(
            project_id=project_id,
            group="features",
            content="功能内容",
            summary="功能测试",
            status="pending",
            tags=["test"]
        )
        item_id = result["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id

    def test_add_tag_success(self):
        """测试添加标签成功."""
        print("测试: 添加标签成功...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_item()
        try:
            result = tag_service.add_item_tag(
                project_id=project_id,
                group_name="features",
                item_id=item_id,
                tag="api"
            )

            assert result["success"], f"添加标签失败: {result}"
            assert "api" in result["tags"]

            print("  ✓ 添加标签成功测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectItemTagManageRemove:
    """operation=remove 测试."""

    def _setup_project_with_item(self):
        """创建带条目的测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        # 注册标签
        tag_service.register_tag(project_id, "test", "测试标签")
        tag_service.register_tag(project_id, "api", "API标签")

        # 添加带标签的条目
        result = project_service.add_item(
            project_id=project_id,
            group="features",
            content="功能内容",
            summary="功能测试",
            status="pending",
            tags=["test", "api"]
        )
        item_id = result["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id

    def test_remove_tag_success(self):
        """测试移除标签成功."""
        print("测试: 移除标签成功...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_item()
        try:
            result = tag_service.remove_item_tag(
                project_id=project_id,
                group_name="features",
                item_id=item_id,
                tag="test"
            )

            assert result["success"], f"移除标签失败: {result}"
            assert "test" not in result["tags"]

            print("  ✓ 移除标签成功测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectItemTagManageEdgeCases:
    """边缘情况测试."""

    def _setup_project_with_item(self):
        """创建带条目的测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        # 注册标签
        tag_service.register_tag(project_id, "test", "测试标签")

        # 添加带标签的条目
        result = project_service.add_item(
            project_id=project_id,
            group="features",
            content="功能内容",
            summary="功能测试",
            status="pending",
            tags=["test"]
        )
        item_id = result["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id

    def test_manage_nonexistent_item(self):
        """测试管理不存在的条目."""
        print("测试: 管理不存在的条目...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_item()
        try:
            result = tag_service.add_item_tag(
                project_id=project_id,
                group_name="features",
                item_id="nonexistent-item-id",
                tag="api"
            )

            assert not result["success"], "不存在的条目应该失败"

            print("  ✓ 管理不存在的条目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_add_unregistered_tag(self):
        """测试添加未注册标签."""
        print("测试: 添加未注册标签...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_item()
        try:
            result = tag_service.add_item_tag(
                project_id=project_id,
                group_name="features",
                item_id=item_id,
                tag="unregistered"
            )

            # 未注册标签应该失败
            assert not result["success"], "未注册标签应该失败"

            print("  ✓ 添加未注册标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: project_item_tag_manage 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestProjectItemTagManageSet,
        TestProjectItemTagManageAdd,
        TestProjectItemTagManageRemove,
        TestProjectItemTagManageEdgeCases,
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
