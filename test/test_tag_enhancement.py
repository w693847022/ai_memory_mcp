#!/usr/bin/env python
"""测试标签增强功能."""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from memory import ProjectMemory


def test_tag_registration():
    """测试标签注册功能."""
    print("=" * 60)
    print("测试 1: 标签注册功能")
    print("=" * 60)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # 注册项目
        result = memory.register_project(
            name="test_project",
            description="测试项目"
        )
        print(f"✓ 项目注册: {result['success']}")
        project_id = result["project_id"]

        # 测试标签注册
        result = memory.register_tag(
            project_id=project_id,
            tag_name="auth",
            description="用户认证与授权相关功能"
        )
        print(f"✓ 注册标签 'auth': {result['success']}")
        if result.get("success"):
            print(f"  描述: {result['tag_info']['description']}")
            print(f"  使用计数: {result['tag_info']['usage_count']}")

        # 测试标签名称验证
        result = memory.register_tag(
            project_id=project_id,
            tag_name="invalid tag name!",
            description="无效的标签名称，包含空格和特殊字符"
        )
        print(f"✓ 拒绝无效标签名: {not result['success']}")

        # 测试描述长度验证
        result = memory.register_tag(
            project_id=project_id,
            tag_name="test",
            description="太短的描述"
        )
        print(f"✓ 拒绝太短描述: {not result['success']}")

    finally:
        shutil.rmtree(temp_dir)


def test_mandatory_registration():
    """测试强制注册检查."""
    print("\n" + "=" * 60)
    print("测试 2: 强制注册检查")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # 注册项目
        result = memory.register_project(name="test_project2")
        project_id = result["project_id"]

        # 注册标签
        result = memory.register_tag(
            project_id=project_id,
            tag_name="urgent",
            description="高优先级紧急任务，需要立即处理"
        )
        print(f"✓ 注册标签 'urgent': {result['success']}")

        # 尝试使用未注册的标签
        result = memory.add_feature(
            project_id=project_id,
            feature="测试功能",
            tags=["unregistered_tag"]
        )
        print(f"✓ 拒绝未注册标签: {not result['success']}")
        if not result.get("success"):
            print(f"  错误: {result['error']}")

        # 使用已注册的标签
        result = memory.add_feature(
            project_id=project_id,
            feature="紧急功能",
            tags=["urgent"]
        )
        print(f"✓ 接受已注册标签: {result['success']}")

        # 检查使用计数
        project_data = memory._load_project(project_id)
        usage_count = project_data["tag_registry"]["urgent"]["usage_count"]
        print(f"✓ 使用计数更新: {usage_count == 1} (实际: {usage_count})")

    finally:
        shutil.rmtree(temp_dir)


def test_query_enhancement():
    """测试查询增强."""
    print("\n" + "=" * 60)
    print("测试 3: 查询增强")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # 注册项目
        result = memory.register_project(name="test_project3")
        project_id = result["project_id"]

        # 注册标签
        memory.register_tag(
            project_id=project_id,
            tag_name="frontend",
            description="前端相关功能"
        )
        memory.register_tag(
            project_id=project_id,
            tag_name="backend",
            description="后端相关功能"
        )

        # 添加功能
        memory.add_feature(
            project_id=project_id,
            feature="前端页面",
            tags=["frontend"]
        )
        memory.add_feature(
            project_id=project_id,
            feature="API接口",
            tags=["backend"]
        )

        # 测试 list_group_tags
        result = memory.list_group_tags(project_id, "features")
        print(f"✓ list_group_tags: {result['success']}")
        if result.get("success"):
            for tag_info in result["tags"]:
                print(f"  - {tag_info['tag']}: {tag_info['description']} (使用次数: {tag_info['count']})")

        # 测试 query_by_tag
        result = memory.query_by_tag(project_id, "features", "frontend")
        print(f"✓ query_by_tag: {result['success']}")
        if result.get("success") and result.get("tag_info"):
            print(f"  标签信息: {result['tag_info']['description']}")
            print(f"  匹配条目数: {result['total']}")

    finally:
        shutil.rmtree(temp_dir)


def test_tag_management():
    """测试标签管理功能."""
    print("\n" + "=" * 60)
    print("测试 4: 标签管理")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # 注册项目
        result = memory.register_project(name="test_project4")
        project_id = result["project_id"]

        # 注册标签
        memory.register_tag(
            project_id=project_id,
            tag_name="old_tag",
            description="旧标签，将被合并到新标签中"
        )
        memory.register_tag(
            project_id=project_id,
            tag_name="new_tag",
            description="新标签，将接收旧标签的引用"
        )

        # 添加使用旧标签的功能
        memory.add_feature(
            project_id=project_id,
            feature="测试功能",
            tags=["old_tag"]
        )

        # 测试标签更新
        result = memory.update_tag(
            project_id=project_id,
            tag_name="old_tag",
            description="更新后的标签描述，长度超过十个字"
        )
        print(f"✓ 标签更新: {result['success']}")

        # 测试标签合并
        result = memory.merge_tags(
            project_id=project_id,
            old_tag="old_tag",
            new_tag="new_tag"
        )
        print(f"✓ 标签合并: {result['success']}")
        if result.get("success"):
            print(f"  迁移条目数: {result['migrated_count']}")

        # 测试标签删除
        result = memory.delete_tag(
            project_id=project_id,
            tag_name="new_tag",
            force=True
        )
        print(f"✓ 标签删除: {result['success']}")

    finally:
        shutil.rmtree(temp_dir)


def test_backward_compatibility():
    """测试向后兼容性."""
    print("\n" + "=" * 60)
    print("测试 5: 向后兼容性")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # 创建旧格式的项目文件（没有 tag_registry）
        project_id = "test_old_project"
        old_project_data = {
            "id": project_id,
            "info": {
                "name": "Old Project",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "tags": []
            },
            "features": [],
            "notes": []
        }

        # 保存旧格式项目
        import json
        from datetime import datetime
        project_path = memory._get_project_path(project_id)
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(old_project_data, f, ensure_ascii=False, indent=2)

        # 加载项目应该自动添加 tag_registry 和 fixes
        project_data = memory._load_project(project_id)
        print(f"✓ 自动添加 tag_registry: {'tag_registry' in project_data}")
        print(f"✓ 自动添加 fixes: {'fixes' in project_data}")

    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_tag_registration()
    test_mandatory_registration()
    test_query_enhancement()
    test_tag_management()
    test_backward_compatibility()

    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)
