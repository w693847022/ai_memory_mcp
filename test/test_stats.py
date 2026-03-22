#!/usr/bin/env python
"""测试调用统计功能."""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from src.memory import CallStats

# 测试统计功能
def test_call_stats():
    """测试 CallStats 类."""

    # 创建临时测试目录
    test_dir = Path("/tmp/test_stats_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    test_dir.mkdir(exist_ok=True)

    # 初始化统计
    stats = CallStats(str(test_dir))

    print("=== 测试1: 基本调用记录 ===")
    stats.record_call("project_register", "test_project", "claude-code", "local")
    stats.record_call("project_feature_add", "test_project", "claude-code", "local")
    stats.record_call("project_feature_add", "test_project", "cursor", "192.168.1.100")
    print("✓ 记录了3次调用")

    print("\n=== 测试2: 工具统计 ===")
    result = stats.get_tool_stats("project_feature_add")
    assert result["success"], "获取工具统计失败"
    assert result["total"] == 2, f"期望2次调用，实际{result['total']}"
    print(f"✓ project_feature_add: {result['total']} 次调用")

    print("\n=== 测试3: 项目统计 ===")
    result = stats.get_project_stats("test_project")
    assert result["success"], "获取项目统计失败"
    assert result["total_calls"] == 3, f"期望3次调用，实际{result['total_calls']}"
    print(f"✓ test_project: {result['total_calls']} 次调用")
    print(f"  工具: {result['tools_called']}")

    print("\n=== 测试4: 客户端统计 ===")
    result = stats.get_client_stats()
    assert result["success"], "获取客户端统计失败"
    print("✓ 客户端统计:")
    for client, count in result["clients"]:
        print(f"  {client}: {count} 次")

    print("\n=== 测试5: IP统计 ===")
    result = stats.get_ip_stats()
    assert result["success"], "获取IP统计失败"
    print("✓ IP统计:")
    for ip, count in result["ips"]:
        print(f"  {ip}: {count} 次")

    print("\n=== 测试6: 每日统计 ===")
    result = stats.get_daily_stats()
    assert result["success"], "获取每日统计失败"
    print(f"✓ 统计天数: {len(result['recent_days'])}")

    print("\n=== 测试7: 完整统计 ===")
    result = stats.get_full_summary()
    assert result["success"], "获取完整统计失败"
    print(f"✓ 总调用次数: {result['metadata']['total_calls']}")
    print(f"✓ 已统计工具数: {result['metadata']['total_tools']}")

    print("\n=== 测试8: 多次调用同一工具 ===")
    for i in range(5):
        stats.record_call("project_note_add", "test_project", "cursor", "local")
    result = stats.get_tool_stats("project_note_add")
    assert result["total"] == 5, f"期望5次调用，实际{result['total']}"
    print(f"✓ project_note_add: {result['total']} 次调用")

    print("\n=== 测试9: 查看统计文件 ===")
    stats_file = test_dir / "_stats.json"
    with open(stats_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✓ 统计文件已创建: {stats_file}")
    print(f"  版本: {data['version']}")
    print(f"  工具数: {len(data['tool_calls'])}")

    # 清理
    import shutil
    shutil.rmtree(test_dir)
    print(f"\n✓ 测试完成，临时目录已清理")

if __name__ == "__main__":
    test_call_stats()
    print("\n=== 所有测试通过! ===")
