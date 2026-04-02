#!/usr/bin/env python3
"""MCP接口: stats_* 完整边界测试 (新三层架构).

测试统计接口：
- stats_summary
- stats_cleanup

使用新架构：直接测试 business 层的 StatsService
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService
from business.tag_service import TagService
from business.stats_service import StatsService


def _setup_with_stats():
    """创建带统计的测试环境."""
    temp_dir = tempfile.mkdtemp()
    storage = Storage(storage_dir=temp_dir)
    project_service = ProjectService(storage)
    tag_service = TagService(storage)
    stats_service = StatsService(storage)

    # 创建项目并记录调用
    result = project_service.register_project("测试项目", "/tmp", "测试", ["test"])
    project_id = result["project_id"]

    # 记录一些调用
    stats_service.record_call("project_add", project_id)
    stats_service.record_call("project_get", project_id)
    stats_service.record_call("project_get", project_id)

    return temp_dir, storage, project_service, tag_service, stats_service, project_id


class TestStatsSummaryTypeTool:
    """stats_summary type=tool 测试."""

    def test_tool_stats_all(self):
        """测试获取所有工具统计."""
        print("测试: 所有工具统计...")
        temp_dir, storage, project_service, tag_service, stats_service, project_id = _setup_with_stats()
        try:
            result = stats_service.get_tool_stats()

            assert "tools" in result or "stats" in result

            print("  ✓ 所有工具统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_tool_stats_specific(self):
        """测试获取特定工具统计."""
        print("测试: 特定工具统计...")
        temp_dir, storage, project_service, tag_service, stats_service, project_id = _setup_with_stats()
        try:
            result = stats_service.get_tool_stats("project_get")

            # 应该返回特定工具的统计
            assert result is not None

            print("  ✓ 特定工具统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStatsSummaryTypeProject:
    """stats_summary type=project 测试."""

    def test_project_stats(self):
        """测试获取项目统计."""
        print("测试: 项目统计...")
        temp_dir, storage, project_service, tag_service, stats_service, project_id = _setup_with_stats()
        try:
            result = stats_service.get_project_stats(project_id)

            assert result is not None

            print("  ✓ 项目统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStatsSummaryTypeClient:
    """stats_summary type=client 测试."""

    def test_client_stats(self):
        """测试获取客户端统计."""
        print("测试: 客户端统计...")
        temp_dir, storage, project_service, tag_service, stats_service, project_id = _setup_with_stats()
        try:
            result = stats_service.get_client_stats()

            assert result is not None

            print("  ✓ 客户端统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStatsSummaryTypeIp:
    """stats_summary type=ip 测试."""

    def test_ip_stats(self):
        """测试获取 IP 统计."""
        print("测试: IP 统计...")
        temp_dir, storage, project_service, tag_service, stats_service, project_id = _setup_with_stats()
        try:
            result = stats_service.get_ip_stats()

            assert result is not None

            print("  ✓ IP 统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStatsSummaryTypeDaily:
    """stats_summary type=daily 测试."""

    def test_daily_stats_all(self):
        """测试获取所有日统计."""
        print("测试: 所有日统计...")
        temp_dir, storage, project_service, tag_service, stats_service, project_id = _setup_with_stats()
        try:
            result = stats_service.get_daily_stats()

            assert result is not None

            print("  ✓ 所有日统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_daily_stats_specific_date(self):
        """测试获取特定日期统计."""
        print("测试: 特定日期统计...")
        temp_dir, storage, project_service, tag_service, stats_service, project_id = _setup_with_stats()
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            result = stats_service.get_daily_stats(today)

            assert result is not None

            print("  ✓ 特定日期统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStatsSummaryTypeFull:
    """stats_summary type=full 测试."""

    def test_full_stats(self):
        """测试获取完整统计."""
        print("测试: 完整统计...")
        temp_dir, storage, project_service, tag_service, stats_service, project_id = _setup_with_stats()
        try:
            result = stats_service.get_full_summary()

            assert result is not None

            print("  ✓ 完整统计测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStatsCleanup:
    """stats_cleanup 测试."""

    def test_cleanup_default_days(self):
        """测试默认保留天数清理."""
        print("测试: 默认保留天数清理...")
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(storage_dir=temp_dir)
            stats_service = StatsService(storage)

            result = stats_service.cleanup_stats()

            assert result is not None

            print("  ✓ 默认保留天数清理测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cleanup_custom_days(self):
        """测试自定义保留天数."""
        print("测试: 自定义保留天数...")
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(storage_dir=temp_dir)
            stats_service = StatsService(storage)

            result = stats_service.cleanup_stats(retention_days=7)

            assert result is not None

            print("  ✓ 自定义保留天数测试通过")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("MCP接口: stats_* 完整边界测试 (新三层架构)")
    print("=" * 60)
    print()

    test_classes = [
        TestStatsSummaryTypeTool,
        TestStatsSummaryTypeProject,
        TestStatsSummaryTypeClient,
        TestStatsSummaryTypeIp,
        TestStatsSummaryTypeDaily,
        TestStatsSummaryTypeFull,
        TestStatsCleanup,
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
