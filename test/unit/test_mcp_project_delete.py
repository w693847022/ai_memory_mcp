#!/usr/bin/env python3
"""MCP接口: project_delete 完整边界测试 (新三层架构).

测试删除项目条目接口的所有边界情况。

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


class TestProjectDeleteBasic:
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

        # 添加条目
        result1 = project_service.add_item(
            project_id=project_id,
            group="features",
            summary="功能A",
            content="内容A",
            status="pending",
            tags=["test"]
        )
        item_id = result1["item_id"]

        result2 = project_service.add_item(
            project_id=project_id,
            group="features",
            summary="功能B",
            content="内容B",
            status="pending",
            tags=["test"]
        )
        item_id2 = result2["item_id"]

        return temp_dir, storage, project_service, tag_service, project_id, item_id, item_id2

    def test_delete_item_success(self):
        """测试删除条目成功."""
        print("测试: 删除条目...")
        temp_dir, storage, project_service, tag_service, project_id, item_id, item_id2 = self._setup_project_with_items()
        try:
            result = project_service.delete_item(
                project_id=project_id,
                group="features",
                item_id=item_id
            )

            assert result["success"], f"删除条目失败: {result}"

            print("  ✓ 删除条目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_nonexistent_item(self):
        """测试删除不存在的条目."""
        print("测试: 删除不存在的条目...")
        temp_dir, storage, project_service, tag_service, project_id, item_id, item_id2 = self._setup_project_with_items()
        try:
            result = project_service.delete_item(
                project_id=project_id,
                group="features",
                item_id="nonexistent-item-id"
            )

            assert not result["success"], "删除不存在的条目应该失败"

            print("  ✓ 删除不存在的条目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_item_wrong_group(self):
        """测试从错误分组删除条目."""
        print("测试: 从错误分组删除条目...")
        temp_dir, storage, project_service, tag_service, project_id, item_id, item_id2 = self._setup_project_with_items()
        try:
            # item_id 属于 features，尝试从 notes 删除
            result = project_service.delete_item(
                project_id=project_id,
                group="notes",
                item_id=item_id
            )

            assert not result["success"], "从错误分组删除应该失败"

            print("  ✓ 从错误分组删除条目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectDeleteEdgeCases:
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

    def test_delete_from_nonexistent_project(self):
        """测试从不存在的项目删除条目."""
        print("测试: 从不存在的项目删除条目...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.delete_item(
                project_id="nonexistent-project-id",
                group="features",
                item_id=item_id
            )

            assert not result["success"], "从不存在的项目删除应该失败"

            print("  ✓ 从不存在的项目删除条目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_last_item(self):
        """测试删除最后一个条目."""
        print("测试: 删除最后一个条目...")
        temp_dir, storage, project_service, tag_service, project_id, item_id = self._setup_project_with_items()
        try:
            result = project_service.delete_item(
                project_id=project_id,
                group="features",
                item_id=item_id
            )

            assert result["success"], f"删除最后一个条目应该成功: {result}"

            # 验证分组为空
            project_data = project_service.get_project(project_id)
            features = project_data["data"].get("features", [])
            assert len(features) == 0, "features 分组应该为空"

            print("  ✓ 删除最后一个条目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: project_delete 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestProjectDeleteBasic,
        TestProjectDeleteEdgeCases,
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
