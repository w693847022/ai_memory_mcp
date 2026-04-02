#!/usr/bin/env python3
"""MCP接口: tag_* 完整边界测试 (新三层架构).

测试标签管理接口的所有边界情况：
- tag_register
- tag_update
- tag_delete
- tag_merge

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


class TestTagRegisterBasic:
    """tag_register 基础功能测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_register_tag_success(self):
        """测试注册标签成功."""
        print("测试: 注册标签成功...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = tag_service.register_tag(
                project_id=project_id,
                tag_name="api",
                summary="API相关标签"
            )

            assert result["success"], f"注册标签失败: {result}"

            print("  ✓ 注册标签成功测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_register_tag_with_aliases(self):
        """测试注册带别名的标签."""
        print("测试: 注册带别名的标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = tag_service.register_tag(
                project_id=project_id,
                tag_name="backend",
                summary="后端标签",
                aliases=["后端", "server"]
            )

            assert result["success"], f"注册带别名标签失败: {result}"

            print("  ✓ 注册带别名标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestTagRegisterValidation:
    """tag_register 参数验证测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_missing_tag_name(self):
        """测试缺少 tag_name."""
        print("测试: 缺少 tag_name...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = tag_service.register_tag(
                project_id=project_id,
                tag_name="",
                summary="测试"
            )

            assert not result["success"], "空 tag_name 应该失败"

            print("  ✓ 缺少 tag_name 测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_invalid_tag_name(self):
        """测试无效标签名."""
        print("测试: 无效标签名...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            invalid_names = ["tag with spaces", "标签", "标签!", "tag@"]

            for name in invalid_names:
                result = tag_service.register_tag(
                    project_id=project_id,
                    tag_name=name,
                    summary="测试"
                )

                # 无效标签名应该失败
                assert not result["success"] or "tag" in result.get("error", "").lower()

            print("  ✓ 无效标签名测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_register_duplicate_tag(self):
        """测试重复注册标签."""
        print("测试: 重复注册标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            # 第一次注册
            result1 = tag_service.register_tag(
                project_id=project_id,
                tag_name="duplicate",
                summary="重复标签测试"
            )
            assert result1["success"], f"第一次注册应该成功: {result1}"

            # 第二次注册
            result2 = tag_service.register_tag(
                project_id=project_id,
                tag_name="duplicate",
                summary="重复标签测试"
            )

            # 重复注册应该失败
            assert not result2["success"], "重复注册应该失败"

            print("  ✓ 重复注册标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestTagUpdateBasic:
    """tag_update 基础功能测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        # 先注册标签
        tag_service.register_tag(project_id, "test", "原摘要")

        return temp_dir, storage, project_service, tag_service, project_id

    def test_update_tag_summary(self):
        """测试更新标签摘要."""
        print("测试: 更新标签摘要...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = tag_service.update_tag(
                project_id=project_id,
                tag_name="test",
                summary="新摘要"
            )

            assert result["success"], f"更新标签失败: {result}"

            print("  ✓ 更新标签摘要测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestTagUpdateValidation:
    """tag_update 参数验证测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_update_nonexistent_tag(self):
        """测试更新不存在的标签."""
        print("测试: 更新不存在的标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = tag_service.update_tag(
                project_id=project_id,
                tag_name="nonexistent",
                summary="新摘要"
            )

            assert not result["success"], "不存在的标签应该失败"

            print("  ✓ 更新不存在的标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestTagDeleteBasic:
    """tag_delete 基础功能测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_delete_unused_tag(self):
        """测试删除未使用的标签."""
        print("测试: 删除未使用的标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            # 注册但未使用
            tag_service.register_tag(project_id, "unused", "未使用标签")

            result = tag_service.delete_tag(
                project_id=project_id,
                tag_name="unused"
            )

            assert result["success"], f"删除未使用标签失败: {result}"

            print("  ✓ 删除未使用标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_used_tag_with_force(self):
        """测试强制删除使用中的标签."""
        print("测试: 强制删除使用中的标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            # 注册并使用标签
            tag_service.register_tag(project_id, "used", "使用标签")
            project_service.add_item(
                project_id=project_id,
                group="features",
                summary="内容",
                content="内容",
                status="pending",
                tags=["used"]
            )

            result = tag_service.delete_tag(
                project_id=project_id,
                tag_name="used",
                force=True
            )

            assert result["success"], f"强制删除失败: {result}"

            print("  ✓ 强制删除使用中的标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_used_tag_without_force(self):
        """测试不强制删除使用中的标签."""
        print("测试: 不强制删除使用中的标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            tag_service.register_tag(project_id, "used2", "使用标签")
            project_service.add_item(
                project_id=project_id,
                group="features",
                summary="内容",
                content="内容",
                status="pending",
                tags=["used2"]
            )

            result = tag_service.delete_tag(
                project_id=project_id,
                tag_name="used2",
                force=False
            )

            assert not result["success"], "不强制删除使用中的标签应该失败"

            print("  ✓ 不强制删除使用中的标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestTagDeleteValidation:
    """tag_delete 参数验证测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_delete_nonexistent_tag(self):
        """测试删除不存在的标签."""
        print("测试: 删除不存在的标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = tag_service.delete_tag(
                project_id=project_id,
                tag_name="nonexistent"
            )

            assert not result["success"], "不存在的标签应该失败"

            print("  ✓ 删除不存在的标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestTagMergeBasic:
    """tag_merge 基础功能测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        # 注册两个标签
        tag_service.register_tag(project_id, "old_tag", "旧标签")
        tag_service.register_tag(project_id, "new_tag", "新标签")

        # 使用旧标签
        project_service.add_item(
            project_id=project_id,
            group="features",
            summary="内容",
            content="内容",
            status="pending",
            tags=["old_tag"]
        )

        return temp_dir, storage, project_service, tag_service, project_id

    def test_merge_tags_success(self):
        """测试合并标签成功."""
        print("测试: 合并标签成功...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = tag_service.merge_tags(
                project_id=project_id,
                old_tag="old_tag",
                new_tag="new_tag"
            )

            assert result["success"], f"合并标签失败: {result}"

            print("  ✓ 合并标签成功测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestTagMergeValidation:
    """tag_merge 参数验证测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_merge_nonexistent_old_tag(self):
        """测试合并不存在的旧标签."""
        print("测试: 合并不存在的旧标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            tag_service.register_tag(project_id, "new", "新标签")

            result = tag_service.merge_tags(
                project_id=project_id,
                old_tag="nonexistent",
                new_tag="new"
            )

            assert not result["success"], "不存在的旧标签应该失败"

            print("  ✓ 合并不存在的旧标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_merge_same_tag(self):
        """测试合并相同标签."""
        print("测试: 合并相同标签...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            tag_service.register_tag(project_id, "same", "相同标签")

            result = tag_service.merge_tags(
                project_id=project_id,
                old_tag="same",
                new_tag="same"
            )

            # 合并相同标签应该失败
            assert not result["success"], "合并相同标签应该失败"

            print("  ✓ 合并相同标签测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: tag_* 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestTagRegisterBasic,
        TestTagRegisterValidation,
        TestTagUpdateBasic,
        TestTagUpdateValidation,
        TestTagDeleteBasic,
        TestTagDeleteValidation,
        TestTagMergeBasic,
        TestTagMergeValidation,
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
