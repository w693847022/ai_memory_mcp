#!/usr/bin/env python3
"""版本控制单元测试."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from unittest.mock import Mock, MagicMock, patch
from business.project_service import ProjectService
from datetime import datetime


class TestVersionControl:
    """测试版本控制功能."""

    def setup_method(self):
        """设置测试环境."""
        self.mock_storage = Mock()
        self.mock_storage.generate_timestamps.return_value = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.service = ProjectService(self.mock_storage)

    def test_update_item_with_version_conflict(self):
        """测试版本冲突检测."""
        # 准备测试数据
        project_id = "test_project"
        group = "features"
        item_id = "feat_001"

        # 创建一个版本为2的条目
        item_data = {
            "id": item_id,
            "summary": "Test feature",
            "content": "Test content",
            "version": 2,
            "tags": ["test"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Mock update_item_with_version_check 返回版本冲突
        self.mock_storage.update_item_with_version_check.return_value = {
            "success": False,
            "error": "version_conflict",
            "message": "版本冲突",
            "current_version": 2,
            "expected_version": 1
        }

        # 尝试用错误的版本号更新（期望版本是1，但实际是2）
        result = self.service.update_item(
            project_id=project_id,
            group=group,
            item_id=item_id,
            summary="Updated summary",
            expected_version=1  # 错误的版本号
        )

        # 验证版本冲突被检测到
        assert result["success"] is False
        assert result["error"] == "version_conflict"
        assert result["current_version"] == 2
        assert result["expected_version"] == 1
        assert "版本冲突" in result["message"]

    def test_update_item_with_correct_version(self):
        """测试正确版本号的更新."""
        project_id = "test_project"
        group = "features"
        item_id = "feat_001"

        # 创建一个版本为2的条目
        item_data = {
            "id": item_id,
            "summary": "Test feature",
            "content": "Test content",
            "version": 2,
            "tags": ["test"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Mock update_item_with_version_check 返回成功
        updated_item = item_data.copy()
        updated_item["summary"] = "Updated summary"
        updated_item["version"] = 3

        self.mock_storage.update_item_with_version_check.return_value = {
            "success": True,
            "version": 3,
            "item": updated_item,
            "old_item": item_data.copy()
        }

        self.mock_storage.get_project_data.return_value = {
            "info": {
                "name": "Test Project",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "tags": []
            },
            "features": [updated_item],
            "tag_registry": {}
        }
        self.mock_storage.save_project_data.return_value = True
        self.mock_storage.update_timestamp = Mock()

        # 用正确的版本号更新
        result = self.service.update_item(
            project_id=project_id,
            group=group,
            item_id=item_id,
            summary="Updated summary",
            expected_version=2  # 正确的版本号
        )

        # 验证更新成功且版本递增
        assert result["success"] is True
        assert result["version"] == 3
        assert result["item"]["summary"] == "Updated summary"

    def test_update_item_without_version_check(self):
        """测试不进行版本检查的更新."""
        project_id = "test_project"
        group = "features"
        item_id = "feat_001"

        item_data = {
            "id": item_id,
            "summary": "Test feature",
            "content": "Test content",
            "version": 2,
            "tags": ["test"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Mock update_item_with_version_check 返回成功（不检查版本）
        updated_item = item_data.copy()
        updated_item["summary"] = "Updated summary"
        updated_item["version"] = 3

        self.mock_storage.update_item_with_version_check.return_value = {
            "success": True,
            "version": 3,
            "item": updated_item,
            "old_item": item_data.copy()
        }

        self.mock_storage.get_project_data.return_value = {
            "info": {
                "name": "Test Project",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "tags": []
            },
            "features": [updated_item],
            "tag_registry": {}
        }
        self.mock_storage.save_project_data.return_value = True
        self.mock_storage.update_timestamp = Mock()

        # 不提供版本号，应该直接更新
        result = self.service.update_item(
            project_id=project_id,
            group=group,
            item_id=item_id,
            summary="Updated summary"
        )

        # 验证更新成功且版本递增
        assert result["success"] is True
        assert result["version"] == 3

    def test_update_item_version_initialization(self):
        """测试没有版本字段的条目初始化为版本1."""
        project_id = "test_project"
        group = "features"
        item_id = "feat_001"

        # 创建没有版本字段的条目
        item_data = {
            "id": item_id,
            "summary": "Test feature",
            "content": "Test content",
            "tags": ["test"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Mock update_item_with_version_check 返回成功（版本从1递增到2）
        updated_item = item_data.copy()
        updated_item["summary"] = "Updated summary"
        updated_item["version"] = 2

        self.mock_storage.update_item_with_version_check.return_value = {
            "success": True,
            "version": 2,
            "item": updated_item,
            "old_item": item_data.copy()
        }

        self.mock_storage.get_project_data.return_value = {
            "info": {
                "name": "Test Project",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "tags": []
            },
            "features": [updated_item],
            "tag_registry": {}
        }
        self.mock_storage.save_project_data.return_value = True
        self.mock_storage.update_timestamp = Mock()

        # 更新条目
        result = self.service.update_item(
            project_id=project_id,
            group=group,
            item_id=item_id,
            summary="Updated summary"
        )

        # 验证版本从1初始化并递增到2
        assert result["success"] is True
        assert result["version"] == 2