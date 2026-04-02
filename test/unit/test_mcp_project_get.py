#!/usr/bin/env python3
"""MCP接口: project_get 完整边界测试 (新三层架构).

测试获取项目/条目接口的所有边界情况。

使用新架构：直接测试 business 层的 ProjectService
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService
from business.tag_service import TagService


class TestProjectGetBasic:
    """基础功能测试."""

    def _setup_project_with_items(self):
        """创建测试项目和多个条目."""
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

        # 添加各种状态的条目
        project_service.add_item(project_id, "features", "内容1", "功能A", status="pending", tags=["test"])
        project_service.add_item(project_id, "features", "内容2", "功能B", status="in_progress", tags=["api"])
        project_service.add_item(project_id, "features", "内容3", "功能C", status="completed", tags=["backend"])
        project_service.add_item(project_id, "fixes", "修复1", "修复A", status="pending", severity="high", tags=["test"])
        project_service.add_item(project_id, "notes", "笔记1", "笔记A", tags=["test"])
        project_service.add_item(project_id, "standards", "规范1", "规范A", tags=["test"])

        return temp_dir, storage, project_service, tag_service, project_id

    def test_get_project_info(self):
        """测试获取项目信息（不传 group_name）."""
        print("测试: 获取项目信息...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_items()
        try:
            result = project_service.get_project(project_id)

            assert result["success"], f"获取项目信息失败: {result}"
            assert "data" in result
            assert "info" in result["data"]

            print("  ✓ 获取项目信息测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_group_list(self):
        """测试获取分组列表."""
        print("测试: 获取分组列表...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_items()
        try:
            project_data = project_service.get_project(project_id)
            features = project_data["data"].get("features", [])

            assert len(features) == 3, f"应该有3个features，实际有{len(features)}"

            print("  ✓ 获取分组列表测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_item_detail(self):
        """测试获取条目详情."""
        print("测试: 获取条目详情...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_items()
        try:
            project_data = project_service.get_project(project_id)
            item_id = project_data["data"]["features"][0]["id"]

            # 获取特定条目 - 需要遍历查找
            features = project_data["data"].get("features", [])
            item = None
            for f in features:
                if f["id"] == item_id:
                    item = f
                    break

            assert item is not None, f"应该找到条目 {item_id}"
            assert "content" in item or "summary" in item

            print("  ✓ 获取条目详情测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectGetParams:
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

        project_service.add_item(project_id, "features", "内容1", "功能A", status="pending", tags=["test"])

        return temp_dir, storage, project_service, tag_service, project_id

    def test_missing_project_id(self):
        """测试缺少 project_id."""
        print("测试: 缺少 project_id...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_items()
        try:
            result = project_service.get_project("")

            assert not result["success"], "空 project_id 应该失败"

            print("  ✓ 缺少 project_id 测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_nonexistent_project_id(self):
        """测试不存在的项目ID."""
        print("测试: 不存在的项目ID...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_items()
        try:
            result = project_service.get_project("nonexistent-id")

            assert not result["success"], "不存在的项目应该失败"

            print("  ✓ 不存在的项目ID测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectGetFilters:
    """过滤条件测试."""

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

        project_service.add_item(project_id, "features", "内容1", "功能A", status="pending", tags=["test"])
        project_service.add_item(project_id, "features", "内容2", "功能B", status="in_progress", tags=["api"])
        project_service.add_item(project_id, "features", "内容3", "功能C", status="completed", tags=["backend"])
        project_service.add_item(project_id, "fixes", "修复1", "修复A", status="pending", severity="high", tags=["test"])

        return temp_dir, storage, project_service, tag_service, project_id

    def test_status_filter(self):
        """测试状态过滤."""
        print("测试: 状态过滤...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_items()
        try:
            project_data = project_service.get_project(project_id)
            features = project_data["data"].get("features", [])

            pending_items = [f for f in features if f.get("status") == "pending"]
            assert len(pending_items) == 1, f"应该有1个pending，实际有{len(pending_items)}"

            print("  ✓ 状态过滤测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_severity_filter(self):
        """测试严重程度过滤."""
        print("测试: 严重程度过滤...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_items()
        try:
            project_data = project_service.get_project(project_id)
            fixes = project_data["data"].get("fixes", [])

            high_fixes = [f for f in fixes if f.get("severity") == "high"]
            assert len(high_fixes) == 1, f"应该有1个high severity的fix，实际有{len(high_fixes)}"

            print("  ✓ 严重程度过滤测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectGetEdgeCases:
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

        project_service.add_item(project_id, "features", "内容1", "功能A", status="pending", tags=["test"])

        return temp_dir, storage, project_service, tag_service, project_id

    def test_get_empty_group(self):
        """测试获取空分组."""
        print("测试: 获取空分组...")
        temp_dir, storage, project_service, tag_service, project_id = self._setup_project_with_items()
        try:
            project_data = project_service.get_project(project_id)

            # 某个分组可能为空
            empty_group = project_data["data"].get("standards", [])
            assert isinstance(empty_group, list), "分组应该返回列表"

            print("  ✓ 获取空分组测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: project_get 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestProjectGetBasic,
        TestProjectGetParams,
        TestProjectGetFilters,
        TestProjectGetEdgeCases,
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
