# MCP Memory Server Tests

本目录包含项目本地记忆 MCP 服务器的所有测试脚本。

## 测试文件列表

### 单元测试

- `test_guidelines.py` - 测试使用建议接口功能（中英文支持、JSON结构）
- `test_id_generation.py` - 测试ID生成功能
- `test_note_description.py` - 测试笔记描述功能

### 功能测试

- `test_fix_features.py` - 测试Fix分组和Note关联功能
- `test_transport_modes.py` - 测试不同传输模式（stdio/sse/streamable-http）

### 集成测试

- `test_e2e.py` - 端到端测试
- `test_http.py` - HTTP接口测试
- `test_stats.py` - 统计功能测试
- `test_simple.py` - 简单启动测试

## 运行测试

### 运行所有测试

```bash
# 从项目根目录运行
python -m pytest test/ -v

# 或逐个运行
python test/test_guidelines.py
python test/test_fix_features.py
python test/test_e2e.py
```

### 运行特定测试

```bash
# 单元测试
python test/test_guidelines.py
python test/test_id_generation.py

# 功能测试
python test/test_fix_features.py

# 集成测试
python test/test_simple.py
```

## 测试覆盖范围

- ✅ 使用建议接口（guidelines://usage）
- ✅ 项目注册与管理
- ✅ 功能记录与状态跟踪
- ✅ Bug修复记录与追踪
- ✅ 开发笔记记录
- ✅ 笔记关联功能
- ✅ 标签系统
- ✅ ID生成
- ✅ 传输模式
- ✅ 统计功能

## 注意事项

- 所有测试已更新导入路径，支持从 test/ 目录运行
- 测试使用临时存储目录，不会影响实际数据
- 某些测试需要网络连接（如 Web 搜索测试）
