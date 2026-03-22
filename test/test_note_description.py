#!/usr/bin/env python
"""测试Note description字段 - 验证新字段和向后兼容性."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from memory import ProjectMemory
import tempfile
import shutil
import json

def test_note_with_description():
    """测试带description的笔记"""
    print("🧪 测试Note description字段...")

    # 创建临时存储目录
    temp_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # 注册测试项目
        result = memory.register_project("test_note_desc", "/tmp/test")
        assert result["success"], f"项目注册失败: {result}"
        project_id = result['project_id']
        print(f"✓ 项目已注册: {project_id}")

        # 测试1: 添加带description的笔记
        print("\n测试1: 添加带description的笔记")
        result = memory.add_note(
            project_id,
            note="这是详细的笔记内容，包含技术细节和实现说明。",
            description="简短描述"
        )
        assert result['success'], f"添加笔记失败: {result}"
        note_id = result['note_id']
        print(f"✓ 笔记已添加: {note_id}")

        # 验证数据结构
        project_data = memory.get_project(project_id)
        note = project_data['data']['notes'][0]
        assert note['description'] == "简短描述", f"description字段不正确: {note.get('description')}"
        assert note['content'] == "这是详细的笔记内容，包含技术细节和实现说明。"
        print("✓ 笔记数据结构验证通过")

        # 测试2: 更新description
        print("\n测试2: 更新笔记description")
        result = memory.update_note(
            project_id,
            note_id,
            description="更新的简短描述"
        )
        assert result['success'], f"更新笔记失败: {result}"
        print(f"✓ 笔记description已更新")

        # 验证更新
        project_data = memory.get_project(project_id)
        note = project_data['data']['notes'][0]
        assert note['description'] == "更新的简短描述"
        assert note['content'] == "这是详细的笔记内容，包含技术细节和实现说明。"
        print("✓ 更新验证通过")

        # 测试3: 向后兼容 - 模拟旧数据
        print("\n测试3: 向后兼容性测试")
        project_path = memory._get_project_path(project_id)

        # 读取并修改数据，移除description字段
        with open(project_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 移除description字段模拟旧数据
        for note in data['notes']:
            if 'description' in note:
                del note['description']

        # 保存修改后的数据
        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("✓ 已模拟旧数据（移除description字段）")

        # 清除缓存以模拟重新加载
        memory._project_data_cache.pop(project_id, None)

        # 重新加载项目，验证向后兼容
        project_data = memory._load_project(project_id)
        note = project_data['notes'][0]

        # 验证description字段自动补充
        assert 'description' in note, "向后兼容失败：缺少description字段"
        assert note['description'] == "", f"向后兼容失败：description应为空字符串，实际为: {note['description']}"
        print("✓ 向后兼容性验证通过（自动补充空description）")

        # 测试4: 添加不带description的笔记
        print("\n测试4: 添加不带description的笔记")
        result = memory.add_note(
            project_id,
            note="另一条笔记"
        )
        assert result['success'], f"添加笔记失败: {result}"
        note_id_2 = result['note_id']
        print(f"✓ 笔记已添加: {note_id_2}")

        # 验证description为空字符串
        project_data = memory.get_project(project_id)
        note = project_data['data']['notes'][1]
        assert note['description'] == ""
        print("✓ 空description验证通过")

        print("\n✅ 所有测试通过!")
        return True

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_note_with_description()
