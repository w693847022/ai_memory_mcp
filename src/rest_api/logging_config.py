"""日志配置模块 - 支持滚动删除."""

import logging
import logging.handlers
import os
import sys
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "/app/logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
):
    """配置日志滚动删除.

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志目录
        max_bytes: 单个日志文件最大大小（字节）
        backup_count: 保留的旧日志文件数量
    """
    # 日志格式
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器（始终启用）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)

    # 尝试添加文件处理器（可能因权限失败）
    log_path = Path(log_dir)
    file_handler_added = False

    try:
        log_path.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path / "fastapi.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8',
        )
        file_handler.setFormatter(log_format)
        root_logger.addHandler(file_handler)
        file_handler_added = True
    except (PermissionError, OSError) as e:
        root_logger.warning(f"无法创建文件日志处理器: {e}，仅使用控制台日志")

    # 配置 Uvicorn 日志
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    return log_path if file_handler_added else None


def get_request_id(record: logging.LogRecord) -> str:
    """从日志记录中提取 request_id."""
    if hasattr(record, 'request_id'):
        return f"[{record.request_id}] "
    return ""
