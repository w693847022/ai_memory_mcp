#!/usr/bin/env python3
"""MCP接口: project_update 完整边界测试 (新三层架构).

测试更新项目条目接口的所有边界情况。

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


class TestProjectUpdateBasic:
    """基础功能测试."""

    def _setup_project_with_items(self):
        """创建测试项目和多个条目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        tag_service.register_tag(project_id, "test", "测试标签")
        tag_service.register_tag(project_id, "api", "API标签")
        tag_service.register_tag(project_id, "backend", "后端标签")

        result1 = project_service.add_item(
            project_id=project_id,
            group="features",
            summary="功能A",
            content="内容A",
            status="pending",
            tags=["test"]
        )
        item_id = result1["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id

    def test_update_summary_success(self):
        """测试更新摘要成功."""
        print("测试: 更新摘要...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id=item_id,
                summary="新摘要"
            )

            assert result["success"], f"更新摘要失败: {result}"

            print("  ✓ 更新摘要测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_update_status_success(self):
        """测试更新状态成功."""
        print("测试: 更新状态...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id=item_id,
                status="completed"
            )

            assert result["success"], f"更新状态失败: {result}"

            print("  ✓ 更新状态测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_update_content_success(self):
        """测试更新内容成功."""
        print("测试: 更新内容...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id=item_id,
                content="新内容"
            )

            assert result["success"], f"更新内容失败: {result}"

            print("  ✓ 更新内容测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_update_tags(self):
        """测试更新标签."""
        print("测试: 更新标签...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id=item_id,
                tags=["api", "backend"]
            )

            assert result["success"], f"更新标签失败: {result}"

            print("  ✓ 更新标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_update_multiple_fields(self):
        """测试同时更新多个字段."""
        print("测试: 更新多个字段...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id=item_id,
                summary="新摘要",
                content="新内容",
                status="completed",
                tags=["backend"]
            )

            assert result["success"], f"更新多个字段失败: {result}"

            print("  ✓ 更新多个字段测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectUpdateParams:
    """参数验证测试."""

    def _setup_project_with_items(self):
        """创建测试项目和多个条目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        tag_service.register_tag(project_id, "test", "测试标签")

        result1 = project_service.add_item(
            project_id=project_id,
            group="features",
            summary="功能A",
            content="内容A",
            status="pending",
            tags=["test"]
        )
        item_id = result1["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id

    def test_update_nonexistent_item(self):
        """测试更新不存在的条目."""
        print("测试: 更新不存在的条目...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id="nonexistent-item-id",
                summary="新摘要"
            )

            assert not result["success"], "更新不存在的条目应该失败"

            print("  ✓ 更新不存在的条目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_update_without_any_fields(self):
        """测试不提供任何更新字段."""
        print("测试: 不提供任何更新字段...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id=item_id
            )

            # 应该成功（没有实际更新）
            assert result["success"], f"不提供更新字段应该成功: {result}"

            print("  ✓ 不提供任何更新字段测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectUpdateTagsValidation:
    """标签更新验证测试."""

    def _setup_project_with_items(self):
        """创建测试项目和多个条目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        tag_service.register_tag(project_id, "test", "测试标签")
        tag_service.register_tag(project_id, "api", "API标签")
        tag_service.register_tag(project_id, "backend", "后端标签")

        result1 = project_service.add_item(
            project_id=project_id,
            group="features",
            summary="功能A",
            content="内容A",
            status="pending",
            tags=["test"]
        )
        item_id = result1["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id

    def test_update_with_registered_tags(self):
        """测试更新使用已注册标签."""
        print("测试: 已注册标签...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id=project_id,
                group="features",
                item_id=item_id,
                tags=["api", "backend"]
            )

            assert result["success"], "已注册标签应该成功"

            print("  ✓ 已注册标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectUpdateEdgeCases:
    """边缘情况测试."""

    def _setup_project_with_items(self):
        """创建测试项目和多个条目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        tag_service.register_tag(project_id, "test", "测试标签")

        result1 = project_service.add_item(
            project_id=project_id,
            group="features",
            summary="功能A",
            content="内容A",
            status="pending",
            tags=["test"]
        )
        item_id = result1["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id

    def test_update_nonexistent_project(self):
        """测试更新不存在的项目."""
        print("测试: 更新不存在的项目...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.update_item(
                project_id="nonexistent-project-id",
                group="features",
                item_id=item_id,
                summary="新摘要"
            )

            assert not result["success"], "不存在的项目应该失败"

            print("  ✓ 更新不存在的项目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: project_update 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestProjectUpdateBasic,
        TestProjectUpdateParams,
        TestProjectUpdateTagsValidation,
        TestProjectUpdateEdgeCases,
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
