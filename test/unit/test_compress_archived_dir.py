#!/usr/bin/env python3
"""_compress_archived_dir 方法单元测试 - fix_20260417_1.

测试重命名时旧目录压缩归档逻辑。
"""

import tarfile
from pathlib import Path

from src.business.core.storage_base import ProjectStorage


class TestCompressArchivedDir:
    """_compress_archived_dir 方法测试."""

    def test_compress_success(self, tmp_path):
        """正常压缩：目录存在，压缩为 tar.gz 并删除原目录."""
        storage = ProjectStorage(storage_dir=tmp_path)

        # 创建一个待归档的目录
        archived_dir = tmp_path / "old_project"
        archived_dir.mkdir()
        (archived_dir / "test.txt").write_text("hello")

        result = storage._compress_archived_dir(str(archived_dir))

        assert result["success"] is True
        assert "compressed_path" in result
        assert result["compressed_path"].endswith(".tar.gz")
        assert "old_project" in result["compressed_path"]

        # 原目录应已删除
        assert not archived_dir.exists()

        # 压缩文件应存在
        compressed = Path(result["compressed_path"])
        assert compressed.exists()

        # 验证压缩内容
        with tarfile.open(str(compressed), "r:gz") as tar:
            names = tar.getnames()
            assert "old_project/test.txt" in names

    def test_compress_empty_path(self, tmp_path):
        """空路径返回错误."""
        storage = ProjectStorage(storage_dir=tmp_path)

        result = storage._compress_archived_dir("")
        assert result["success"] is False
        assert "归档路径为空" in result["error"]

    def test_compress_none_path(self, tmp_path):
        """None 路径返回错误."""
        storage = ProjectStorage(storage_dir=tmp_path)

        result = storage._compress_archived_dir(None)
        assert result["success"] is False

    def test_compress_nonexistent_path(self, tmp_path):
        """不存在的路径返回错误."""
        storage = ProjectStorage(storage_dir=tmp_path)

        result = storage._compress_archived_dir(str(tmp_path / "nonexistent"))
        assert result["success"] is False
        assert "归档目录不存在" in result["error"]

    def test_compress_file_not_dir(self, tmp_path):
        """传入文件路径（非目录）返回错误."""
        storage = ProjectStorage(storage_dir=tmp_path)

        file_path = tmp_path / "a_file.txt"
        file_path.write_text("not a dir")

        result = storage._compress_archived_dir(str(file_path))
        assert result["success"] is False
        assert "归档目录不存在" in result["error"]

    def test_compress_filename_format(self, tmp_path):
        """验证压缩文件名格式为 {timestamp}_{dirname}.tar.gz."""
        storage = ProjectStorage(storage_dir=tmp_path)

        archived_dir = tmp_path / "my_project"
        archived_dir.mkdir()
        (archived_dir / "data.json").write_text("{}")

        result = storage._compress_archived_dir(str(archived_dir))

        assert result["success"] is True
        compressed = Path(result["compressed_path"])
        name = compressed.name
        # 格式: YYYYMMDD_HHMMSS_my_project.tar.gz (由 _safe_migrate_project_dir 命名)
        assert name == "my_project.tar.gz"
