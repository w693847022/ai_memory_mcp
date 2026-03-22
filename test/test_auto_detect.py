#!/usr/bin/env python3
"""测试 project_auto_detect 功能."""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from memory import get_git_info, get_config_file_name, ProjectMemory

def test_git_info():
    """测试 Git 信息读取."""
    print("=== 测试 get_git_info() ===")
    current_path = os.getcwd()

    git_info = get_git_info(current_path)

    print(f"当前路径: {current_path}")
    print(f"是否为 Git 仓库: {git_info['is_git_repo']}")

    if git_info['is_git_repo']:
        print(f"Git Remote: {git_info['git_remote']}")
        print(f"Git Remote URL: {git_info['git_remote_url']}")
        print(f"当前分支: {git_info['branch']}")
        print(f"仓库名: {git_info['repo_name']}")
        print(f"Git Root: {git_info['root_path']}")

    print()

def test_config_file_name():
    """测试配置文件读取."""
    print("=== 测试 get_config_file_name() ===")
    current_path = os.getcwd()

    config_name = get_config_file_name(current_path)

    print(f"当前路径: {current_path}")
    print(f"从配置文件读取的项目名称: {config_name}")
    print()

def test_find_project_by_git_remote():
    """测试通过 Git remote 查找项目."""
    print("=== 测试 find_project_by_git_remote() ===")

    memory = ProjectMemory()
    current_path = os.getcwd()
    git_info = get_git_info(current_path)

    if git_info['is_git_repo'] and git_info['git_remote']:
        print(f"Git Remote: {git_info['git_remote']}")

        project_id = memory.find_project_by_git_remote(git_info['git_remote'])
        if project_id:
            print(f"✓ 找到已注册项目: {project_id}")
        else:
            print(f"✗ 未找到已注册项目")
    else:
        print("当前路径不是 Git 仓库")

    print()

def test_register_with_git_info():
    """测试使用 Git 信息注册项目."""
    print("=== 测试使用 Git 信息注册项目 ===")

    memory = ProjectMemory()
    current_path = os.getcwd()
    git_info = get_git_info(current_path)

    # 检查是否已注册
    if git_info['is_git_repo'] and git_info['git_remote']:
        existing_project = memory.find_project_by_git_remote(git_info['git_remote'])
        if existing_project:
            print(f"项目已注册: {existing_project}")
            return

    # 测试注册（使用测试名称）
    test_name = "test_auto_detect_project"
    result = memory.register_project(
        name=test_name,
        path=current_path,
        git_remote=git_info.get('git_remote', ''),
        git_remote_url=git_info.get('git_remote_url', ''),
        description="自动检测测试项目",
        tags=["test", "auto-detect"]
    )

    if result['success']:
        print(f"✓ 项目注册成功")
        print(f"  项目ID: {result['project_id']}")
        print(f"  项目名称: {test_name}")
        print(f"  Git Remote: {git_info.get('git_remote', '无')}")

        # 验证数据已保存
        project_data = memory.get_project(result['project_id'])
        if project_data['success']:
            info = project_data['data']['info']
            print(f"  验证 - git_remote 字段: {info.get('git_remote', '无')}")
            print(f"  验证 - git_remote_url 字段: {info.get('git_remote_url', '无')}")
    else:
        print(f"✗ 项目注册失败: {result.get('error')}")

    print()

if __name__ == "__main__":
    print("开始测试项目自动检测功能\n")

    test_git_info()
    test_config_file_name()
    test_find_project_by_git_remote()
    test_register_with_git_info()

    print("测试完成！")
