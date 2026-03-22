---
name: memory-fix
description: 记录 fix 修复 使用MCP[memory_mcp]快速记录 Fix/Bug
allowed-tools: mcp__memory_mcp__project_list, mcp__memory_mcp__project_get, mcp__memory_mcp__project_add, mcp__memory_mcp__project_update, mcp__memory_mcp__project_tags_info
context: fork
argument-hint: <Fix/Bug描述>
---

# memory-fix 技能

快速记录 Fix/Bug 到 Memory MCP，自动检查相关记录并提醒合并/重启。

---

## 执行流程

### 步骤 1: 输入检查

**检查命令参数**：

用户输入：`/memory-fix <描述>`

- 如果 `<描述>` 为空 → 提示用户输入并退出
- 如果 `<描述>` 不为空 → 继续处理

**判断方法**：
- 空输入：`/memory-fix` 或 `/memory-fix `（后面只有空格）
- 有输入：`/memory-fix 登录接口超时`

---

### 步骤 2: 确定项目

调用 `project_list()` 获取所有项目列表，通过以下方式确定当前项目 ID：
1. 优先使用 Git remote URL 匹配
2. 其次使用目录名匹配
3. 如果都无法确定，提示用户选择项目

---

### 步骤 3: 查询相关 Fix

调用 `project_get(project_id, "fixes")` 获取所有 fix 记录。

**相似度判断标准**：
- 关键词重合度 > 50%
- 描述相似度 > 70%

**分析方法**：
1. 提取用户描述中的关键词（中文分词）
2. 与已有 fix 的 description 进行关键词匹配
3. 计算相似度，筛选相关 fix

---

### 步骤 4: 智能提示

#### 无相关 Fix
直接进入步骤 5。

#### 有相关 Fix
展示相关 fix 并询问用户操作：

```
发现相关 Fix:
- <fix_id>: <description> (状态: <status>)

推荐操作：
1. 合并到 <fix_id> - 推荐用于相同问题的补充信息
2. 重启 <fix_id> - 推荐用于问题复现或继续修复
3. 新建记录 - 推荐用于新问题

请选择操作 (1/2/3):
```

**操作说明**：
- **合并**: 更新现有 fix 的 content/note_id，不改变状态
- **重启**: 将状态改为 in_progress
- **新建**: 创建新的 fix 记录

---

### 步骤 5: 确认状态

根据用户描述自动推荐状态：

| 用户描述关键词 | 推荐状态 |
|----------------|----------|
| 已修复、修复了、解决了 | completed |
| 发现、遇到、出现 | pending |
| 正在、正在修复、处理中 | in_progress |

**确认格式**：
```
推荐状态: <recommended_status>
- pending: 待处理
- in_progress: 进行中
- completed: 已完成

请确认状态 (默认: <recommended_status>):
```

---

### 步骤 6: 确认严重程度

默认为 `medium`，可选值：
- `critical`: 系统崩溃、数据丢失、安全漏洞
- `high`: 核心功能不可用、严重性能问题
- `medium`: 功能异常但有替代方案
- `low`: 轻微问题、UI瑕疵

---

### 步骤 7: 记录创建

#### 7.1 检查描述长度

- 如果描述长度 > 30 字符 → 创建 Note
- 如果描述长度 ≤ 30 字符 → 不创建 Note

#### 7.2 创建 Note（如需要）

```python
project_add(
    project_id="<project_id>",
    group="notes",
    content="<完整描述>",
    description="<摘要>",
    tags="fix,implementation"
)
```

#### 7.3 创建或更新 Fix

**新建记录**：
```python
project_add(
    project_id="<project_id>",
    group="fixes",
    content="<标题>: <摘要>",
    description="<摘要>",
    severity="<severity>",
    status="<status>",
    note_id="<note_id或空>",
    tags="fix,<module>,<severity>"
)
```

**合并到现有记录**：
```python
# 先获取现有记录
existing_fix = project_get(project_id, "fixes", "<fix_id>")

# 如果现有记录有 note_id，追加内容
if existing_fix.get("note_id"):
    project_update(
        project_id=project_id,
        group="notes",
        item_id=existing_fix["note_id"],
        content="<追加新内容>"
    )

# 如果需要创建新的 note
elif len(description) > 30:
    # 创建 note 并关联
    ...

# 更新 fix 的 description（可选）
project_update(
    project_id=project_id,
    group="fixes",
    item_id="<fix_id>",
    description="<更新后的描述>"
)
```

**重启现有记录**：
```python
project_update(
    project_id=project_id,
    group="fixes",
    item_id="<fix_id>",
    status="in_progress"
)
```

---

### 步骤 8: 输出结果

```
## 记录成功

- Fix ID: <fix_id>
- 状态: <status>
- 严重程度: <severity>
- Note ID: <note_id 或 无>
```

---

## 示例

### 示例 1: 新建记录

```
用户: /memory-fix 登录接口超时，等待30秒无响应

技能处理：
1. 确定项目: ai_memory_mcp
2. 查询相关 fix: 无
3. 推荐状态: pending (包含"等待"描述)
4. 严重程度: medium (默认)
5. 描述长度: > 30 字符 → 创建 Note
6. 记录成功

结果:
- Fix ID: fix_20260322_001
- 状态: pending
- Note ID: note_20260322_003
```

### 示例 2: 合并到现有记录

```
用户: /memory-fix 登录接口有时会超时

技能处理：
1. 确定项目: ai_memory_mcp
2. 查询相关 fix: 发现 fix_20260322_001 "登录接口超时"
3. 显示提示，用户选择合并
4. 追加内容到现有 Note
5. 记录成功

结果:
- Fix ID: fix_20260322_001 (已更新)
- 状态: pending (不变)
```

### 示例 3: 重启现有记录

```
用户: /memory-fix 登录接口超时问题又出现了

技能处理：
1. 确定项目: ai_memory_mcp
2. 查询相关 fix: 发现 fix_20260322_001 "登录接口超时" (状态: completed)
3. 显示提示，用户选择重启
4. 更新状态为 in_progress
5. 记录成功

结果:
- Fix ID: fix_20260322_001 (已重启)
- 状态: in_progress
```

---

## 注意事项

1. **关键词提取**: 简单按空格分词，去除停用词（的、了、是等）
2. **相似度计算**: 关键词重合数 / 用户关键词总数
3. **状态推荐**: 基于关键词匹配，用户可以覆盖
4. **Note 创建**: 仅在描述 > 30 字符时创建
5. **错误处理**: 任何 MCP 调用失败时，显示错误信息并退出
