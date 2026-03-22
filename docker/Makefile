.PHONY: help start stop restart status logs build shell clean

# 默认目标
help:
	@echo "MCP Memory Server Docker 管理命令"
	@echo ""
	@echo "使用方法: make [命令]"
	@echo ""
	@echo "可用命令:"
	@echo "  make start    - 启动服务"
	@echo "  make stop     - 停止服务"
	@echo "  make restart  - 重启服务"
	@echo "  make status   - 查看服务状态"
	@echo "  make logs     - 查看服务日志"
	@echo "  make build    - 重新构建镜像"
	@echo "  make shell    - 进入容器 shell"
	@echo "  make clean    - 清理容器和镜像"
	@echo ""

# 启动服务
start:
	@echo "🚀 启动 MCP Memory Server..."
	@cd docker && docker-compose up -d
	@sleep 2
	@cd docker && docker-compose ps

# 停止服务
stop:
	@echo "🛑 停止 MCP Memory Server..."
	@cd docker && docker-compose down

# 重启服务
restart:
	@echo "🔄 重启 MCP Memory Server..."
	@cd docker && docker-compose restart
	@sleep 2
	@cd docker && docker-compose ps

# 查看状态
status:
	@echo "📊 服务状态:"
	@echo ""
	@cd docker && docker-compose ps

# 查看日志
logs:
	@cd docker && docker-compose logs -f --tail=100

# 重新构建
build:
	@echo "🔨 重新构建镜像..."
	@cd docker && docker-compose build --no-cache
	@echo "✅ 构建完成"

# 进入容器
shell:
	@echo "🐚 进入容器 shell..."
	@cd docker && docker-compose exec mcp-memory-server /bin/bash

# 清理
clean:
	@echo "🧹 清理容器和镜像..."
	@cd docker && docker-compose down -v --rmi all
	@echo "✅ 清理完成"
