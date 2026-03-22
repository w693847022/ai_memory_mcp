---
name: rememory-std
description: 回忆项目规范 standard 规范 查询 插入上下文 使用MCP[memory_mcp]查询项目规范
allowed-tools: mcp__memory_mcp__project_list, mcp__memory_mcp__project_get
context: fork
argument-hint: <规范类型，如：代码规范、开发规范、API规范>
---

# rememory-std 技能

回忆项目规范并返回紧凑 JSON 格式。

## ⚠️ 第一步：参数检查

**检查命令参数**：

用户输入：`/rememory-std <参数>`

- 如果 `<参数>` 为空 → 无参数模式
- 如果 `<参数>` 不为空 → 有参数模式

**判断方法**：
- 空输入：`/rememory-std` 或 `/rememory-std `（后面只有空格）
- 有输入：`/rememory-std 代码规范`、`/rememory-std docs`

## 📋 执行流程

### 步骤 1：确定项目

获取项目列表，通过 Git remote 或目录名确定当前项目 ID。

### 步骤 2：获取所有规范

调用 `project_get(project_id="<项目ID>", group_name="standards")` 查询所有规范。

### 步骤 3：根据参数决定返回内容

#### 无参数模式
返回所有规范，按主标签分组。

#### 有参数模式 - 语义过滤

**参数到标签映射表**：

| 用户输入 | 返回标签 | 说明 |
|---------|----------|------|
| 代码规范 | code-style, api, naming | 代码风格、API、命名相关 |
| 开发规范 | code-style, structure, testing | 代码、结构、测试 |
| 文档规范 | docs | 文档相关 |
| API规范 | api | API 相关 |
| Git规范 | git | Git 相关 |
| 运维规范 | ops, docker | 运维、Docker |
| 命名规范 | naming, code-style | 命名相关 |
| docs | docs | 直接标签名 |
| git | git | 直接标签名 |
| code-style | code-style | 直接标签名 |

**过滤规则**：
1. 根据用户输入查找匹配的标签
2. 只返回这些标签的规范
3. 使用 `matched_tags` 字段显示匹配到的标签

## 📤 输出格式

### 无参数输出

```json
{
  "project_id": "mcp_test",
  "standards": {
    "code-style": ["规范内容1", "规范内容2"],
    "structure": ["规范内容3"]
  }
}
```

### 有参数输出

```json
{
  "project_id": "mcp_test",
  "input": "代码规范",
  "matched_tags": ["code-style", "api", "naming"],
  "standards": {
    "code-style": ["规范内容"],
    "api": ["规范内容"],
    "naming": ["规范内容"]
  }
}
```

## ✅ 检查清单

执行前确认：
- [ ] 已检查用户是否输入了参数
- [ ] 无参数 → 返回所有规范
- [ ] 有参数 → 按映射表过滤，只返回匹配标签
- [ ] 输出格式正确
