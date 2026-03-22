#!/usr/bin/env python
"""测试统一 MCP 工具接口."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from memory import ProjectMemory
from server import (
    project_add, project_update, project_delete,
    _normalize_group, _parse_tags
)


def test_helper_functions():
    """测试辅助函数."""
    print("=" * 60)
    print("测试辅助函数")
    print("=" * 60)

    print("\n1. 测试 _normalize_group 函数...")
    test_cases = [
        ("features", "features"),
        ("feature", "features"),
        ("功能", "features"),
        ("FEAT", "features"),
        ("fixes", "fixes"),
        ("fix", "fixes"),
        ("修复", "fixes"),
        ("bugfix", "fixes"),
        ("notes", "notes"),
        ("note", "notes"),
        ("笔记", "notes"),
    ]
    for input_val, expected in test_cases:
        result = _normalize_group(input_val)
        status = "✓" if result == expected else "✗"
        print(f"   {status} _normalize_group('{input_val}') = '{result}' (expected: '{expected}')")
        assert result == expected, f"Expected '{expected}', got '{result}'"

    print("\n2. 测试 _parse_tags 函数...")
    test_cases = [
        ("tag1,tag2,tag3", ["tag1", "tag2", "tag3"]),
        ("", []),
        ("single", ["single"]),
        ("tag1, tag2 , tag3", ["tag1", "tag2", "tag3"]),
    ]
    for input_val, expected in test_cases:
        result = _parse_tags(input_val)
        status = "✓" if result == expected else "✗"
        print(f"   {status} _parse_tags('{input_val}') = {result} (expected: {expected})")
        assert result == expected, f"Expected {expected}, got {result}"

    print("\n✓ 所有辅助函数测试通过!")


def test_project_add():
    """测试 project_add 统一接口."""
    print("\n" + "=" * 60)
    print("测试 project_add 统一接口")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(storage_dir=tmpdir)
        import server
        server.memory = memory

        # 注册测试项目
        result = memory.register_project("test_unified", "/tmp/test")
        project_id = result['project_id']
        print(f"\n项目ID: {project_id}")

        # 1. 测试添加功能 (features)
        print("\n1. 测试添加功能 (features)...")
        output = project_add(project_id, "features", "实现登录功能", status="pending")
        print(f"   {output}")
        assert "✓" in output
        assert "feat_" in output

        # 2. 测试中文 group 别名
        print("\n2. 测试中文 group 别名 (功能)...")
        output = project_add(project_id, "功能", "实现注册功能", status="pending")
        print(f"   {output}")
        assert "✓" in output

        # 3. 测试添加修复 (fixes)
        print("\n3. 测试添加修复 (fixes)...")
        output = project_add(project_id, "fixes", "修复登录bug", status="pending", severity="high")
        print(f"   {output}")
        assert "✓" in output
        assert "fix_" in output

        # 4. 测试中文 group 别名 (修复)
        print("\n4. 测试中文 group 别名 (修复)...")
        output = project_add(project_id, "修复", "修复注册bug", status="pending", severity="critical")
        print(f"   {output}")
        assert "✓" in output

        # 5. 测试添加笔记 (notes)
        print("\n5. 测试添加笔记 (notes)...")
        output = project_add(project_id, "notes", "这是调试笔记", description="登录问题")
        print(f"   {output}")
        assert "✓" in output
        assert "note_" in output

        # 6. 测试中文 group 别名 (笔记)
        print("\n6. 测试中文 group 别名 (笔记)...")
        output = project_add(project_id, "笔记", "这是中文笔记", description="中文描述")
        print(f"   {output}")
        assert "✓" in output

        print("\n✓ 所有 project_add 测试通过!")


def test_project_update():
    """测试 project_update 统一接口."""
    print("\n" + "=" * 60)
    print("测试 project_update 统一接口")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(storage_dir=tmpdir)
        import server
        server.memory = memory

        # 注册测试项目
        result = memory.register_project("test_unified", "/tmp/test")
        project_id = result['project_id']

        # 1. 测试更新功能
        print("\n1. 测试更新功能...")
        add_output = project_add(project_id, "features", "功能1", status="pending")
        feature_id = add_output.split("\n")[1].split(": ")[1]
        print(f"   添加功能: {feature_id}")

        update_output = project_update(project_id, "features", feature_id, status="completed")
        print(f"   {update_output}")
        assert "✓" in update_output
        assert "completed" in update_output

        # 2. 测试更新修复
        print("\n2. 测试更新修复...")
        add_output = project_add(project_id, "fixes", "修复1", status="pending", severity="high")
        fix_id = add_output.split("\n")[1].split(": ")[1]
        print(f"   添加修复: {fix_id}")

        update_output = project_update(project_id, "fixes", fix_id, severity="medium", status="in_progress")
        print(f"   {update_output}")
        assert "✓" in update_output
        assert "medium" in update_output
        assert "in_progress" in update_output

        # 3. 测试更新笔记
        print("\n3. 测试更新笔记...")
        add_output = project_add(project_id, "notes", "笔记1", description="描述1")
        # Note format: "笔记ID: note_XXX 描述: XXX"
        note_line = add_output.split("\n")[1]
        note_id = note_line.split(": ")[1].split(" ")[0]  # Extract just the ID part
        print(f"   添加笔记: {note_id}")

        update_output = project_update(project_id, "notes", note_id, description="描述2")
        print(f"   {update_output}")
        assert "✓" in update_output
        assert "描述2" in update_output

        print("\n✓ 所有 project_update 测试通过!")


def test_project_delete():
    """测试 project_delete 统一接口."""
    print("\n" + "=" * 60)
    print("测试 project_delete 统一接口")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(storage_dir=tmpdir)
        import server
        server.memory = memory

        # 注册测试项目
        result = memory.register_project("test_unified", "/tmp/test")
        project_id = result['project_id']

        # 1. 测试删除功能
        print("\n1. 测试删除功能...")
        add_output = project_add(project_id, "features", "待删除功能", status="pending")
        feature_id = add_output.split("\n")[1].split(": ")[1]
        print(f"   添加功能: {feature_id}")

        delete_output = project_delete(project_id, "features", feature_id)
        print(f"   {delete_output}")
        assert "✓" in delete_output

        # 2. 测试删除修复
        print("\n2. 测试删除修复...")
        add_output = project_add(project_id, "fixes", "待删除修复", status="pending")
        fix_id = add_output.split("\n")[1].split(": ")[1]
        print(f"   添加修复: {fix_id}")

        delete_output = project_delete(project_id, "fixes", fix_id)
        print(f"   {delete_output}")
        assert "✓" in delete_output

        # 3. 测试删除笔记
        print("\n3. 测试删除笔记...")
        add_output = project_add(project_id, "notes", "待删除笔记")
        # Note format: "笔记ID: note_XXX 描述: XXX" or just "笔记ID: note_XXX"
        note_line = add_output.split("\n")[1]
        note_id = note_line.split(": ")[1].split(" ")[0]  # Extract just the ID part
        print(f"   添加笔记: {note_id}")

        delete_output = project_delete(project_id, "notes", note_id)
        print(f"   {delete_output}")
        assert "✓" in delete_output

        print("\n✓ 所有 project_delete 测试通过!")


def test_invalid_group():
    """测试无效的 group 参数."""
    print("\n" + "=" * 60)
    print("测试无效的 group 参数")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(storage_dir=tmpdir)
        import server
        server.memory = memory

        # 注册测试项目
        result = memory.register_project("test_unified", "/tmp/test")
        project_id = result['project_id']

        print("\n1. 测试无效的 group...")
        output = project_add(project_id, "invalid_group", "test")
        print(f"   {output}")
        assert "✗" in output
        assert "无效的分组类型" in output

        print("\n2. 测试空的 content...")
        output = project_add(project_id, "features", "", status="pending", description="test", tags="test")
        print(f"   {output}")
        assert "✗" in output
        assert "content 参数不能为空" in output

        print("\n3. 测试 project_update 缺少 item_id...")
        output = project_update(project_id, "features", "")
        print(f"   {output}")
        assert "✗" in output
        assert "item_id 参数不能为空" in output

        print("\n✓ 所有错误处理测试通过!")


if __name__ == "__main__":
    import tempfile

    print("\n" + "=" * 60)
    print("统一 MCP 工具接口测试")
    print("=" * 60)

    try:
        test_helper_functions()
        test_project_add()
        test_project_update()
        test_project_delete()
        test_invalid_group()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
