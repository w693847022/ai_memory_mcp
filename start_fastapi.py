#!/usr/bin/env python
"""FastAPI REST API 服务启动脚本.

独立启动 FastAPI REST API 服务（端口 8001）。
"""

import sys
import os
from pathlib import Path

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("FASTAPI_PORT", 8001))
    host = os.environ.get("FASTAPI_HOST", "0.0.0.0")

    print(f"启动 FastAPI REST API 服务...")
    print(f"监听地址: {host}:{port}")
    print(f"健康检查: http://{host}:{port}/health")
    print()

    # 设置 PYTHONPATH 以便 uvicorn 能正确导入模块
    os.environ["PYTHONPATH"] = str(src_path)

    uvicorn.run(
        "rest_api.main:app",
        host=host,
        port=port,
        reload=False
    )
