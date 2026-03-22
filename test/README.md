# 项目测试套件

## 测试结构

```
test/
├── unit/               # 单元测试
│   ├── test_memory.py      # ProjectMemory 类测试
│   ├── test_callstats.py   # CallStats 类测试
│   └── test_utils.py       # 工具函数测试
├── integration/        # 集成测试
│   ├── test_api.py         # MCP 工具接口集成测试
│   └── test_storage.py     # 存储层集成测试
├── e2e/                # 端到端测试
│   ├── test_workflow.py    # 完整工作流测试
│   └── test_resources.py   # MCP 资源测试
├── run_all.py          # 批量运行所有测试
└── README.md           # 本文件
```

## 运行测试

### 运行所有测试

```bash
python test/run_all.py
```

### 运行单个测试文件

```bash
# 单元测试
python test/unit/test_memory.py
python test/unit/test_callstats.py
python test/unit/test_utils.py

# 集成测试
python test/integration/test_api.py
python test/integration/test_storage.py

# 端到端测试
python test/e2e/test_workflow.py
python test/e2e/test_resources.py
```

## 测试说明

### 单元测试 (unit/)

- **test_memory.py**: 测试 ProjectMemory 类的核心方法
  - 项目注册、重命名、删除
  - 各分组条目的增删改查
  - ID 生成和验证

- **test_callstats.py**: 测试 CallStats 类
  - 接口调用统计
  - 日统计记录
  - 项目/工具统计查询

- **test_utils.py**: 测试工具函数
  - 分组标准化
  - 标签解析
  - 内容长度验证

### 集成测试 (integration/)

- **test_api.py**: MCP 工具接口集成测试
  - 项目列表接口
  - 按标签查询
  - 标签操作集成
  - 分组列表接口

- **test_storage.py**: 存储层集成测试
  - JSON 持久化
  - 笔记内容分离存储
  - 目录结构验证
  - 并发访问安全性

### 端到端测试 (e2e/)

- **test_workflow.py**: 完整工作流测试
  - 注册→添加→查询→更新→删除
  - 多项目管理
  - 端到端场景验证

- **test_resources.py**: MCP 资源测试
  - 中文指南资源
  - 英文指南资源
  - 指南结构完整性

## 测试特点

1. **使用临时目录**: 所有测试使用 `tempfile.mkdtemp()` 创建临时存储，测试完成后自动清理
2. **独立隔离**: 每个测试函数独立运行，互不影响
3. **直接运行**: 使用 `python test_xxx.py` 直接运行，无需 pytest
4. **清晰输出**: 测试结果有清晰的通过/失败标识
