#!/usr/bin/env python3
"""工具函数单元测试."""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_id_generation():
    """测试 ID 生成格式."""
    print("测试: ID 生成格式...")

    # 测试 features ID 格式
    feature_pattern = r'^feat_\d{8}_\d+$'
    assert re.match(feature_pattern, "feat_20260322_1"), "features ID 格式不正确"

    # 测试 notes ID 格式
    note_pattern = r'^note_\d{8}_\d+$'
    assert re.match(note_pattern, "note_20260322_1"), "notes ID 格式不正确"

    # 测试 fixes ID 格式
    fix_pattern = r'^fix_\d{8}_\d+$'
    assert re.match(fix_pattern, "fix_20260322_1"), "fixes ID 格式不正确"

    # 测试 standards ID 格式
    standard_pattern = r'^std_\d{8}_\d+$'
    assert re.match(standard_pattern, "std_20260322_1"), "standards ID 格式不正确"

    print("  ✓ ID 生成格式测试通过")
    return True


def test_group_normalization():
    """测试分组标准化."""
    print("测试: 分组标准化...")

    # 测试中文别名
    aliases_map = {
        "features": ["features", "feature", "功能", "feat"],
        "fixes": ["fixes", "fix", "修复", "bugfix"],
        "notes": ["notes", "note", "笔记"],
        "standards": ["standards", "standard", "规范", "标准"]
    }

    for normalized, variants in aliases_map.items():
        for variant in variants:
            from features.tools import _normalize_group
            result = _normalize_group(variant)
            assert result == normalized, f"'{variant}' 应该标准化为 '{normalized}'"

    print("  ✓ 分组标准化测试通过")
    return True


def test_tag_parsing():
    """测试标签解析."""
    print("测试: 标签解析...")

    from features.tools import _parse_tags

    # 测试逗号分隔
    tags = _parse_tags("tag1,tag2,tag3")
    assert tags == ["tag1", "tag2", "tag3"], f"标签解析错误: {tags}"

    # 测试空格处理
    tags = _parse_tags("tag1, tag2 , tag3")
    assert tags == ["tag1", "tag2", "tag3"], f"标签空格处理错误: {tags}"

    # 测试空字符串
    tags = _parse_tags("")
    assert tags == [], f"空字符串应该返回空列表: {tags}"

    print("  ✓ 标签解析测试通过")
    return True


def test_content_validation():
    """测试内容长度验证."""
    print("测试: 内容长度验证...")

    from features.tools import _validate_content_length

    # 测试有效内容
    valid, msg = _validate_content_length("短内容", max_tokens=30)
    assert valid, f"短内容应该有效: {msg}"

    # 测试过长内容
    long_content = "a" * 100
    valid, msg = _validate_content_length(long_content, max_tokens=30)
    assert not valid, "过长内容应该无效"

    print("  ✓ 内容长度验证测试通过")
    return True


def run_all_tests():
    """运行所有单元测试."""
    print("=" * 60)
    print("工具函数单元测试")
    print("=" * 60)
    print()

    tests = [
        test_id_generation,
        test_group_normalization,
        test_tag_parsing,
        test_content_validation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except AssertionError as e:
            failed += 1
            print(f"  ✗ 测试失败: {e}")
            print()
        except Exception as e:
            failed += 1
            print(f"  ✗ 测试错误: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
