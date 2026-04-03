#!/usr/bin/env python3
"""简化的并发问题测试."""

import sys
import tempfile
import shutil
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService


def test_concurrent_same_version():
    """测试：两个线程同时修改同一条目（相同版本）."""
    print("测试：两个线程并发修改同一条目（相同版本）")
    print("=" * 70)

    temp_dir = tempfile.mkdtemp()
    try:
        storage = Storage(storage_dir=temp_dir)
        service = ProjectService(storage)

        # 创建项目和条目
        result = service.register_project("测试项目", "/tmp/test", summary="测试")
        project_id = result["project_id"]

        add_result = service.add_item(
            project_id, "features",
            content="原始内容",
            summary="原始摘要"
        )
        item_id = add_result["item_id"]
        initial_version = add_result.get("version", 1)

        print(f"条目ID: {item_id}")
        print(f"初始版本: {initial_version}")
        print()

        # 结果收集
        results = []
        lock = threading.Lock()

        def update_thread(thread_name, new_summary):
            result = service.update_item(
                project_id, "features", item_id,
                summary=new_summary,
                expected_version=initial_version
            )
            with lock:
                results.append((thread_name, result))

        # 使用屏障确保真正并发
        barrier = threading.Barrier(2)

        def update_with_barrier(thread_name, new_summary):
            barrier.wait()  # 同步点
            update_thread(thread_name, new_summary)

        # 启动线程
        t1 = threading.Thread(target=update_with_barrier, args=("线程A", "修改A"))
        t2 = threading.Thread(target=update_with_barrier, args=("线程B", "修改B"))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # 分析结果
        print("结果:")
        print("-" * 70)
        for name, result in results:
            success = result.get("success", False)
            error = result.get("error")
            version = result.get("version")

            if success:
                print(f"  {name}: ✅ 成功 (version: {version})")
            elif error == "version_conflict":
                print(f"  {name}: ❌ 版本冲突 (当前版本: {result.get('current_version')})")
            else:
                print(f"  {name}: ❓ 错误: {error}")

        # 判断
        success_count = sum(1 for _, r in results if r.get("success"))
        conflict_count = sum(1 for _, r in results if r.get("error") == "version_conflict")

        print("\n分析:")
        print("-" * 70)
        print(f"成功数: {success_count}")
        print(f"冲突数: {conflict_count}")

        if success_count == 2:
            print("\n⚠️  两个线程都成功了！")
            print("❌ 存在 Lost Update 问题：两个线程都通过版本检查并成功保存")
            print("   后执行的线程会覆盖先执行线程的修改")
            return False
        elif success_count == 1 and conflict_count == 1:
            print("\n✅ 正确：一个成功，一个冲突")
            print("   版本控制机制工作正常")
            return True
        else:
            print(f"\n❓ 意外结果")
            return False

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_concurrent_same_version()
