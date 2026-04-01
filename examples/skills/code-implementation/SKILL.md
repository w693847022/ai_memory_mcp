---
name: code-implementation
description: 代码实现与测试 - 按照方案实现代码、编写单元测试、执行整合测试（支持 feature 和 fix）
allowed-tools: mcp__memory_mcp__project_get, mcp__memory_mcp__project_update, Read, Edit, Write, Bash, Grep, Glob
argument-hint: <feature_id|fix_id>
---

# 代码实现与测试技能

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
- 必须存在 `[<item_id>-implementation-plan]` note
- 必须存在 `[<item_id>-development-log]` note

### 推荐前置条件
- 已确认测试计划
- 已在正确的开发分支上

---

## ⚠️ 重要指令

**DO NOT ENTER PLAN MODE** - 此技能要求直接执行，不进入计划模式

**所有memory_mcp的操作使用子代理来处理，减少主窗口上下文**

**开发记录**: 每一步的关键结果记录到[<item_id>-development-log]note中

**提醒用户使用 auto 模式**

---

## 初始化

1. 读取memory_mcp中的对应记录（feature 或 fix）

2. 读取关联的notes:
   - `[<item_id>-requirements]` 或 `[<item_id>-requirements]`: 完整需求/问题描述
   - `[<item_id>-implementation-plan]`: 实现方案
   - `[<item_id>-development-log]`: 开发历史

3. 检查Git分支，确认不在main/master分支上

---

## 阶段 1: 代码实现

**目标**: 按照确认的方案进行代码编写

**流程**:

1. 按照确认的方案进行代码编写
   - 如果是测试返回的代码修改，则根据具体情况进行修改

2. 每完成一个功能模块后更新开发记录note，记录摘要

3. 如果编写阶段出现文件修改方面的问题，需要先解决该问题后再修改代码
   - 多次解决不掉则让用户协助

4. 全部修改完成后，如果有则使用对应语言的静态检测工具进行扫描
   - 如果有ERROR类型的扫描结果，则修复然后返回本阶段步骤4
   - 循环三次后暂停请求用户协助

---

## 阶段 2: 单元测试

**目标**: 根据之前确认的需求单元测试创建并执行测试

**流程**:

1. 根据之前确认的需求单元测试创建单元测试文件然后执行测试

2. 如果测试失败：
   - 如果因为需求实现代码逻辑问题 **返回阶段1** 进行分析错误原因并修改代码
   - 如果因为单元测试文件本身问题修改后重新执行
   - 不管什么原因循环超过3次仍然失败，暂停并请用户介入决策

3. 单元测试成功后更新开发记录，记录测试结果

4. 继续下一步

---

## 阶段 3: 整合测试

**目标**: 执行项目的全测试用例测试

**流程**:

1. 检查项目测试规范，如果有则执行项目全用例测试
   - 如果本次修改导致测试需要调整则需要 **返回阶段1** 进行测试代码调整

2. 如果测试失败 **返回阶段1** 进行分析错误原因并修改代码

3. 循环超过3次仍然失败，暂停并请用户介入决策

4. 整合测试成功后更新开发记录，记录测试结果

---

## 输出

```
item_id: <feature_id|fix_id>
implementation_result:
  code_status: completed
  unit_test: passed
  integration_test: passed
```

---

## 完成展示

展示开发完成摘要：
```
item_id: <feature_id|fix_id>

代码实现: 完成
单元测试: 通过
整合测试: 通过

开发记录: [<item_id>-development-log]
```
