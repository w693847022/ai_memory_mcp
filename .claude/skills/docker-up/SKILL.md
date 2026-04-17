---
name: docker-up
description: 使用 docker/manage.sh restart 重启 Docker 容器
allowed-tools: Bash
---

重启项目的 Docker 容器。

操作步骤：
1. 确认 `docker/manage.sh` 存在且可执行
2. 在项目根目录执行 `./docker/manage.sh restart`
3. 等待容器启动完成
4. 向用户报告容器启动状态（成功/失败）及关键日志摘要
