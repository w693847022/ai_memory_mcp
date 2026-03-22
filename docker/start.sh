#!/bin/bash
# Docker 启动脚本 - MCP Memory Server

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$SCRIPT_DIR"

echo "=== MCP Memory Server Docker 启动 ==="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 进入 docker 目录
cd "$DOCKER_DIR"

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 配置文件..."
    cp .env.example .env
    echo "✅ .env 文件已创建，请根据需要修改配置"
fi

# 停止旧容器（如果存在）
echo "🛑 停止旧容器..."
docker-compose down 2>/dev/null || true

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "🚀 启动 MCP 服务器..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 显示状态
echo ""
echo "=== 服务状态 ==="
docker-compose ps

echo ""
echo "=== 服务日志 ==="
docker-compose logs --tail=20

echo ""
echo "✅ MCP Memory Server 已启动！"
echo ""
echo "📊 监控命令："
echo "  查看日志: docker-compose -f docker/docker-compose.yml logs -f"
echo "  查看状态: docker-compose -f docker/docker-compose.yml ps"
echo "  停止服务: docker-compose -f docker/docker-compose.yml down"
echo "  重启服务: docker-compose -f docker/docker-compose.yml restart"
echo ""
echo "🌐 服务地址:"
echo "  HTTP: http://localhost:8000"
echo "  MCP: http://localhost:8000/mcp/"
echo ""
