---
name: solution-design
description: 方案设计与选择 - 探索代码库并设计方案，用户选择后进行详细规划（支持 feature 和 fix）
allowed-tools: mcp__memory_mcp__project_get, mcp__memory_mcp__project_add, mcp__memory_mcp__project_update, Agent, AskUserQuestion, Read, Grep, Glob
argument-hint: <feature_id|fix_id>
---

# 方案设计与选择技能

## 参数规范

| 参数 | 说明 | 要求 |
|------|------|------|
| `feature_id` | 已存在的功能ID | **必需**（feature 类型） |
| `fix_id` | 已存在的修复ID | **必需**（fix 类型） |

**无参数时**: 拒绝执行

**参数无效时**: 拒绝执行并提示

---

## 前置条件

### 必需前置条件
- `feature_id` 或 `fix_id` 必须存在
- 对应记录中必须有已确认的需求/问题描述

### 推荐前置条件
- 已完成相关性探索结果

---

## ⚠️ 重要指令

**DO NOT ENTER PLAN MODE** - 此技能要求直接执行，不进入计划模式

**所有memory_mcp的操作使用子代理来处理，减少主窗口上下文**

**开发记录**: 每一步的关键结果记录到[<item_id>-development-log]note中

---

## 初始化

1. 读取memory_mcp中的对应记录（feature 或 fix），获取确认的需求/问题描述

2. 读取关联的notes:
   - `[<item_id>-requirements]` 或 `[<item_id>-requirements]`: 完整需求/问题描述
   - `[<item_id>-development-log]`: 开发历史

3. 如果存在 `exploration_result`，使用它作为设计基础

---

## 阶段 1: 方案设计

**目标**: 探索代码库并设计方案

**流程**:

1. 探索代码库：
   - 使用 Explore 代理探索
   - 分析现有架构和模式
   - 需要符合上下文中提到的规范
   - 设计 1-3 个实现方案

2. 向用户展示方案选项

**方案格式**:
```
## 方案一: <方案名称>

**优点**: <优点列表>
**缺点**: <缺点列表>
**实现步骤**:
1. <步骤1>
2. <步骤2>
...

**影响范围**: <文件列表>

---

## 方案二: <方案名称>
...
```

3. 请问用户有没有方案设计方向建议
   - 如果提出建议则返回步骤1重新设计方案

4. 要求用户 **选择一个方案**

---

## 阶段 2: 方案详细规划

**目标**: 根据用户选择的方案进行详细规划

**流程**:

**要求**: 代码修改需要符合之前查询到的代码相关规范

1. 根据初选方案、开发规范、之前探索对需求的理解，给出这个方案的详细改动实例

   **实例详细程度**:
   - 列出函数级别的更改项
   - 列出核心逻辑的代码段改动
   - 列出受影响的文件列表

2. 询问用户修改建议
   - 如果有修改建议则根据建议修改后返回步骤1

3. 建立note[<item_id>-implementation-plan] 记录完整方案内容
   - 在对应条目中增加这个note的关联

4. 更新development-log note
   - 记录方案设计和选择已经完成 

---

## 输出

```
item_id: <feature_id|fix_id>
selected_solution: <选择的方案对象>
```

---

## 完成展示

展示创建/更新的记录ID：
```
record:
  - item_id

note:
  - note_id:summary (implementation-plan)
  - note_id:summary (development-log updated)
```
