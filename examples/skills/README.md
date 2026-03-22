# Skills 示例

本目录包含 AI Memory MCP 项目的相关 Skills 示例，这些 Skills 与 Memory MCP 配合使用，实现完整的项目开发流程。

## Skills 列表

### 开发流程类

| Skill | 说明 | 触发词 |
|-------|------|--------|
| **feature-dev** | 功能开发完整流程，从需求分析到代码实现 | `feature`, `功能`, `开发` |
| **bug-fix** | Bug 修复完整流程，从问题分析到修复验证 | `bug`, `fix`, `修复` |

### Git 管理类

| Skill | 说明 | 触发词 |
|-------|------|--------|
| **git-branch** | 为开发技能提供 Git 分支准备和合并功能 | - |
| **git-commit** | 自动生成符合 Conventional Commits 规范的中文提交信息 | `commit` |
| **git-feature-merge** | 功能开发完成后合并到主干分支 | - |

### 记忆管理类

| Skill | 说明 | 触发词 |
|-------|------|--------|
| **memory-std** | 初始化项目标准规范，支持自动探索和用户输入 | `memory-std` |
| **rememory-std** | 回忆项目规范，支持语义过滤 | `rememory-std` |
| **rememory-project** | 按标签查询项目记忆 | `query`, `search`, `记忆`, `回忆` |
| **memory-tidy** | 整理项目记忆，合并重复、清理冗余 | `tidy`, `整理` |

## 使用方式

### 安装 Skills

将需要的 Skill 目录复制到 `~/.claude/skills/` 目录下：

```bash
# 示例：安装 feature-dev 技能
cp -r examples/skills/feature-dev ~/.claude/skills/
```

### 技能调用

在 Claude Code 中使用斜杠命令调用技能：

```
# 开发新功能
/feature-dev 实现用户登录功能

# 修复 Bug
/bug-fix 登录接口报错

# 生成提交信息
/commit

# 查询记忆
/rememory-project 用户认证相关记录

# 初始化项目规范
/memory-std code-style
```

## 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        项目开发流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ memory-std   │───→│ rememory-std │───→│ 项目规范就绪  │      │
│  │ 初始化规范    │    │ 回忆规范      │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│           ↓                                            ↓        │
│  ┌──────────────┐                            ┌──────────────┐   │
│  │ feature-dev  │                            │  bug-fix     │   │
│  │ 功能开发流程  │                            │  Bug修复流程  │   │
│  └──────────────┘                            └──────────────┘   │
│           ↓                                            ↓        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  git-commit  │←───│git-branch    │    │ memory-tidy  │      │
│  │  生成提交信息 │    │ 分支管理      │    │ 整理记忆      │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Skill 依赖关系

```
feature-dev
├── rememory-std (回忆规范)
├── rememory-project (查询记忆)
├── git-branch (分支管理)
└── git-commit (提交信息)

bug-fix
├── rememory-std (回忆规范)
├── rememory-project (查询记忆)
├── git-branch (分支管理)
└── git-commit (提交信息)

git-branch
└── git-commit (生成提交信息)
```

## 注意事项

1. **安装位置**: Skills 必须安装在 `~/.claude/skills/` 目录下才能被识别
2. **MCP 依赖**: 大部分 Skills 依赖 Memory MCP 服务，请确保服务正常运行
3. **参数格式**: 每个 Skill 的参数格式不同，请参考具体 Skill 文件
4. **冲突检测**: Git 相关 Skills 会自动检测冲突，有冲突时会提示处理

## 自定义 Skills

你可以基于这些示例 Skills 创建自己的定制版本：

1. 复制示例 Skill 目录
2. 修改 `SKILL.md` 文件
3. 调整流程和参数
4. 安装到 `~/.claude/skills/` 目录
