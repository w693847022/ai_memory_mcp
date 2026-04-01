---
name: fix-bug-s
description: Bug修复（拆分版本）- 每个阶段独立文件，便于按需引用和修改
allowed-tools: mcp__memory_mcp__project_list, mcp__memory_mcp__project_get, mcp__memory_mcp__project_add, mcp__memory_mcp__project_update, mcp__memory_mcp__project_tags_info, mcp__memory_mcp__tag_register, Read, Grep, Glob, Bash, Skill
argument-hint: <Bug描述>
---

# Bug 修复技能（拆分版）

## ⚠️ 重要指令

**不要并发执行步骤，后面步骤必须要前面步骤完全执行成功**

**DO NOT ENTER PLAN MODE** - 此技能要求直接执行，不进入计划模式，如果在计划模式则需要退出计划模式。

**所有memory_mcp的操作使用子代理来处理，减少主窗口上下文**

**修复记录**: 阶段1后的每一步的关键结果记录到阶段1创建的[<fix_id>-development-log]note中
    - 如果记录时因为入参不规范导致失败，需要重试

**修复流程中会创建的记录**
```
fix:
  id: [fix_id]

note:
  summary:
    - [<fix_id>-requirements]
    - [<fix_id>-implementation-plan]
    - [<fix_id>-development-log]
```

**进度恢复**: 如果用户指定了已经记录Bug修复和该Bug的修复记录的情况下，根据修复记录直接恢复之前上下文，然后跳到记录阶段向后执行。
  - 如果不确定是哪一步则提示用户从阶段1开始，用户确认后清理修复记录后从阶段1开始
  - **恢复前需要执行阶段1,确认项目和回忆规范**

**开始前需要按阶段建立TODO列表，让用户知道当前到那个阶段的那个步骤了**

**每一个阶段使用子代理处理**

---

## 使用示例

### 完整流程 (从开始到结束)
```
/skill fix-bug-s "用户登录功能报错500"
```

### 从中间阶段恢复
```
/skill requirement-confirmation "fix_20260401_001"
/skill solution-design "fix_20260401_001"
/skill code-implementation "fix_20260401_001"
```

---

## 流程概览

```
阶段1    →  阶段2    →  阶段3    →  阶段4    →  阶段5    →  阶段6    →  阶段7    →  阶段8
项目确认 → Bug探索   → 问题澄清 → 方案设计 → 测试确认 → Git准备  → 代码实现 → 分支合并
                   (技能)                        (技能)    (技能)
```

---

## 阶段输出约定 (上下文传递)

| 阶段 | 输出变量 | 说明 |
|------|---------|------|
| 阶段1 | `fix_id`, `project_id` | 修复ID和项目ID |
| 阶段2 | `exploration_result`, `root_cause` | 探索结果和根因 |
| 阶段3 | `confirmed_requirements` | 确认的问题描述 |
| 阶段4 | `selected_solution` | 选择的修复方案 |
| 阶段5 | `test_plan` | 测试计划 |
| 阶段6 | `branch_name` | Git分支名 |
| 阶段7 | `implementation_result` | 实现结果 |
| 阶段8 | `merge_result` | 合并结果 |

---

## 阶段 1: 项目确认

**流程**: 按照 `01-project-confirmation.md` 执行

**输出**:
- `fix_id`: 修复ID
- `project_id`: 项目ID
- `project_name`: 项目名称

**本阶段会完成**:
1. 回忆项目结构规范、代码开发规范、测试规范和部署规范
2. 创建fix记录
3. 创建development-log note

---

## 阶段 2: Bug 探索

**流程**: 按照 `02-bug-exploration.md` 执行

**输出**:
- `exploration_result`: 探索结果对象
- `root_cause`: Bug根因分析

**下一阶段使用**: `requirement-confirmation` 技能会使用这些输出

---

## 阶段 3: 问题澄清与确认

**使用技能**: `requirement-confirmation`

```
Skill: requirement-confirmation, args: "<fix_id>"
```

**技能会完成**:
1. 问题澄清（多轮提问，使用阶段2的root_cause）
2. 问题确认
3. 创建note记录完整问题描述
4. 更新development-log

**输出**:
- `confirmed_requirements`: 确认的问题描述

---

## 阶段 4: 方案设计与选择

**使用技能**: `solution-design`

```
Skill: solution-design, args: "<fix_id>"
```

**技能会完成**:
1. 方案设计（探索代码库并设计方案）
2. 用户选择方案
3. 方案详细规划
4. 创建note记录完整方案
5. 更新development-log

**输出**:
- `selected_solution`: 选择的修复方案

---

## 阶段 5: 测试确认

**流程**: 按照 `04-test-confirmation.md` 执行

**输出**:
- `test_plan`: 测试计划

---

## 阶段 6: Git 分支准备

**流程**: 按照 `05-git-prepare.md` 执行

**输出**:
- `branch_name`: Git分支名

---

## 阶段 7: 代码实现与测试

**使用技能**: `code-implementation`

```
Skill: code-implementation, args: "<fix_id>"
```

**技能会完成**:
1. 代码实现
2. 单元测试
3. 整合测试
4. 更新development-log

**输出**:
- `implementation_result`: 实现结果

---

## 阶段 8: Git 分支合并

**流程**: 按照 `06-git-merge.md` 执行

**输出**:
- `merge_result`: 合并结果

**完成操作**:
- 更新fix状态为completed
- 整理development-log

---

## 错误处理

如果子技能执行失败:
1. 记录失败点到development-log
2. 询问用户: 重试 / 跳过 / 回退上一阶段
3. 根据用户选择继续

---

## 最后展示相关的记录ID

```
fix:
  - fix_id
  - fix:summary
  - fix:content

note:
  - note_id:summary (requirements)
  - note_id:summary (implementation-plan)
  - note_id:summary (development-log)
```
