#!/usr/bin/env python3
"""批量运行所有测试."""

import sys
import subprocess
from pathlib import Path

# 测试文件列表
TEST_FILES = [
    # 单元测试
    ("unit/test_memory.py", "ProjectMemory 单元测试"),
    ("unit/test_callstats.py", "CallStats 单元测试"),
    ("unit/test_utils.py", "工具函数单元测试"),
    # 集成测试
    ("integration/test_api.py", "API 接口集成测试"),
    ("integration/test_storage.py", "存储层集成测试"),
    # 端到端测试
    ("e2e/test_workflow.py", "端到端工作流测试"),
    ("e2e/test_resources.py", "MCP 资源测试"),
]


def run_test_file(test_path, description):
    """运行单个测试文件."""
    print(f"\n{'=' * 60}")
    print(f"运行: {description}")
    print(f"文件: {test_path}")
    print('=' * 60)

    full_path = Path(__file__).parent / test_path
    result = subprocess.run(
        [sys.executable, str(full_path)],
        capture_output=False,
        text=True
    )

    return result.returncode == 0


def main():
    """主函数."""
    print("=" * 60)
    print("完整功能测试套件")
    print("=" * 60)

    results = []
    total_passed = 0
    total_failed = 0

    for test_path, description in TEST_FILES:
        success = run_test_file(test_path, description)
        results.append((description, success))
        if success:
            total_passed += 1
        else:
            total_failed += 1

    # 输出汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    for description, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status} - {description}")

    print("\n" + "=" * 60)
    print(f"总计: {total_passed} 通过, {total_failed} 失败")
    print("=" * 60)

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
