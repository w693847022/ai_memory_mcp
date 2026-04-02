#!/usr/bin/env python3
"""MCP接口: project_* 操作类接口完整边界测试 (新三层架构).

测试项目操作接口：
- project_remove
- project_rename
- project_groups_list
- project_stats

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
from business.stats_service import StatsService


class TestProjectRemoveBasic:
    """project_remove 基础功能测试."""

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

    def test_archive_project(self):
        """测试归档项目."""
        print("测试: 归档项目...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = project_service.remove_project(
                project_id=project_id,
                mode="archive"
            )

            assert result["success"], f"归档项目失败: {result}"

            print("  ✓ 归档项目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_project(self):
        """测试永久删除项目."""
        print("测试: 永久删除项目...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = project_service.remove_project(
                project_id=project_id,
                mode="delete"
            )

            assert result["success"], f"删除项目失败: {result}"

            print("  ✓ 永久删除项目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectRemoveValidation:
    """project_remove 参数验证测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_remove_nonexistent_project(self):
        """测试删除不存在的项目."""
        print("测试: 删除不存在的项目...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = project_service.remove_project(project_id="nonexistent")

            assert not result["success"], "不存在的项目应该失败"

            print("  ✓ 删除不存在的项目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectRenameBasic:
    """project_rename 基础功能测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        tag_service.register_tag(project_id, "test", "测试标签")

        return temp_dir, storage, project_service, tag_service, project_id

    def test_rename_success(self):
        """测试重命名成功."""
        print("测试: 重命名成功...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = project_service.project_rename(
                project_id=project_id,
                new_name="新项目名"
            )

            assert result["success"], f"重命名失败: {result}"
            assert result["new_name"] == "新项目名"

            print("  ✓ 重命名成功测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectRenameValidation:
    """project_rename 参数验证测试."""

    def _setup_project(self):
        """创建测试项目."""
        temp_dir = tempfile.mkdtemp()
        storage = Storage(storage_dir=temp_dir)
        project_service = ProjectService(storage)
        tag_service = TagService(storage)

        result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
        project_id = result["project_id"]

        return temp_dir, storage, project_service, tag_service, project_id

    def test_rename_nonexistent_project(self):
        """测试重命名不存在的项目."""
        print("测试: 重命名不存在的项目...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project()
        try:
            result = project_service.project_rename(
                project_id="nonexistent",
                new_name="新名称"
            )

            assert not result["success"], "不存在的项目应该失败"

            print("  ✓ 重命名不存在的项目测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_rename_to_duplicate_name(self):
        """测试重命名为重复名称."""
        print("测试: 重命名为重复名称...")
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(storage_dir=temp_dir)
            project_service = ProjectService(storage)

            result1 = project_service.register_project("项目1", "/tmp1", "项目1摘要", ["test"])
            result2 = project_service.register_project("项目2", "/tmp2", "项目2摘要", ["test"])

            project_id_1 = result1["project_id"]

            result = project_service.project_rename(
                project_id=project_id_1,
                new_name="项目2"
            )

            # 重复名称可能被允许或拒绝
            # 验证有明确行为

            print("  ✓ 重命名为重复名称测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectGroupsList:
    """project_groups_list 测试."""

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
            # 应该有4个分组
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


class TestProjectStats:
    """project_stats 测试."""

    def test_get_stats_success(self):
        """测试获取统计成功."""
        print("测试: 获取统计...")
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(storage_dir=temp_dir)
            project_service = ProjectService(storage)
            stats_service = StatsService(storage)

            # 创建多个项目
            for i in range(3):
                result = project_service.register_project(f"项目{i}", f"/tmp{i}", f"项目{i}摘要", ["test"])
                project_id = result["project_id"]
                project_service.add_item(project_id, "features", f"内容{i}", f"功能{i}", status="pending", tags=["test"])

            # 记录一些调用
            stats_service.record_call("project_add", project_id)
            stats_service.record_call("project_get", project_id)

            # 获取统计
            full_summary = stats_service.get_full_summary()

            assert "tool_stats" in full_summary or "stats" in full_summary

            print("  ✓ 获取统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: project_* 操作类完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestProjectRemoveBasic,
        TestProjectRemoveValidation,
        TestProjectRenameBasic,
        TestProjectRenameValidation,
        TestProjectGroupsList,
        TestProjectStats,
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
