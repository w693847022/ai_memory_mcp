---
name: rememory-project
description: query memory explore show search 搜索 记忆 查询 回忆 展示 使用MCP[memory_mcp]查询过往记录
allowed-tools: mcp__memory_mcp__project_list, mcp__memory_mcp__project_tags_info, mcp__memory_mcp__project_get
context: fork
---

# 前提:

如果没有 $ARGUMENTS 询问用户需要输入查询内容

# 查询流程

1. context: fork subagent

1. **确定查询项目**
    - 调用 `project_list` 获取所有项目列表
    - 确定目标项目 ID

2. **查询项目所有注册标签**
    - 调用 `project_tags_info(project_id)` 获取标签列表
    - 返回信息包含：
        - 标签描述
        - 所属分组（features/notes/fixes）及每个分组中的条目数
        - 使用次数

1. context: fork subagent

3. **筛选和$ARGUMENTS相关的标签**
    - 根据标签描述和所属分组信息，确定需要查询的标签名称
    - 注意所属分组信息格式：`features(2), notes(1)` 表示该标签在 features 分组有 2 条，notes 分组有 1 条

4. **查询标签下的具体内容**
    - 调用 `project_tags_info(project_id, group_name, tag_name)`
    - 查看该标签在指定分组下的所有条目详情
    - 总结摘要和对应的记录ID返回

---

# 示例

```
# 1. 列出项目
project_list()

# 2. 查看 mcp_test 项目的所有标签
project_tags_info("mcp_test")

# 3. 假设要查看 "api" 标签在 "features" 分组下的内容
project_tags_info("mcp_test", "features", "api")
```

---

# 输出说明

- `所属分组: features(2), notes(1)` - 该标签在 features 分组有 2 条记录，notes 分组有 1 条记录
- `所属分组: 未使用` - 该标签已注册但尚未被任何条目使用
- `使用次数` - 标签被使用的总次数
