#!/usr/bin/env python
"""端到端测试 - 验证所有改进的完整工作流程."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from memory import ProjectMemory
import tempfile
import shutil
from datetime import datetime

def test_full_workflow():
    """测试完整工作流程"""
    print("🧪 端到端测试：完整工作流程\n")

    # 创建临时存储目录
    temp_dir = tempfile.mkdtemp()
    try:
        memory = ProjectMemory(storage_dir=temp_dir)

        # ==================== 测试1: 项目注册 ====================
        print("=" * 60)
        print("测试1: 项目注册")
        print("=" * 60)

        result = memory.register_project(
            "test_project",
            "/tmp/test_project",
            description="测试项目",
            tags=["testing", "demo"]
        )
        assert result["success"], f"项目注册失败: {result}"
        project_id = result['project_id']
        print(f"✓ 项目已注册: {project_id}")

        # 注册测试标签
        print("注册测试标签...")
        memory.register_tag(project_id, "auth", "认证相关")
        memory.register_tag(project_id, "security", "安全相关")
        memory.register_tag(project_id, "validation", "数据验证")
        memory.register_tag(project_id, "data", "数据相关")
        memory.register_tag(project_id, "api", "API相关")
        memory.register_tag(project_id, "backend", "后端相关")
        memory.register_tag(project_id, "jwt", "JWT认证")
        memory.register_tag(project_id, "implementation", "实施记录")
        memory.register_tag(project_id, "technical", "技术笔记")
        memory.register_tag(project_id, "completed", "已完成")
        print("✓ 测试标签已注册")

        # ==================== 测试2: 添加功能（改进1：ID生成） ====================
        print("\n" + "=" * 60)
        print("测试2: 添加功能（改进1：修复ID生成逻辑）")
        print("=" * 60)

        # 添加多个功能，测试ID唯一性
        feature_ids = []
        features = [
            ("用户认证功能", ["auth", "security"]),
            ("数据验证功能", ["validation", "data"]),
            ("API接口功能", ["api", "backend"]),
        ]

        for desc, tags in features:
            result = memory.add_feature(project_id, desc, tags=tags)
            assert result["success"], f"添加功能失败: {result}"
            feature_ids.append(result['feature_id'])
            print(f"✓ 功能已添加: {desc} -> {result['feature_id']}")

        # 验证ID唯一性
        assert len(feature_ids) == len(set(feature_ids)), "功能ID存在重复！"
        print(f"✓ 成功生成 {len(feature_ids)} 个唯一功能ID")

        # ==================== 测试3: 添加笔记（改进4：description字段） ====================
        print("\n" + "=" * 60)
        print("测试3: 添加笔记（改进4：description字段）")
        print("=" * 60)

        note_id_1 = memory.add_note(
            project_id,
            note="""## 用户认证实现

使用JWT令牌进行用户认证：
- 登录接口生成access token
- 刷新令牌机制
- 令牌过期处理

技术栈：Python, JWT, Flask""",
            description="用户认证功能实现笔记",
            tags=["implementation", "auth", "jwt"]
        )['note_id']
        print(f"✓ 笔记已添加: {note_id_1}")

        note_id_2 = memory.add_note(
            project_id,
            note="## 数据验证\n\n使用Pydantic进行数据验证。",
            description="数据验证笔记",
            tags=["technical"]
        )['note_id']
        print(f"✓ 笔记已添加: {note_id_2}")

        # 验证笔记数据结构
        project_data = memory.get_project(project_id)
        note_1 = project_data['data']['notes'][0]
        assert note_1['description'] == "用户认证功能实现笔记"
        assert "implementation" in note_1['tags']
        print("✓ 笔记数据结构验证通过")

        # ==================== 测试4: 更新功能状态 ====================
        print("\n" + "=" * 60)
        print("测试4: 更新功能状态")
        print("=" * 60)

        # 将第一个功能标记为完成
        result = memory.update_feature(
            project_id,
            feature_ids[0],
            status="completed"
        )
        assert result["success"], f"更新功能失败: {result}"
        print(f"✓ 功能状态已更新: {feature_ids[0]} -> completed")

        # ==================== 测试5: 添加实施完成笔记（改进3/4） ====================
        print("\n" + "=" * 60)
        print("测试5: 添加实施完成笔记")
        print("=" * 60)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        implementation_note = memory.add_note(
            project_id,
            note=f"""## 实施完成

### 功能描述
用户认证功能

### 实施摘要
完成JWT令牌认证系统，包括登录、刷新令牌和权限验证。

### 修改文件列表
- `src/auth/login.py`: 实现登录逻辑
- `src/auth/jwt.py`: JWT令牌管理
- `src/middleware.py`: 认证中间件
- `tests/test_auth.py`: 测试用例

### 技术要点
- 使用PyJWT库生成和验证令牌
- 实现refresh token机制
- 添加权限装饰器

### 完成时间
{timestamp}""",
            description="实施完成: 用户认证功能",
            tags=["implementation", "completed", "auth", "jwt"]
        )['note_id']
        print(f"✓ 实施笔记已添加: {implementation_note}")

        # ==================== 测试6: 验证数据完整性 ====================
        print("\n" + "=" * 60)
        print("测试6: 验证数据完整性")
        print("=" * 60)

        # 重新加载项目数据
        project_data = memory.get_project(project_id)
        data = project_data['data']

        # 验证功能
        assert len(data['features']) == 3
        assert data['features'][0]['status'] == "completed"
        assert data['features'][1]['status'] == "pending"
        print(f"✓ 功能数据完整（{len(data['features'])} 个功能）")

        # 验证笔记
        assert len(data['notes']) == 3
        assert data['notes'][0]['description'] == "用户认证功能实现笔记"
        assert "implementation" in data['notes'][0]['tags']
        assert data['notes'][2]['description'] == "实施完成: 用户认证功能"
        print(f"✓ 笔记数据完整（{len(data['notes'])} 个笔记）")

        # 验证description字段
        for note in data['notes']:
            assert 'description' in note, f"笔记 {note['id']} 缺少description字段"
        print("✓ 所有笔记都有description字段")

        # ==================== 测试7: 查询和统计 ====================
        print("\n" + "=" * 60)
        print("测试7: 查询和统计")
        print("=" * 60)

        # 按标签查询
        result = memory.query_by_tag(project_id, "features", "auth")
        assert result["success"]
        assert result["total"] == 1
        print(f"✓ 标签查询成功：auth -> {result['total']} 个功能")

        # 获取项目统计
        stats = memory.get_stats()
        assert stats["success"]
        print(f"✓ 统计信息：")
        print(f"  - 总项目数: {stats['stats']['total_projects']}")
        print(f"  - 总功能数: {stats['stats']['total_features']}")
        print(f"  - 总笔记数: {stats['stats']['total_notes']}")
        print(f"  - 功能状态: {stats['stats']['feature_status']}")

        # ==================== 测试总结 ====================
        print("\n" + "=" * 60)
        print("✅ 端到端测试完成！所有改进验证通过")
        print("=" * 60)
        print("\n已验证的改进：")
        print("✓ 改进1: ID生成逻辑（同一天内唯一ID）")
        print("✓ 改进4: Note description字段（数据结构增强）")
        print("✓ 改进2&3: 自动实施记录流程（工具可用性）")
        print("\n所有改进工作正常！🎉")

        return True

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_full_workflow()
