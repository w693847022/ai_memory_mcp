---
name: memory-tidy
description: memory tidy 整理MCP[memory_mcp]记忆
allowed-tools: mcp__memory_mcp__project_list, mcp__memory_mcp__project_get, mcp__memory_mcp__project_groups_list, mcp__memory_mcp__project_tags_info, mcp__memory_mcp__project_update, mcp__memory_mcp__project_add, mcp__memory_mcp__project_delete, mcp__memory_mcp__project_item_tag_manage, mcp__memory_mcp__tag_merge, mcp__memory_mcp__tag_register, mcp__memory_mcp__tag_update, mcp__memory_mcp__project_feature_update, mcp__memory_mcp__project_feature_delete, mcp__memory_mcp__project_fix_add, mcp__memory_mcp__project_fix_update, mcp__memory_mcp__project_fix_delete, mcp__memory_mcp__project_note_update, mcp__memory_mcp__project_note_delete
---

# Memory 整理技能

整理 MCP [memory_mcp] 中的项目记忆数据，包括功能记录、修复记录、笔记和标签。

## 前置准备

1. **获取项目列表**: 使用 `project_list` 查看所有项目
2. **选择目标项目**: 让用户确认要整理的项目
3. **获取项目详情**: 使用 `project_get` 获取完整数据

## 整理流程

### 步骤 1: 整理 Feature 功能记录

1. **识别重复功能**: 查找描述相似或功能相同的记录
2. **合并重复项**:
   - **重要：只有状态一致的条目支持合并**（pending 只能和 pending 合并，completed 只能和 completed 合并）
   - 选择保留的主要记录（通常是描述更完整或更新的）
   - **合并前必须向用户确认**，说明合并原因
   - 将其他重复记录的标签合并到主记录
   - 如有关联笔记，选择保留最完整的
   - 删除被合并的重复记录
3. **清理标签**: 移除无意义或重复的标签

**合并确认格式**：
```
即将合并以下功能记录：

保留: [ID] 描述内容...
删除: [ID] 描述内容...

合并原因: [说明为什么这两个记录重复/相似]

是否确认合并？(y/n)
```

**操作示例**:
```
# 1. 查看功能列表
project_get(project_id="xxx", group_name="features")

# 2. 合并标签到主记录
project_item_tag_manage(project_id="xxx", group_name="features", item_id="主记录ID", operation="add", tag="被合并记录的标签")

# 3. 删除重复记录
project_delete(project_id="xxx", group="features", item_id="重复记录ID")
```

### 步骤 2: 整理 Fix 修复记录

1. **识别重复修复**: 查找相同问题的多次记录
2. **合并重复项**:
   - **重要：只有状态一致的条目支持合并**（pending 只能和 pending 合并，completed 只能和 completed 合并）
   - **合并前必须向用户确认**，说明合并原因（同 Feature 格式）
   - 其余逻辑同 Feature 合并
3. **检查关联**: 确保修复记录正确关联到相关 Feature

### 步骤 3: Feature → Fix 迁移

有些 Feature 记录实际上描述的是 Bug 修复，需要迁移：

**判断标准**:
- 描述中包含 "修复"、"fix"、"bug"、"问题" 等关键词
- 内容主要是解决某个问题而非新增功能

**迁移操作**:
```
# 场景A: 全部内容都是修复
# 1. 在 fix 分组创建新记录
project_add(project_id="xxx", group="fixes", content="修复描述", severity="medium", tags="原标签")

# 2. 删除原 feature 记录
project_delete(project_id="xxx", group="features", item_id="原ID")

# 场景B: 部分是修复
# 1. 为修复部分创建 fix 记录
project_add(project_id="xxx", group="fixes", content="修复部分内容", related_feature="原featureID")

# 2. 更新原 feature，移除修复部分
project_update(project_id="xxx", group="features", item_id="原ID", content="仅保留功能部分")
```

### 步骤 4: 整理 Note 笔记

**前置：理解 Note 关联的意义**

Note 是 Feature 或 Fix 的**细节补充**，它们之间存在语义关联：
- 关联了 feature 的 note → 是该功能的技术细节/实现说明
- 关联了 fix 的 note → 是该修复的原因分析/解决方案细节
- **无关联的 note** → 独立的开发笔记/临时记录

---

#### 4.1 删除 Note 的判断

**核心原则**：有关联的 note 是 feature/fix 的补充，不应轻易删除

```
删除前检查流程：
1. 查询 feature 和 fix 列表，检查 note_id 是否指向该 note
2. 如果有关联 → 保留该 note，它是补充说明
3. 如果无关联 → 可以删除（独立的临时笔记）
```

**不应删除的情况**：
- note 关联了有效的 feature（feature 状态非 deleted）
- note 关联了有效的 fix

**可以删除的情况**：
- note 无任何关联，且内容已过时
- note 无关联，且内容已合并到其他笔记

---

#### 4.2 合并 Note 的场景判断

合并前，必须先分析两个 note 的关联情况，按以下场景处理：

| 场景 | note1 | note2 | 处理方式 |
|------|-------|-------|----------|
| A | 关联 feature1 | 关联 feature2 | **先判断 feature1 和 feature2 是否需要合并** |
| B | 关联 feature1 | 无关联 | 直接合并 note2 到 note1，保持 feature1 关联 |
| C | 关联 feature1 | 关联 fix1 | **不合并**（跨类型关联） |
| D | 关联 fix1 | 关联 fix2 | **先判断 fix1 和 fix2 是否需要合并** |
| E | 无关联 | 无关联 | 直接合并，无需处理关联 |

**场景 A 详细处理**（note1→feature1, note2→feature2）场景D同理：
```
1. 先判断 feature1 和 feature2 是否是重复/相似功能
   - 如果是 → 先合并 feature（使用 Feature 整理流程）
   - 合并后，两个 note 都关联到同一个 feature，再合并 note
   - 如果否 → 两个 note 分属不同功能，不应合并
```

**场景 B 详细处理**（note1→feature1, note2 无关联）：
```
1. 将 note2 内容合并到 note1
2. 删除 note2（它只是独立笔记，合并后不再需要）
3. feature1 的关联保持不变
```

---

#### 4.3 操作顺序（重要）

```
1. 查询所有 feature 和 fix，建立 note_id → [关联的 feature/fix] 映射表
2. 分析要合并/删除的 note 的关联情况
3. 根据场景判断表决定处理方式
4. 如需先合并 feature/fix，先完成 feature/fix 合并
5. 执行 note 合并/删除操作
6. 同步更新受影响的 feature/fix 的 note_id
7. 最后删除被合并/废弃的笔记
```

**代码示例**：
```
# 查找关联关系
project_get(project_id="xxx", group_name="features")  # 检查所有 feature.note_id
project_get(project_id="xxx", group_name="fixes")     # 检查所有 fix.note_id

# 合并笔记后更新关联
project_update(project_id="xxx", group="features", item_id="关联的featureID", note_id="新笔记ID")

# 确认关联更新后再删除旧笔记
project_delete(project_id="xxx", group="notes", item_id="被合并的笔记ID")
```

### 步骤 5: 标签整理

1. **获取标签统计**:
```
project_tags_info(project_id="xxx")
```

2. **识别相似标签**: 查找语义相近的标签
   - 例如: "bugfix" 和 "fix", "implementation" 和 "impl"
   - 中英文同义: "修复" 和 "fix"

3. **合并标签**:
   - **合并前必须向用户确认**，说明合并原因
```
# 合并确认格式
即将合并标签:

旧标签: "bugfix" (N 个条目使用)
新标签: "fix" (M 个条目使用)

合并原因: [说明为什么这两个标签语义相同]

是否确认合并？(y/n)

# 确认后执行合并
tag_merge(project_id="xxx", old_tag="bugfix", new_tag="fix")
```

4. **注册缺失标签**: 为未注册的常用标签添加语义描述
```
tag_register(project_id="xxx", tag_name="refactor", description="代码重构相关，不改变功能的代码改进")
```

## 注意事项

1. **合并确认**: **执行任何合并操作前必须向用户确认**，说明合并原因
2. **合并限制**: **只有状态一致的条目支持合并**（pending 只能和 pending 合并，in_progress 只能和 in_progress 合并，completed 只能和 completed 合并）
3. **谨慎删除**: 删除前确认内容已合并或不再需要
4. **保留关联**: 合并时注意保持笔记与功能/修复的关联关系
5. **标签规范**: 合并后建议使用英文标签，保持一致性

## 输出格式

整理完成后，输出整理报告：

```
## 整理报告 - 项目: {项目名}

### 功能记录
- 合并: X 条 → Y 条
- 迁移到修复: Z 条

### 修复记录
- 合并: X 条 → Y 条
- 新增（从功能迁移）: Z 条

### 笔记
- 合并: X 条
- 删除: Y 条

### 标签
- 合并: "old_tag" → "new_tag" (N 条记录)
- 新注册: "tag_name" (描述)
```

