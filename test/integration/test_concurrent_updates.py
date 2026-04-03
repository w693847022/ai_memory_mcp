#!/usr/bin/env python3
"""并发更新测试.

测试多线程并发更新场景：
1. 多线程同时更新同一项目的不同条目（应该都成功）
2. 多线程同时更新同一条目（第一个成功，其他返回冲突）
3. 并发读取和写入（读写分离正确）
"""

import sys
import os
import tempfile
import shutil
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.storage import Storage
from business.project_service import ProjectService
from business.tag_service import TagService


class TestConcurrentUpdates:
    """并发更新测试类."""

    def setup_method(self):
        """每个测试方法前执行：设置测试环境."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(storage_dir=self.temp_dir)
        self.project_service = ProjectService(self.storage)
        self.tag_service = TagService(self.storage)

        # 注册测试项目
        result = self.project_service.register_project(
            "并发测试项目",
            "/tmp/concurrent_test",
            summary="用于并发测试的项目"
        )
        self.project_id = result["project_id"]

        # 注册标签
        self.tag_service.register_tag(
            self.project_id,
            "concurrent",
            "并发测试标签"
        )

    def teardown_method(self):
        """每个测试方法后执行：清理测试环境."""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_concurrent_update_different_items(self):
        """测试1: 多线程同时更新同一项目的不同条目（应该都成功）."""
        # 创建多个不同条目
        num_items = 5
        item_ids = []

        for i in range(num_items):
            result = self.project_service.add_item(
                project_id=self.project_id,
                group="features",
                content=f"初始内容 {i}",
                summary=f"初始摘要 {i}",
                status="pending",
                tags=["concurrent"]
            )
            item_ids.append(result["item_id"])

        # 用于存储线程执行结果
        update_results = []
        update_lock = threading.Lock()

        def update_item_worker(item_index: int, item_id: str):
            """工作线程：更新指定条目."""
            try:
                # 添加随机延迟，增加并发竞争
                time.sleep(0.01 * item_index)

                result = self.project_service.update_item(
                    project_id=self.project_id,
                    group="features",
                    item_id=item_id,
                    content=f"线程更新内容 {item_index}",
                    summary=f"线程更新摘要 {item_index}",
                    status="in_progress"
                )

                with update_lock:
                    update_results.append({
                        "item_index": item_index,
                        "item_id": item_id,
                        "success": result.get("success", False),
                        "version": result.get("version", 0)
                    })

            except Exception as e:
                with update_lock:
                    update_results.append({
                        "item_index": item_index,
                        "item_id": item_id,
                        "success": False,
                        "error": str(e)
                    })

        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=num_items) as executor:
            futures = []
            for i, item_id in enumerate(item_ids):
                future = executor.submit(update_item_worker, i, item_id)
                futures.append(future)

            # 等待所有线程完成
            for future in as_completed(futures):
                pass

        # 验证结果
        all_success = True
        for result in update_results:
            if not result["success"]:
                all_success = False

        # 验证最终状态
        project_data = self.project_service.get_project(self.project_id)
        features = project_data["data"]["features"]

        for i, item_id in enumerate(item_ids):
            # 查找对应的条目
            item = next((f for f in features if f["id"] == item_id), None)
            if item:
                expected_summary = f"线程更新摘要 {i}"
                if item["summary"] != expected_summary:
                    all_success = False
            else:
                all_success = False

        # 断言测试结果
        assert all_success, f"部分条目更新失败"
        assert len(update_results) == num_items, f"期望 {num_items} 个更新结果，实际 {len(update_results)} 个"

    def test_concurrent_update_same_item_conflict(self):
        """测试2: 多线程同时更新同一条目（第一个成功，其他返回冲突）."""
        # 创建一个测试条目
        result = self.project_service.add_item(
            project_id=self.project_id,
            group="features",
            content="初始内容",
            summary="初始摘要",
            status="pending",
            tags=["concurrent"]
        )
        item_id = result["item_id"]

        # 获取条目的当前版本
        project_data = self.project_service.get_project(self.project_id)
        item = next((f for f in project_data["data"]["features"] if f["id"] == item_id), None)
        current_version = item.get("version", 1) if item else 1

        # 用于存储线程执行结果
        update_results = []
        update_lock = threading.Lock()

        def update_same_item_worker(thread_index: int):
            """工作线程：尝试更新同一条目."""
            try:
                # 所有线程都使用相同的期望版本（模拟并发冲突）
                expected_version = current_version

                # 添加随机延迟，模拟真实并发场景
                time.sleep(0.001 * thread_index)

                result = self.project_service.update_item(
                    project_id=self.project_id,
                    group="features",
                    item_id=item_id,
                    content=f"线程 {thread_index} 更新内容",
                    summary=f"线程 {thread_index} 更新摘要",
                    expected_version=expected_version  # 使用乐观锁
                )

                with update_lock:
                    update_results.append({
                        "thread_index": thread_index,
                        "success": result.get("success", False),
                        "error": result.get("error", ""),
                        "version": result.get("version", 0),
                        "expected_version": expected_version
                    })

            except Exception as e:
                with update_lock:
                    update_results.append({
                        "thread_index": thread_index,
                        "success": False,
                        "error": str(e),
                        "version": 0,
                        "expected_version": current_version
                    })

        # 使用线程池并发执行
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for i in range(num_threads):
                future = executor.submit(update_same_item_worker, i)
                futures.append(future)

            # 等待所有线程完成
            for future in as_completed(futures):
                pass

        # 分析结果
        success_count = sum(1 for r in update_results if r["success"])
        conflict_count = sum(1 for r in update_results if r["error"] == "version_conflict")
        error_count = sum(1 for r in update_results if not r["success"] and r["error"] != "version_conflict")

        # 验证最终状态
        project_data = self.project_service.get_project(self.project_id)
        item = next((f for f in project_data["data"]["features"] if f["id"] == item_id), None)

        if item:
            final_version = item.get("version", 1)

            # 验证：应该只有一个线程成功，其他都遇到版本冲突
            assert success_count == 1, f"期望 1 个成功，实际 {success_count} 个"
            assert conflict_count == num_threads - 1, f"期望 {num_threads - 1} 个冲突，实际 {conflict_count} 个"
            assert error_count == 0, f"期望 0 个错误，实际 {error_count} 个"
            assert final_version == current_version + 1, f"期望版本 {current_version + 1}，实际 {final_version}"
        else:
            assert False, "条目未找到"

    def test_concurrent_read_write(self):
        """测试3: 并发读取和写入（读写分离正确）."""
        # 创建测试条目
        num_items = 3
        item_ids = []

        for i in range(num_items):
            result = self.project_service.add_item(
                project_id=self.project_id,
                group="features",
                content=f"读写测试内容 {i}",
                summary=f"读写测试 {i}",
                status="pending",
                tags=["concurrent"]
            )
            item_ids.append(result["item_id"])

        # 用于存储操作结果
        operation_results = []
        operation_lock = threading.Lock()

        def read_worker(worker_index: int):
            """读操作工作线程."""
            try:
                time.sleep(0.01 * worker_index)  # 添加延迟

                project_data = self.project_service.get_project(self.project_id)
                features = project_data["data"]["features"]

                with operation_lock:
                    operation_results.append({
                        "worker_index": worker_index,
                        "operation": "read",
                        "success": True,
                        "item_count": len(features)
                    })

            except Exception as e:
                with operation_lock:
                    operation_results.append({
                        "worker_index": worker_index,
                        "operation": "read",
                        "success": False,
                        "error": str(e)
                    })

        def write_worker(worker_index: int, item_id: str):
            """写操作工作线程."""
            try:
                time.sleep(0.01 * worker_index)  # 添加延迟

                result = self.project_service.update_item(
                    project_id=self.project_id,
                    group="features",
                    item_id=item_id,
                    content=f"写线程 {worker_index} 更新",
                    summary=f"写线程 {worker_index}",
                    status="completed"
                )

                with operation_lock:
                    operation_results.append({
                        "worker_index": worker_index,
                        "operation": "write",
                        "success": result.get("success", False),
                        "item_id": item_id
                    })

            except Exception as e:
                with operation_lock:
                    operation_results.append({
                        "worker_index": worker_index,
                        "operation": "write",
                        "success": False,
                        "error": str(e)
                    })

        # 使用线程池并发执行读写操作
        num_readers = 5
        num_writers = 3

        with ThreadPoolExecutor(max_workers=num_readers + num_writers) as executor:
            futures = []

            # 启动读线程
            for i in range(num_readers):
                future = executor.submit(read_worker, i)
                futures.append(future)

            # 启动写线程
            for i in range(num_writers):
                item_id = item_ids[i % num_items]
                future = executor.submit(write_worker, i, item_id)
                futures.append(future)

            # 等待所有线程完成
            for future in as_completed(futures):
                pass

        # 分析结果
        read_results = [r for r in operation_results if r["operation"] == "read"]
        write_results = [r for r in operation_results if r["operation"] == "write"]

        successful_reads = len([r for r in read_results if r["success"]])
        successful_writes = len([r for r in write_results if r["success"]])

        # 验证所有操作都成功（读写不应该互相阻塞）
        assert successful_reads == num_readers, f"读操作失败 ({successful_reads}/{num_readers})"
        assert successful_writes == num_writers, f"写操作失败 ({successful_writes}/{num_writers})"
