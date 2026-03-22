#!/bin/bash
# Docker 管理脚本 - MCP Memory Server

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 显示使用说明
show_usage() {
    echo "MCP Memory Server Docker 管理脚本"
    echo ""
    echo "用法: ./manage.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看服务状态"
    echo "  logs      查看服务日志"
    echo "  build     重新构建镜像"
    echo "  shell     进入容器 shell"
    echo "  clean     清理容器和镜像"
    echo "  help      显示此帮助信息"
    echo ""
}

# 启动服务
start_service() {
    cd "$SCRIPT_DIR"
    echo "🚀 启动 MCP Memory Server..."
    docker-compose up -d
    sleep 2
    docker-compose ps
}

# 停止服务
stop_service() {
    cd "$SCRIPT_DIR"
    echo "🛑 停止 MCP Memory Server..."
    docker-compose down
}

# 重启服务
restart_service() {
    cd "$SCRIPT_DIR"
    echo "🔄 重启 MCP Memory Server..."
    docker-compose restart
    sleep 2
    docker-compose ps
}

# 查看状态
show_status() {
    cd "$SCRIPT_DIR"
    echo "📊 服务状态:"
    echo ""
    docker-compose ps
    echo ""
    echo "🌐 端口监听:"
    docker-compose exec mcp-memory-server netstat -tlnp 2>/dev/null || ss -tlnp 2>/dev/null || echo "无法查看端口信息"
}

# 查看日志
show_logs() {
    cd "$SCRIPT_DIR"
    docker-compose logs -f --tail=100
}

# 重新构建
rebuild() {
    cd "$SCRIPT_DIR"
    echo "🔨 重新构建镜像..."
    docker-compose build --no-cache
    echo "✅ 构建完成"
}

# 进入容器
enter_shell() {
    cd "$SCRIPT_DIR"
    echo "🐚 进入容器 shell..."
    docker-compose exec mcp-memory-server /bin/bash
}

# 清理
clean() {
    cd "$SCRIPT_DIR"
    echo "🧹 清理容器和镜像..."
    read -p "确定要清理吗? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        echo "✅ 清理完成"
    else
        echo "❌ 取消清理"
    fi
}

# 主逻辑
case "${1:-}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    build)
        rebuild
        ;;
    shell)
        enter_shell
        ;;
    clean)
        clean
        ;;
    help|--help|-h|"")
        show_usage
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
