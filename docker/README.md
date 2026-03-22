# MCP Memory Server - Docker 部署指南

使用 Docker 容器化部署 MCP Memory Server，支持后台运行和自动重启。

## 📁 文件结构

```
docker/
├── Dockerfile              # Docker 镜像构建文件
├── docker-compose.yml      # Docker Compose 配置
├── .env.example            # 环境变量示例
├── start.sh               # 快速启动脚本
├── stop.sh                # 快速停止脚本
├── manage.sh              # 管理脚本
├── Makefile               # Make 命令
└── README.md              # 本文档
```

## 🚀 快速开始

### 1. 配置环境变量

```bash
cd docker
cp .env.example .env
# 编辑 .env 文件根据需要修改配置
```

### 2. 启动服务

**方式一：使用启动脚本（推荐）**
```bash
./start.sh
```

**方式二：使用 Docker Compose**
```bash
docker-compose up -d
```

**方式三：使用 Make**
```bash
make start
```

### 3. 验证服务

```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 测试服务端点
curl http://localhost:8000/
```

## 🛠️ 管理命令

### 使用管理脚本

```bash
./manage.sh start     # 启动服务
./manage.sh stop      # 停止服务
./manage.sh restart   # 重启服务
./manage.sh status    # 查看状态
./manage.sh logs      # 查看日志
./manage.sh build     # 重新构建
./manage.sh shell     # 进入容器
./manage.sh clean     # 清理容器
```

### 使用 Make

```bash
make start    # 启动服务
make stop     # 停止服务
make restart  # 重启服务
make status   # 查看状态
make logs     # 查看日志
make build    # 重新构建
make shell    # 进入容器
make clean    # 清理容器
```

### 使用 Docker Compose

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重启
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重新构建
docker-compose build --no-cache

# 进入容器
docker-compose exec mcp-memory-server /bin/bash
```

## ⚙️ 配置说明

### 环境变量 (.env)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| MCP_TRANSPORT | streamable-http | 传输模式 (stdio/sse/streamable-http) |
| MCP_HOST | 0.0.0.0 | 监听地址 |
| MCP_PORT | 8000 | 监听端口 |
| MCP_LOG_LEVEL | INFO | 日志级别 |

### 端口映射

默认映射: `8000:8000`

修改端口:
```bash
# 在 .env 文件中修改
MCP_PORT=9000
```

### 数据持久化

容器会自动挂载 `~/.project_memory_ai` 到容器内，确保数据持久化。

## 📊 监控和日志

### 查看实时日志
```bash
docker-compose logs -f
```

### 查看最近日志
```bash
docker-compose logs --tail=100
```

### 查看特定服务日志
```bash
docker-compose logs -f mcp-memory-server
```

## 🐛 故障排查

### 1. 端口被占用
```bash
# 检查端口占用
lsof -i :8000

# 修改 .env 中的端口
MCP_PORT=9000
```

### 2. 容器启动失败
```bash
# 查看详细日志
docker-compose logs

# 重新构建镜像
docker-compose build --no-cache
docker-compose up -d
```

### 3. 进入容器调试
```bash
docker-compose exec mcp-memory-server /bin/bash
```

## 🔄 更新服务

```bash
# 停止服务
docker-compose down

# 拉取最新代码（如果在 git 仓库中）
git pull

# 重新构建并启动
docker-compose build --no-cache
docker-compose up -d
```

## 🗑️ 清理

### 停止并删除容器
```bash
docker-compose down
```

### 完全清理（包括镜像）
```bash
docker-compose down -v --rmi all
```

## 🔧 开发模式

开发模式下，源代码目录以只读方式挂载到容器中，修改代码后重启容器即可生效：

```bash
docker-compose restart
```

## 📡 服务端点

启动后，服务可通过以下端点访问：

- **HTTP API**: `http://localhost:8000/`
- **MCP 协议**: `http://localhost:8000/mcp/`
- **SSE**: `http://localhost:8000/sse/`

## 🔐 安全建议

1. **生产环境**：
   - 使用反向代理 (Nginx/Apache)
   - 配置 HTTPS/TLS
   - 限制访问 IP
   - 添加身份认证

2. **防火墙配置**：
   ```bash
   # 仅允许本地访问
   iptables -A INPUT -p tcp --dport 8000 -s 127.0.0.1 -j ACCEPT
   iptables -A INPUT -p tcp --dport 8000 -j DROP
   ```

## 📝 注意事项

- 首次启动会自动构建 Docker 镜像，需要等待几分钟
- 容器会自动重启（除非手动停止）
- 数据存储在宿主机 `~/.project_memory_ai` 目录
- 建议定期备份此目录
