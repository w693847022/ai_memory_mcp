#!/usr/bin/env python3
"""竞态条件测试 - 验证并发问题."""

import sys
import tempfile
import shutil
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService


def test_race_condition_same_version():
    """测试两个线程同时修改同一条目（相同版本）."""
    print("测试：两个线程并发修改同一条目（相同版本）")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    try:
        storage = Storage(storage_dir=temp_dir)
        service = ProjectService(storage)

        # 创建测试项目和条目
        result = service.register_project("竞态测试", "/tmp/test", summary="测试")
        project_id = result["project_id"]

        # 添加初始条目
        add_result = service.add_item(
            project_id, "features",
            content="原始内容",
            summary="原始摘要"
        )
        item_id = add_result["item_id"]

        # 获取当前版本
        project_data = storage.get_project_data(project_id)
        item = next(i for i in project_data["features"] if i["id"] == item_id)
        initial_version = item.get("version", 1)
        print(f"初始版本: {initial_version}")

        # 两个线程的结果
        results = []
        lock = threading.Lock()

        def update_thread(thread_name, new_summary):
            """线程更新函数."""
            result = service.update_item(
                project_id, "features", item_id,
                summary=new_summary,
                expected_version=initial_version  # 两个线程都用相同版本
            )
            with lock:
                results.append((thread_name, result))

        # 启动两个线程
        t1 = threading.Thread(target=update_thread, args=("线程A", "修改A"))
        t2 = threading.Thread(target=update_thread, args=("线程B", "修改B"))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # 检查结果
        print("\n结果:")
        for name, result in results:
            if result.get("success"):
                print(f"  {name}: ✅ 成功, version={result.get('version')}")
            else:
                print(f"  {name}: ❌ 失败, error={result.get('error')}")

        # 验证最终状态
        final_data = storage.get_project_data(project_id)
        final_item = next(i for i in final_data["features"] if i["id"] == item_id)

        print(f"\n最终状态:")
        print(f"  summary: {final_item['summary']}")
        print(f"  version: {final_item.get('version')}")

        # 检测是否有问题
        success_count = sum(1 for _, r in results if r.get("success"))
        if success_count == 2:
            print("\n⚠️  检测到竞态条件：两个线程都成功了！")
            print("   这是一个问题：应该有一个线程失败或等待")
            return False
        elif success_count == 1:
            print("\n✅ 正确：只有一个线程成功")
            return True
        else:
            print("\n❌ 意外情况")
            return False

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_race_condition_same_version()
