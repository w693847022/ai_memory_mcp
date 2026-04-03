#!/usr/bin/env python3
"""简单的 CAS 测试."""

import sys
sys.path.insert(0, 'src')

from business.storage import Storage
from business.project_service import ProjectService
import tempfile
import shutil

# 创建测试环境
temp_dir = tempfile.mkdtemp()
try:
    storage = Storage(storage_dir=temp_dir)
    service = ProjectService(storage)

    print("创建项目...")
    result = service.register_project("测试", "/tmp/test", summary="测试")
    project_id = result["project_id"]
    print(f"项目ID: {project_id}")

    print("添加条目...")
    add_result = service.add_item(project_id, "features", content="内容", summary="原始摘要")
    item_id = add_result["item_id"]
    version = add_result.get("version", 1)
    print(f"条目ID: {item_id}, 版本: {version}")

    print("更新条目...")
    update_result = service.update_item(
        project_id, "features", item_id,
        summary="新摘要",
        expected_version=version
    )
    print(f"更新结果: {update_result.get('success')}")
    print(f"新版本: {update_result.get('version')}")

    print("✅ 测试完成")

finally:
    shutil.rmtree(temp_dir, ignore_errors=True)
