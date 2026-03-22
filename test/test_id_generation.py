#!/usr/bin/env python
"""测试ID生成逻辑 - 验证同一天内生成的ID唯一性."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from memory import ProjectMemory
import tempfile
import shutil
import json

def test_unique_ids():
    """测试同一天内生成唯一ID"""
    print("🧪 测试ID生成唯一性...")

    # 创建临时存储目录
    temp_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # 注册测试项目
        result = memory.register_project("test_id_gen", "/tmp/test")
        assert result["success"], f"项目注册失败: {result}"
        project_id = result['project_id']
        print(f"✓ 项目已注册: {project_id}")

        # 添加多个功能
        feature_ids = []
        for i in range(5):
            result = memory.add_feature(project_id, f"功能{i}")
            assert result["success"], f"添加功能{i}失败: {result}"
            feature_ids.append(result['feature_id'])
            print(f"✓ 添加功能{i}: {result['feature_id']}")

        # 验证ID唯一性
        assert len(feature_ids) == len(set(feature_ids)), f"ID存在重复！{feature_ids}"
        print(f"✓ 成功生成 {len(feature_ids)} 个唯一ID")

        # 验证ID格式
        for fid in feature_ids:
            assert fid.startswith("feat_"), f"ID格式错误: {fid}"
            assert len(fid.split("_")) == 3, f"ID格式错误: {fid}"
        print("✓ ID格式验证通过")

        # 测试笔记ID
        note_ids = []
        for i in range(3):
            result = memory.add_note(project_id, f"笔记{i}")
            assert result["success"], f"添加笔记{i}失败: {result}"
            note_ids.append(result['note_id'])
            print(f"✓ 添加笔记{i}: {result['note_id']}")

        # 验证笔记ID唯一性
        assert len(note_ids) == len(set(note_ids)), f"笔记ID存在重复！{note_ids}"
        print(f"✓ 成功生成 {len(note_ids)} 个唯一笔记ID")

        # 验证功能ID和笔记ID不会冲突
        all_ids = feature_ids + note_ids
        assert len(all_ids) == len(set(all_ids)), "功能ID和笔记ID存在冲突！"
        print("✓ 功能ID和笔记ID无冲突")

        print("\n✅ 基础测试通过!")
        return True

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_gap_in_sequence():
    """测试ID序号不连续时仍能生成唯一ID"""
    print("\n🧪 测试ID序号不连续场景...")

    temp_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # 注册测试项目
        result = memory.register_project("test_gap", "/tmp/test")
        project_id = result['project_id']

        # 手动创建一个有间隙的项目数据
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")

        # 直接操作存储文件，模拟已有不连续ID的情况
        project_data = memory._load_project(project_id)
        project_data["features"] = [
            {"id": f"feat_{date_str}_1", "description": "功能1", "status": "pending", "tags": [], "created_at": datetime.now().isoformat()},
            {"id": f"feat_{date_str}_5", "description": "功能5", "status": "pending", "tags": [], "created_at": datetime.now().isoformat()},
            {"id": f"feat_{date_str}_10", "description": "功能10", "status": "pending", "tags": [], "created_at": datetime.now().isoformat()},
        ]
        memory._save_project(project_id, project_data)
        print(f"✓ 模拟已有ID: feat_{date_str}_1, feat_{date_str}_5, feat_{date_str}_10")

        # 添加新功能，应该生成 feat_YYYYMMDD_11（最大序号+1）
        result = memory.add_feature(project_id, "新功能")
        new_id = result['feature_id']
        print(f"✓ 新生成的ID: {new_id}")

        # 验证ID是最大序号+1
        expected_id = f"feat_{date_str}_11"
        assert new_id == expected_id, f"期望 {expected_id}，实际 {new_id}"
        print(f"✓ 正确生成最大序号+1: {new_id}")

        # 再添加一个，应该是 12
        result = memory.add_feature(project_id, "另一个新功能")
        new_id2 = result['feature_id']
        assert new_id2 == f"feat_{date_str}_12", f"期望 feat_{date_str}_12，实际 {new_id2}"
        print(f"✓ 连续添加正确: {new_id2}")

        print("\n✅ 间隙测试通过!")
        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_large_number_of_items():
    """测试大量条目时ID生成（不使用固定3位数格式）"""
    print("\n🧪 测试大量条目ID生成...")

    temp_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        result = memory.register_project("test_large", "/tmp/test")
        project_id = result['project_id']

        # 模拟已有100+条目
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")

        project_data = memory._load_project(project_id)
        for i in range(1, 150):
            project_data["features"].append({
                "id": f"feat_{date_str}_{i}",
                "description": f"功能{i}",
                "status": "pending",
                "tags": [],
                "created_at": datetime.now().isoformat()
            })
        memory._save_project(project_id, project_data)
        print(f"✓ 模拟已有149个功能条目")

        # 添加新功能，应该是150
        result = memory.add_feature(project_id, "第150个功能")
        new_id = result['feature_id']
        print(f"✓ 新生成的ID: {new_id}")

        # 验证ID不是固定3位数格式（150 vs 150）
        assert new_id == f"feat_{date_str}_150", f"期望 feat_{date_str}_150，实际 {new_id}"
        # 确保格式不包含前导零
        assert "_150" in new_id, "ID格式应不包含前导零"
        print(f"✓ 正确处理3位数以上序号: {new_id}")

        print("\n✅ 大量条目测试通过!")
        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_unique_ids()
    test_gap_in_sequence()
    test_large_number_of_items()
    print("\n🎉 所有测试通过!")
