#!/usr/bin/env python
"""项目本地记忆 MCP 服务器 - 主启动脚本."""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    from server import parse_args, server

    # 解析参数
    args = parse_args()

    # 运行服务器
    print(f"启动 MCP 服务器...")
    print(f"传输模式: {args.transport}")
    if args.transport != "stdio":
        print(f"监听地址: {args.host}:{args.port}")
    print()

    server.run(transport=args.transport)
