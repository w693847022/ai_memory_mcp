#!/usr/bin/env python3
"""严格验证并发问题的测试."""

import sys
import tempfile
import shutil
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService


def test_race_condition_strict():
    """严格测试：两个线程同时修改同一条目."""
    print("严格测试：验证是否存在 Lost Update 问题")
    print("=" * 70)

    temp_dir = tempfile.mkdtemp()
    try:
        storage = Storage(storage_dir=temp_dir)
        service = ProjectService(storage)

        # 创建测试项目和条目
        result = service.register_project("竞态测试", "/tmp/test", summary="测试")
        project_id = result["project_id"]

        # 先添加一个条目
        add_result = service.add_item(
            project_id, "features",
            content="原始内容",
            summary="原始摘要"
        )
        item_id = add_result["item_id"]

        # 获取初始版本
        project_data = storage.get_project_data(project_id)
        item = next(i for i in project_data["features"] if i["id"] == item_id)
        initial_version = item.get("version", 1)
        print(f"初始版本: {initial_version}")
        print(f"初始摘要: {item['summary']}")
        print()

        # 用于同步的屏障
        barrier = threading.Barrier(2)
        results = []

        def update_thread(thread_name, new_summary, new_content):
            """线程更新函数."""
            try:
                # 等待两个线程都准备好
                barrier.wait()

                # 同时执行更新
                result = service.update_item(
                    project_id, "features", item_id,
                    summary=new_summary,
                    content=new_content,
                    expected_version=initial_version
                )
                results.append((thread_name, result))
            except Exception as e:
                results.append((thread_name, {"exception": str(e)}))

        # 启动两个线程
        t1 = threading.Thread(target=update_thread, args=("线程A", "修改A", "内容A"))
        t2 = threading.Thread(target=update_thread, args=("线程B", "修改B", "内容B"))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # 分析结果
        print("\n结果分析:")
        print("-" * 70)

        success_count = 0
        conflict_count = 0

        for name, result in results:
            if result.get("success"):
                success_count += 1
                print(f"  {name}: ✅ 成功")
                print(f"       返回 version: {result.get('version')}")
            elif result.get("error") == "version_conflict":
                conflict_count += 1
                print(f"  {name}: ❌ 版本冲突")
                print(f"       当前版本: {result.get('current_version')}")
            else:
                print(f"  {name}: ❓ 其他错误: {result.get('error')}")

        # 验证最终状态
        print("\n最终状态验证:")
        print("-" * 70)

        # 清空缓存后重新加载
        storage._project_data_cache.clear()
        final_data = storage.get_project_data(project_id)
        if final_data and "features" in final_data:
            final_item = next((i for i in final_data["features"] if i["id"] == item_id), None)
            if final_item is None:
                print("  ❌ 找不到条目")
                return False
        else:
            print("  ❌ 找不到项目数据")
            return False

        print(f"  最终 summary: {final_item['summary']}")
        print(f"  最终 content: {final_item.get('content', '(N/A)')}")
        print(f"  最终 version: {final_item.get('version')}")

        # 检测问题
        print("\n问题检测:")
        print("-" * 70)

        if success_count == 2:
            print("  ⚠️  两个线程都成功了！")
            print("  ❌ 这是问题：应该只有一个成功，或应该有版本冲突")
            print("  ❌ 可能存在 Lost Update 问题")

            # 检查是否丢失了更新
            if final_item['summary'] not in ["修改A", "修改B"]:
                print(f"  ❌ 数据异常: summary 既不是 '修改A' 也不是 '修改B'")
            elif final_item['summary'] == "修改B":
                print("  ❌ 可能丢失了 '修改A' (线程A的更新)")

            return False

        elif success_count == 1 and conflict_count == 1:
            print("  ✅ 正确：一个成功，一个冲突")
            print("  ✅ 版本控制机制工作正常")
            return True

        else:
            print(f"  ❓ 意外结果: 成功={success_count}, 冲突={conflict_count}")
            return False

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_race_condition_strict()
