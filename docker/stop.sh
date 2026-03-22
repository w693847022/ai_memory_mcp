#!/bin/bash
# Docker 停止脚本 - MCP Memory Server

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=== 停止 MCP Memory Server ==="
echo ""

cd "$SCRIPT_DIR"

# 停止服务
echo "🛑 停止 Docker 容器..."
docker-compose down

echo ""
echo "✅ MCP Memory Server 已停止"
