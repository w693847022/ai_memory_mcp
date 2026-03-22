#!/usr/bin/env python
"""测试统计数据清理功能."""

import json
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from src.memory import CallStats


def test_stats_cleanup():
    """测试统计数据清理功能."""

    # 创建临时测试目录
    test_dir = Path("/tmp/test_stats_cleanup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    test_dir.mkdir(exist_ok=True)

    # 初始化统计
    stats = CallStats(str(test_dir))

    print("=== 测试1: 基本调用记录 ===")
    stats.record_call("project_register", "test_project", "claude-code", "local")
    stats.record_call("project_feature_add", "test_project", "claude-code", "local")
    stats.record_call("project_feature_add", "test_project", "cursor", "192.168.1.100")

    # 添加低使用率工具
    for i in range(5):  # 低于 MIN_USAGE_THRESHOLD (10)
        stats.record_call("rare_tool", "test_project", "claude-code", "local")

    print("✓ 记录了8次调用")

    print("\n=== 测试2: 查看清理前的数据 ===")
    result = stats.get_full_summary()
    print(f"✓ 工具数: {result['metadata']['total_tools']}")
    print(f"✓ 统计天数: {result['metadata']['total_days']}")

    print("\n=== 测试3: 手动清理统计数据 ===")
    # 保留0天（清理所有旧数据）
    cleanup_result = stats.cleanup_stats(retention_days=0)
    assert cleanup_result["success"], "清理失败"
    print("✓ 清理成功")
    print(f"  截止日期: {cleanup_result['cleanup_result']['cutoff_date']}")

    print("\n=== 测试4: 验证清理后的数据 ===")
    result = stats.get_full_summary()
    after_tools = result['metadata']['total_tools']
    after_days = result['metadata']['total_days']
    print(f"✓ 工具数: {after_tools}")
    print(f"✓ 统计天数: {after_days}")

    # 高使用率的工具应该保留
    result = stats.get_tool_stats("project_feature_add")
    assert result["success"], "高使用率工具应该保留"

    print("\n=== 测试5: 自动清理触发 ===")
    # 记录一些旧数据（模拟）
    stats.data["daily_stats"]["2020-01-01"] = {
        "total_calls": 100,
        "tools": {"old_tool": 50}
    }
    stats._save_stats()

    # 修改最后清理时间为很久以前，触发自动清理
    stats._last_cleanup_time = time.time() - (3600 * 2)  # 2小时前

    # 记录新调用，应该触发自动清理
    stats.record_call("project_note_add", "test_project", "claude-code", "local")

    # 验证旧数据被清理
    assert "2020-01-01" not in stats.data["daily_stats"], "旧数据应该被清理"
    print("✓ 自动清理成功触发")

    print("\n=== 测试6: 清理低使用率条目 ===")
    # 添加很多低使用率的工具和客户端
    for i in range(20):
        stats.record_call(f"temp_tool_{i}", "test_project", "temp_client", "local")

    # 清理
    cleanup_result = stats.cleanup_stats(retention_days=0)
    print(f"✓ 清理了 {cleanup_result['cleanup_result']['clients_cleaned']} 个客户端统计")
    print(f"✓ 清理了 {cleanup_result['cleanup_result']['tools_removed']} 个工具统计")

    # 清理
    shutil.rmtree(test_dir)
    print(f"\n✓ 测试完成，临时目录已清理")


def test_cleanup_preserves_recent_data():
    """测试清理保留最近数据."""

    # 创建临时测试目录
    test_dir = Path("/tmp/test_stats_cleanup_preserve_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    test_dir.mkdir(exist_ok=True)

    stats = CallStats(str(test_dir))

    print("=== 测试保留最近数据 ===")

    # 记录今天的调用
    stats.record_call("project_register", "test_project", "claude-code", "local")

    # 手动添加旧数据
    old_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
    stats.data["daily_stats"][old_date] = {
        "total_calls": 100,
        "tools": {"old_tool": 50}
    }
    stats.data["tool_calls"]["old_tool"] = {
        "total": 50,
        "by_project": {},
        "by_client": {},
        "by_ip": {},
        "first_called": f"{old_date}T12:00:00",
        "last_called": f"{old_date}T12:00:00"
    }
    stats._save_stats()

    print(f"✓ 添加了 {old_date} 的旧数据")

    # 清理30天前的数据
    cleanup_result = stats.cleanup_stats(retention_days=30)

    print(f"✓ 清理完成")
    print(f"  删除每日统计: {cleanup_result['cleanup_result']['daily_stats_removed']}")

    # 验证今天的数据还在
    result = stats.get_full_summary()
    assert result['metadata']['total_days'] == 1, "应该只保留今天的数据"
    print("✓ 最近数据保留成功")

    # 清理
    shutil.rmtree(test_dir)
    print(f"\n✓ 测试完成")


if __name__ == "__main__":
    test_stats_cleanup()
    test_cleanup_preserves_recent_data()
    print("\n=== 所有清理测试通过! ===")
