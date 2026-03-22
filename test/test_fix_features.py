#!/usr/bin/env python
"""测试Fix分组和Note关联功能."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from memory import ProjectMemory

def test_fix_features():
    """测试Fix功能."""
    print("=" * 60)
    print("测试Fix分组和Note关联功能")
    print("=" * 60)

    # 使用临时存储目录进行测试
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(storage_dir=tmpdir)

        # 1. 注册测试项目
        print("\n1. 注册测试项目...")
        result = memory.register_project(
            name="测试项目",
            path="/tmp/test_project",
            description="测试Fix功能的项目"
        )
        print(f"   ✓ 项目已注册: {result['project_id']}")
        project_id = result['project_id']

        # 2. 添加一些笔记
        print("\n2. 添加测试笔记...")
        # 注册测试标签
        memory.register_tag(project_id, "auth", "认证相关")
        memory.register_tag(project_id, "security", "安全相关")
        memory.register_tag(project_id, "migration", "数据迁移")
        memory.register_tag(project_id, "database", "数据库相关")
        memory.register_tag(project_id, "bugfix", "Bug修复")
        memory.register_tag(project_id, "performance", "性能优化")

        note1 = memory.add_note(
            project_id,
            "这是关于用户认证功能的详细笔记",
            description="用户认证功能",
            tags=["auth", "security"]
        )
        print(f"   ✓ 笔记1已添加: {note1['note_id']}")

        note2 = memory.add_note(
            project_id,
            "这是关于数据迁移功能的详细笔记",
            description="数据迁移功能",
            tags=["migration", "database"]
        )
        print(f"   ✓ 笔记2已添加: {note2['note_id']}")

        # 3. 添加功能（带note_id关联）
        print("\n3. 添加功能记录（带note_id关联）...")
        feature1 = memory.add_feature(
            project_id,
            "实现用户认证功能",
            status="in_progress",
            tags=["auth"],
            note_id=note1['note_id']
        )
        print(f"   ✓ 功能1已添加: {feature1['feature_id']}")
        print(f"   ✓ 关联笔记: {feature1.get('note_id', '无')}")

        # 4. 添加bug修复记录
        print("\n4. 添加Bug修复记录...")
        fix1 = memory.add_fix(
            project_id,
            "修复登录接口认证错误",
            status="completed",
            severity="critical",
            related_feature=feature1['feature_id'],
            note_id=note1['note_id'],
            tags=["bugfix", "auth"]
        )
        print(f"   ✓ 修复记录已添加: {fix1['fix_id']}")
        print(f"   ✓ 严重程度: critical")
        print(f"   ✓ 关联功能: {fix1.get('related_feature', '无')}")
        print(f"   ✓ 关联笔记: {fix1.get('note_id', '无')}")

        fix2 = memory.add_fix(
            project_id,
            "修复数据迁移中的内存泄漏问题",
            status="pending",
            severity="high",
            tags=["bugfix", "performance"]
        )
        print(f"   ✓ 修复记录已添加: {fix2['fix_id']}")

        # 5. 测试列表分组
        print("\n5. 测试列表分组...")
        groups_result = memory.list_groups(project_id)
        print("   ✓ 分组列表:")
        for group in groups_result['groups']:
            print(f"     - {group['name']}: {group['count']} 个条目 ({group['description']})")

        # 6. 测试更新修复记录
        print("\n6. 测试更新修复记录...")
        update_result = memory.update_fix(
            project_id,
            fix2['fix_id'],
            status="in_progress"
        )
        print(f"   ✓ 修复记录状态已更新: {update_result['fix']['status']}")

        # 7. 测试获取项目详情
        print("\n7. 测试获取项目详情...")
        project_result = memory.get_project(project_id)
        if project_result['success']:
            data = project_result['data']
            print(f"   ✓ 功能数量: {len(data['features'])}")
            print(f"   ✓ 笔记数量: {len(data['notes'])}")
            print(f"   ✓ 修复记录数量: {len(data.get('fixes', []))}")

            # 检查note_id关联
            for feature in data['features']:
                if feature.get('note_id'):
                    print(f"   ✓ 功能 {feature['id']} 关联笔记: {feature['note_id']}")

            for fix in data.get('fixes', []):
                if fix.get('note_id'):
                    print(f"   ✓ 修复 {fix['id']} 关联笔记: {fix['note_id']}")
                if fix.get('related_feature'):
                    print(f"   ✓ 修复 {fix['id']} 关联功能: {fix['related_feature']}")

        # 8. 测试标签查询（fixes分组）
        print("\n8. 测试标签查询（fixes分组）...")
        tags_result = memory.list_group_tags(project_id, "fixes")
        if tags_result['success']:
            print(f"   ✓ Fix分组标签数量: {tags_result['total_tags']}")
            for tag_info in tags_result['tags']:
                print(f"     - {tag_info['tag']}: {tag_info['count']} 个条目")

        # 9. 测试按标签查询（fixes分组）
        print("\n9. 测试按标签查询（fixes分组）...")
        query_result = memory.query_by_tag(project_id, "fixes", "bugfix")
        if query_result['success']:
            print(f"   ✓ 标签 'bugfix' 下的修复记录: {query_result['total']} 个")
            for item in query_result['items']:
                print(f"     - {item['id']}: {item['description']}")

        # 10. 测试智能笔记匹配
        print("\n10. 测试智能笔记匹配...")
        project_data = memory._load_project(project_id)
        matched_note_id = memory._find_matching_note(
            project_data,
            "实现用户认证功能"
        )
        if matched_note_id:
            print(f"   ✓ 智能匹配成功: {matched_note_id}")
        else:
            print(f"   ✗ 智能匹配失败")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_fix_features()
