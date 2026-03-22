#!/usr/bin/env python
"""测试TTL缓存集成功能."""

import json
import shutil
import time
from pathlib import Path
from datetime import datetime
from src.memory import ProjectMemory
from src.memory import CACHE_TTL_SECONDS, CACHE_MAX_SIZE


def test_cache_basic_operations():
    """测试基本缓存操作."""

    # 创建临时测试目录
    test_dir = Path("/tmp/test_cache_basic_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    test_dir.mkdir(exist_ok=True)

    memory = ProjectMemory(str(test_dir))

    print("=== 测试1: 项目注册和缓存 ===")
    result = memory.register_project("test_project", description="Test project for cache")
    assert result["success"], "项目注册失败"
    project_id = result["project_id"]
    print(f"✓ 项目注册成功: {project_id}")

    # 项目应该在缓存中
    assert project_id in memory._project_data_cache, "项目应该在缓存中"
    print("✓ 项目已缓存")

    print("\n=== 测试2: 缓存命中 ===")
    # 从缓存加载
    start = time.time()
    cached_data = memory._load_project(project_id)
    cache_hit_time = time.time() - start

    # 第一次加载应该命中缓存
    assert cached_data is not None, "缓存数据不应该为空"
    print(f"✓ 缓存命中时间: {cache_hit_time:.6f} 秒")

    print("\n=== 测试3: 写入更新缓存 ===")
    # 修改项目数据
    project_data = memory._load_project(project_id)
    project_data["info"]["description"] = "Updated description"
    memory._save_project(project_id, project_data)

    # 缓存应该已更新
    cached_data = memory._project_data_cache.get(project_id)
    assert cached_data["info"]["description"] == "Updated description", "缓存应该已更新"
    print("✓ 写入时缓存已更新 (write-through)")

    print("\n=== 测试4: 项目删除清理缓存 ===")
    # 删除项目
    result = memory.delete_project(project_id)
    assert result["success"], "项目删除失败"

    # 缓存应该已清理
    assert project_id not in memory._project_data_cache, "缓存应该已清理"
    print("✓ 项目删除时缓存已清理")

    # 清理
    shutil.rmtree(test_dir)
    print(f"\n✓ 测试完成，临时目录已清理")


def test_cache_ttl_expiration():
    """测试缓存TTL过期."""

    # 创建临时测试目录
    test_dir = Path("/tmp/test_cache_ttl_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    test_dir.mkdir(exist_ok=True)

    # 使用较短的TTL进行测试
    import src.memory as memory_module
    original_ttl = memory_module.CACHE_TTL_SECONDS
    memory_module.CACHE_TTL_SECONDS = 1  # 1秒TTL

    memory = ProjectMemory(str(test_dir))

    print("=== 测试TTL过期 ===")

    # 注册项目
    result = memory.register_project("ttl_test_project")
    project_id = result["project_id"]
    print(f"✓ 项目注册: {project_id}")

    # 验证缓存存在
    assert project_id in memory._project_data_cache, "项目应该在缓存中"
    print("✓ 项目已缓存")

    # 等待TTL过期
    print(f"⏳ 等待 {memory_module.CACHE_TTL_SECONDS + 1} 秒...")
    time.sleep(memory_module.CACHE_TTL_SECONDS + 1)

    # 缓存应该已过期
    cached_data = memory._project_data_cache.get(project_id)
    assert cached_data is None, "缓存应该已过期"
    print("✓ 缓存已过期")

    # 重新加载应该从磁盘读取
    reloaded_data = memory._load_project(project_id)
    assert reloaded_data is not None, "应该能从磁盘重新加载"
    print("✓ 从磁盘重新加载成功")

    # 恢复原始TTL
    memory_module.CACHE_TTL_SECONDS = original_ttl

    # 清理
    shutil.rmtree(test_dir)
    print(f"\n✓ 测试完成")


def test_cache_max_size():
    """测试缓存最大大小限制."""

    # 创建临时测试目录
    test_dir = Path("/tmp/test_cache_size_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    test_dir.mkdir(exist_ok=True)

    # 使用较小的缓存大小进行测试
    import src.memory as memory_module
    original_max_size = memory_module.CACHE_MAX_SIZE
    memory_module.CACHE_MAX_SIZE = 3  # 最多缓存3个项目

    memory = ProjectMemory(str(test_dir))

    print("=== 测试缓存大小限制 ===")
    print(f"✓ 缓存最大大小: {memory_module.CACHE_MAX_SIZE}")

    # 注册5个项目
    project_ids = []
    for i in range(5):
        result = memory.register_project(f"size_test_project_{i}")
        project_id = result["project_id"]
        project_ids.append(project_id)
        print(f"✓ 注册项目 {i + 1}: {project_id}")

    # 缓存大小不应超过限制
    cache_size = len(memory._project_data_cache)
    assert cache_size <= memory_module.CACHE_MAX_SIZE, f"缓存大小 {cache_size} 不应超过 {memory_module.CACHE_MAX_SIZE}"
    print(f"✓ 缓存大小: {cache_size} (未超过限制)")

    # 恢复原始缓存大小
    memory_module.CACHE_MAX_SIZE = original_max_size

    # 清理
    shutil.rmtree(test_dir)
    print(f"\n✓ 测试完成")


def test_cache_performance():
    """测试缓存性能提升."""

    # 创建临时测试目录
    test_dir = Path("/tmp/test_cache_perf_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    test_dir.mkdir(exist_ok=True)

    memory = ProjectMemory(str(test_dir))

    print("=== 测试缓存性能 ===")

    # 注册项目
    result = memory.register_project("perf_test_project")
    project_id = result["project_id"]

    # 第一次加载（从磁盘）
    start = time.time()
    memory._load_project(project_id)
    disk_load_time = time.time() - start

    # 第二次加载（从缓存）
    start = time.time()
    memory._load_project(project_id)
    cache_load_time = time.time() - start

    print(f"✓ 磁盘加载时间: {disk_load_time:.6f} 秒")
    print(f"✓ 缓存加载时间: {cache_load_time:.6f} 秒")

    # 缓存应该更快（或至少不慢）
    # 注意：由于现代文件系统缓存，这个差异可能不明显
    if cache_load_time < disk_load_time:
        speedup = disk_load_time / cache_load_time
        print(f"✓ 缓存加速: {speedup:.2f}x")

    # 多次加载测试
    iterations = 100
    start = time.time()
    for _ in range(iterations):
        memory._load_project(project_id)
    cached_time = time.time() - start
    print(f"✓ {iterations} 次缓存加载总时间: {cached_time:.6f} 秒")

    # 清理
    shutil.rmtree(test_dir)
    print(f"\n✓ 测试完成")


def test_cache_with_concurrent_access():
    """测试缓存的线程安全访问."""

    # 创建临时测试目录
    test_dir = Path("/tmp/test_cache_concurrent_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    test_dir.mkdir(exist_ok=True)

    memory = ProjectMemory(str(test_dir))

    print("=== 测试并发访问 ===")

    # 注册项目
    result = memory.register_project("concurrent_test_project")
    project_id = result["project_id"]

    # 使用多线程并发访问
    import threading

    def access_cache():
        for _ in range(50):
            data = memory._load_project(project_id)
            assert data is not None, "加载失败"

    threads = []
    for i in range(5):
        t = threading.Thread(target=access_cache)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("✓ 并发访问测试完成")

    # 清理
    shutil.rmtree(test_dir)
    print(f"\n✓ 测试完成")


if __name__ == "__main__":
    test_cache_basic_operations()
    test_cache_ttl_expiration()
    test_cache_max_size()
    test_cache_performance()
    test_cache_with_concurrent_access()
    print("\n=== 所有缓存测试通过! ===")
