---
name: memory-std
description: 初始化项目标准 standard 规范 初始化 初始化标准 使用MCP[memory_mcp]记录项目标准
allowed-tools: mcp__memory_mcp__project_list, mcp__memory_mcp__project_get, mcp__memory_mcp__project_groups_list, mcp__memory_mcp__project_tags_info, mcp__memory_mcp__project_add, mcp__memory_mcp__project_update, mcp__memory_mcp__tag_register, Glob, Grep, Read,Git
context: fork
---

# Memory-std 技能

初始化项目标准并记录到 memory_mcp 的技能。支持用户输入标准和自动探索项目标准。

## 触发方式

- `/memory-std` - 探索项目所有可能规范
- `/memory-std <类型>` - 探索指定类型的规范
- `/memory-std <类型> <内容>` - 添加指定类型的标准
- `/memory-std <标准内容>` - 直接添加标准（向后兼容）

---

## 流程概览

```
解析输入 → 自动探索(可选) → 标准分类 → 去重检测 → 冲突处理 → 批量添加 → 输出报告
    │            │              │           │           │           │
    └─有输入跳过─→ CLAUDE.md ─→ tags分类 ─→ 相似度 ─→ 用户确认 ─→ project_add
                  配置文件                    >70%       合并/新建
                  代码模式
```

---

## 阶段 1: 确定项目

**目标**: 获取项目 ID 和已有标准

```python
# 1. 获取项目列表
project_list()

# 2. 确定当前项目 ID（通过 Git remote 或目录名）
# 如果有多个项目，让用户选择

# 3. 查询已有标准
project_get(project_id="<项目ID>", group_name="standards")

# 4. 获取已注册标签
project_tags_info(project_id="<项目ID>")
```

---

## 阶段 2: 解析用户输入

### 输入格式

`/memory-std [类型] [内容]`

| 输入示例 | 类型 | 内容 | 行为 |
|---------|------|------|------|
| `/memory-std` | 无 | 无 | 探索项目所有可能规范 |
| `/memory-std code-style` | code-style | 无 | 探索 code-style 类型规范 |
| `/memory-std 代码生成规范` | 代码生成规范 | 无 | 探索代码生成规范类型 |
| `/memory-std code-style 4空格缩进` | code-style | 4空格缩进 | 添加标准，打 code-style 标签 |
| `/memory-std 代码生成规范 使用snake_case` | 代码生成规范 | 使用snake_case | 添加标准，自动注册标签 |

### 解析逻辑

```python
# 解析 $ARGUMENTS
args = $ARGUMENTS.strip()

if not args:
    # 无参数: 探索所有规范
    mode = "explore_all"
elif " " in args:
    # 有空格: 第一个词为类型，其余为内容
    parts = args.split(" ", 1)
    std_type = parts[0]
    content = parts[1]
    mode = "add_typed"
else:
    # 无空格: 整个参数为类型
    std_type = args
    content = None
    mode = "explore_typed"
```

### 中文→英文标签映射

| 中文类型 | 英文标签 | 说明 |
|---------|---------|------|
| 代码风格/代码格式 | code-style | 缩进、换行、引号 |
| 命名规范/命名 | naming | 变量、函数命名 |
| 提交规范/git规范 | git | commit message |
| 代码生成规范 | code-generation | AI生成代码规范 |
| API规范 | api | 接口设计规范 |
| 测试规范 | testing | 测试覆盖率等 |
| 文档规范 | docs | 注释、README |
| 目录结构 | structure | 文件组织 |
| 日志规范 | logging | 日志格式 |
| 安全规范 | security | 安全编码规范 |

```python
def get_english_tag(chinese_type):
    """中文类型转英文标签"""
    mappings = {
        "代码风格": "code-style", "代码格式": "code-style",
        "命名规范": "naming", "命名": "naming",
        "提交规范": "git", "git规范": "git",
        "代码生成规范": "code-generation",
        "API规范": "api", "接口规范": "api",
        "测试规范": "testing",
        "文档规范": "docs",
        "目录结构": "structure",
        "日志规范": "logging",
        "安全规范": "security",
    }
    # 直接匹配
    if chinese_type in mappings:
        return mappings[chinese_type]
    # 检查是否已是英文标签
    if chinese_type.isascii():
        return chinese_type
    # 自定义中文类型: 生成英文标签
    return generate_english_tag(chinese_type)
```

### 自定义类型处理

当用户输入的类型不在映射表中时，自动生成英文标签：

```python
def generate_english_tag(chinese_type):
    """为自定义中文类型生成英文标签"""
    # 示例: "代码生成规范" -> "code-generation"
    # 提取关键词并翻译
    keywords = {
        "代码": "code", "规范": "standard", "标准": "standard",
        "生成": "generation", "自动": "auto", "配置": "config",
        "性能": "performance", "优化": "optimization",
        "部署": "deploy", "构建": "build"
    }
    # 组合生成标签 (使用连字符)
    parts = [keywords.get(k, k) for k in keywords if k in chinese_type]
    return "-".join(parts) if parts else chinese_type.lower()
```

---

## 阶段 3: 自动探索

**触发条件**: `mode == "explore_all"` 或 `mode == "explore_typed"`

**目标**: 从多个来源自动提取项目标准

### 类型过滤

当 `mode == "explore_typed"` 时，只探索与指定类型相关的来源：

```python
# 类型→配置文件映射
TYPE_CONFIG_MAP = {
    "code-style": [".editorconfig", ".eslintrc*", ".prettierrc*", "pyproject.toml", ".flake8", "rustfmt.toml", ".clang-format"],
    "naming": [".eslintrc*", "pyproject.toml"],  # 命名规则通常在lint配置中
    "git": [".gitattributes", "commitlint.config.*"],
    "api": [],  # 从代码注释和文档提取
    "testing": ["pytest.ini", "jest.config.*", "vitest.config.*"],
    "docs": [],  # 从 README 和注释提取
    "structure": [],  # 从目录结构提取
}

# 如果指定了类型，过滤探索范围
if std_type:
    english_tag = get_english_tag(std_type)
    target_configs = TYPE_CONFIG_MAP.get(english_tag, [])
```

### 3.1 探索 CLAUDE.md

```python
# 查找 CLAUDE.md
Glob(pattern="CLAUDE.md")
Glob(pattern="**/CLAUDE.md")

# 读取并提取标准
Read(file_path="<CLAUDE.md路径>")
# 提取内容:
# - 编码规范
# - 提交规范
# - 项目特定标准
```

**提取规则**:
- 查找 "规范"、"标准"、"约定"、"必须"、"应该" 等关键词
- 识别列表形式的规则
- 提取配置说明

### 3.2 探索配置文件

按优先级探索以下文件：

| 文件 | 提取内容 | 标准类型 |
|------|----------|----------|
| `.editorconfig` | 缩进、换行符、编码 | code-style |
| `.eslintrc*` | JS/TS 代码规则 | code-style |
| `.prettierrc*` | 格式化规则 | code-style |
| `pyproject.toml` | Python 配置、black/isort 规则 | code-style |
| `.flake8` | Python lint 规则 | code-style |
| `rustfmt.toml` | Rust 格式化规则 | code-style |
| `.clang-format` | C/C++ 格式化规则 | code-style |
| `.gitattributes` | Git 属性规范 | git |
| `commitlint.config.*` | 提交信息规范 | git |

```python
# 探索配置文件
config_files = [
    ".editorconfig", ".eslintrc", ".eslintrc.js", ".eslintrc.json",
    ".prettierrc", ".prettierrc.js", ".prettierrc.json",
    "pyproject.toml", ".flake8", "setup.cfg",
    "rustfmt.toml", ".clang-format",
    "commitlint.config.js", ".gitattributes"
]

for file in config_files:
    Glob(pattern=file)
    # 如果找到，读取并提取规则
```

### 3.3 探索代码模式

**命名规范**:
```python
# 检查文件命名模式
Glob(pattern="src/**/*.py")  # Python: snake_case
Glob(pattern="src/**/*.js")  # JS: camelCase 或 kebab-case
Glob(pattern="src/**/*.rs")  # Rust: snake_case

# 检查类/函数命名
Grep(pattern="^(class|def|function|const|let|var)\s+[A-Z]", ...)  # PascalCase
Grep(pattern="^(def|function|const|let|var)\s+[a-z]", ...)  # camelCase/snake_case
```

**目录结构**:
```python
# 识别常见目录模式
Glob(pattern="src/*")  # 查看顶层目录结构
# 常见模式:
# - src/api, src/core, src/utils → 分层架构
# - src/components, src/pages → 前端架构
# - tests/, test/ → 测试目录
```

---

## 阶段 4: 标准分类

**目标**: 为提取的标准分配合适的 tags

### 预定义标签分类

| 标签 | 描述 | 示例 |
|------|------|------|
| `code-style` | 代码风格和格式化 | 缩进、换行、引号风格 |
| `git` | Git 提交和分支规范 | commit message 格式、分支命名 |
| `api` | API 设计规范 | RESTful 规范、错误码格式 |
| `naming` | 命名规范 | 变量、函数、类命名规则 |
| `structure` | 目录结构规范 | 文件组织、模块划分 |
| `testing` | 测试规范 | 测试覆盖率、测试命名 |
| `docs` | 文档规范 | 注释风格、README 格式 |
| `code-generation` | 代码生成规范 | AI 生成代码规范 |
| `logging` | 日志规范 | 日志格式、级别 |
| `security` | 安全规范 | 安全编码规范 |

### 自动注册缺失标签

```python
# 检查标签是否已注册
project_tags_info(project_id="<项目ID>")

# 如果需要的标签未注册，先注册
for tag in needed_tags:
    if tag not in registered_tags:
        tag_register(
            project_id="<项目ID>",
            tag_name=tag,
            description=TAG_DESCRIPTIONS.get(tag, f"{tag} 规范")
        )
```

### 自定义类型自动注册

当用户指定的类型不在预定义标签中时：

```python
# 检查是否是自定义类型
if mode == "add_typed" and std_type not in TAG_DESCRIPTIONS:
    english_tag = get_english_tag(std_type)
    # 自动注册标签
    tag_register(
        project_id="<项目ID>",
        tag_name=english_tag,
        description=f"{std_type}规范 (自动生成)"
    )
    tag = english_tag
```

**标签描述映射**:
```python
TAG_DESCRIPTIONS = {
    "code-style": "代码风格和格式化规范，包括缩进、换行、引号等",
    "git": "Git 相关规范，包括提交信息格式、分支命名策略",
    "api": "API 设计规范，包括接口风格、错误处理、版本控制",
    "naming": "命名规范，包括变量、函数、类、文件的命名约定",
    "structure": "目录结构规范，包括文件组织、模块划分原则",
    "testing": "测试规范，包括测试覆盖率要求、测试命名约定",
    "docs": "文档规范，包括注释风格、README 格式要求",
    "code-generation": "AI代码生成规范，包括生成代码的风格和要求",
    "logging": "日志规范，包括日志格式、级别和输出方式",
    "security": "安全规范，包括安全编码、敏感信息处理",
}
```

---

## 阶段 5: 去重检测

**目标**: 检测与已有标准的相似度，避免重复

### 相似度判断标准

1. **关键词相似度 > 70%**
   - 提取标准内容的关键词
   - 与已有标准比较
   - 使用 Jaccard 相似度或 AI 判断

2. **同分类下的标准**
   - 相同 tags 的标准更可能是重复
   - 例如：两个 `code-style` 标准可能描述同一规范

3. **核心概念一致**
   - AI 判断语义相似性

### 检测流程

```python
# 获取已有标准
existing_standards = project_get(project_id, group_name="standards")

# 对每个新标准进行检测
for new_std in extracted_standards:
    similar_items = []
    for existing in existing_standards["items"]:
        # AI 判断相似度
        if is_similar(new_std["content"], existing["content"]):
            similar_items.append(existing)

    if similar_items:
        # 标记为合并候选
        new_std["merge_candidates"] = similar_items
```

---

## 阶段 6: 冲突处理

**目标**: 处理多来源冲突和合并候选

### 场景 A: 多来源冲突

当不同来源提取的标准有冲突时：

```
示例冲突:
- CLAUDE.md: "使用 2 空格缩进"
- .editorconfig: "indent_size = 4"

处理方式:
1. 展示冲突信息给用户
2. 提示用户选择保留哪个
3. 或让用户输入合并后的版本
```

### 场景 B: 合并候选

当检测到相似标准时：

```
示例:
- 新标准: "变量命名使用 snake_case"
- 已有: "命名规范: 变量使用下划线分隔"

处理方式:
1. 展示相似标准给用户
2. 询问用户:
   - 更新已有标准
   - 跳过新标准
   - 保留两者
```

### 用户确认格式

```
## 发现相似标准

**已有标准**:
- [std_001] 命名规范: 变量使用下划线分隔 (tags: naming)

**新提取标准**:
- 变量命名使用 snake_case (tags: naming, code-style)

**相似度**: 高 (关键词重叠: 命名, 变量, 下划线)

请选择处理方式:
1. 更新已有标准 (合并内容)
2. 跳过新标准
3. 保留两者 (作为独立标准)
```

---

## 阶段 7: 批量添加

**目标**: 将确认的标准添加到 memory_mcp

### 添加流程

```python
for standard in confirmed_standards:
    # 如果是更新已有标准
    if standard.get("update_existing"):
        project_update(
            project_id="<项目ID>",
            group="standards",
            item_id=standard["existing_id"],
            content=standard["merged_content"],
            tags=standard["tags"]
        )
    else:
        # 添加新标准
        project_add(
            project_id="<项目ID>",
            group="standards",
            content=standard["content"],
            description=standard.get("description", ""),
            tags=",".join(standard["tags"])
        )
```

---

## 阶段 8: 输出报告

**目标**: 展示添加的标准信息

### 报告格式

```
## 标准初始化完成

**项目**: {项目名称}
**处理时间**: {时间戳}

### 新增标准 ({count} 条)
| ID | 内容 | 标签 |
|----|------|------|
| std_001 | 代码风格: 4空格缩进 | code-style |
| std_002 | 命名规范: snake_case | naming, code-style |

### 更新标准 ({count} 条)
| ID | 原内容 | 新内容 |
|----|--------|--------|
| std_003 | 变量命名 | 变量命名使用 snake_case |

### 跳过标准 ({count} 条)
- Git 提交规范 (与已有标准重复)

### 已注册标签
- code-style: 代码风格和格式化规范
- naming: 命名规范
- git: Git 相关规范

---
总计: 新增 {n} 条, 更新 {u} 条, 跳过 {s} 条
```

---

## 注意事项

1. **标签必须先注册**: 使用 `tag_register` 注册标签后才能使用
2. **标准内容限制**: content 限制 30 tokens，description 可详细
3. **相似度判断**: 优先让 AI 判断，避免误合并
4. **用户确认**: 冲突和合并必须用户确认
5. **增量添加**: 可多次运行，不会重复添加

---

## 使用示例

### 示例 1: 自动探索所有规范

```
用户: /memory-std

执行流程:
1. 确定项目 ID
2. 探索 CLAUDE.md → 提取 3 条标准
3. 探索 .editorconfig → 提取 2 条标准
4. 探索代码模式 → 提取 1 条命名规范
5. 去重检测 → 发现 1 条重复
6. 用户确认合并
7. 添加 5 条标准
8. 输出报告
```

### 示例 2: 探索指定类型规范

```
用户: /memory-std code-style

执行流程:
1. 确定项目 ID
2. 类型过滤 → 只探索 code-style 相关
3. 探索 .editorconfig → 提取缩进规则
4. 探索 pyproject.toml → 提取 black 配置
5. 去重检测 → 无重复
6. 添加 2 条 code-style 标准
7. 输出报告
```

### 示例 3: 添加类型化标准

```
用户: /memory-std code-style 4空格缩进

执行流程:
1. 确定项目 ID
2. 解析输入 → 类型: code-style, 内容: 4空格缩进
3. 检查标签 → code-style 已注册
4. 去重检测 → 无重复
5. 添加标准 (tags: code-style)
6. 输出报告
```

### 示例 4: 自定义类型（自动注册标签）

```
用户: /memory-std 代码生成规范 使用snake_case命名

执行流程:
1. 确定项目 ID
2. 解析输入 → 类型: 代码生成规范, 内容: 使用snake_case命名
3. 转换标签 → 代码生成规范 → code-generation
4. 自动注册标签 → tag_register("code-generation", "代码生成规范 (自动生成)")
5. 去重检测 → 无重复
6. 添加标准 (tags: code-generation)
7. 输出报告
```

### 示例 5: 向后兼容（直接输入标准）

```
用户: /memory-std 代码风格: 使用 4 空格缩进

执行流程:
1. 确定项目 ID
2. 解析输入 → 整体作为标准内容
3. 自动分类 → 识别为 code-style 类型
4. 去重检测 → 无重复
5. 添加标准 (tags: code-style)
6. 输出报告
```
