"""使用指南构建模块."""


def _build_chinese_guidelines() -> dict:
    """构建中文使用指南.

    Returns:
        中文指南字典
    """
    return {
        "version": "1.1",
        "last_updated": "2026-03-22",
        "language": "zh",
        "guidelines": {
            "project_naming": {
                "title": "项目名称确定规范",
                "priority": "highest",
                "workflow": [
                    "1. 优先查找项目文档（CLAUDE.md, README.md）",
                    "2. 查找 package.json, pyproject.toml 等配置文件",
                    "3. 向用户询问项目名称",
                    "4. 确定后记录到项目文档中"
                ],
                "examples": [
                    "从 README.md 提取: '电商平台' → 'E-commerce Platform'",
                    "从 package.json: 'my-app' → 'My App'",
                    "用户确认: '我的项目叫 Project X'"
                ]
            },
            "groups": {
                "title": "分组说明",
                "description": "项目记忆分为4个分组，用于不同类型的内容管理",
                "groups_list": [
                    {
                        "name": "features",
                        "alias": "功能, feat",
                        "description": "功能列表 - 记录功能需求、实现进度等",
                        "use_case": "实现新功能前记录"
                    },
                    {
                        "name": "notes",
                        "alias": "笔记, note",
                        "description": "开发笔记 - 记录技术决策、调试过程、经验总结等",
                        "use_case": "技术决策/调试/经验总结时记录"
                    },
                    {
                        "name": "fixes",
                        "alias": "修复, fix",
                        "description": "Bug修复 - 记录Bug修复过程和结果",
                        "use_case": "修复bug时记录"
                    },
                    {
                        "name": "standards",
                        "alias": "规范, 标准, standard",
                        "description": "项目规范 - 记录开发规范、最佳实践、代码风格等文档性内容",
                        "use_case": "确定项目规范时记录"
                    }
                ]
            },
            "tag_standards": {
                "title": "推荐Tag标准名称",
                "standard_tags": {
                    "standard": "规范、标准、最佳实践",
                    "urgent": "紧急、高优先级",
                    "bug": "Bug相关",
                    "feature": "新功能",
                    "refactor": "重构",
                    "docs": "文档",
                    "test": "测试",
                    "api": "API相关",
                    "frontend": "前端",
                    "backend": "后端",
                    "database": "数据库",
                    "security": "安全",
                    "performance": "性能优化"
                },
                "tag_limits": {
                    "max_per_item": 5,
                    "recommendation": "每条记录的tag数量最好不超过5个"
                }
            },
            "memory_workflow": {
                "title": "记忆工作流",
                "description": "统一的使用流程，包含查询、记录和维护",
                "query_flow": [
                    "步骤0: 获取项目列表确定 project_id → project_list",
                    "步骤1: 查看分组概览 → project_groups_list(project_id) → 了解features/notes/fixes/standards分组",
                    "步骤2: 查询标签信息 → project_tags_info(project_id) → 查看已注册标签",
                    "步骤3: 按标签查询 → project_get(project_id, group_name, tags='tag1,tag2') → 服务端过滤获取列表",
                    "步骤4: 查询详情 → project_get(project_id, group_name, item_id) → 获取具体条目详情"
                ],
                "query_tips": [
                    "标签支持 OR 逻辑: tags='api,backend' 匹配任一标签",
                    "可组合过滤: project_get(project_id, group_name, status='pending', tags='urgent')",
                    "❌ 避免全量获取后手动过滤，应使用 tags 参数服务端过滤"
                ],
                "recording_guide": {
                    "when": {
                        "features": "实现新功能前记录",
                        "notes": "技术决策/调试/经验总结时记录",
                        "fixes": "修复bug时记录",
                        "standards": "确定项目规范时记录"
                    },
                    "tag_registration": "新标签必须先注册: tag_register(project_id, tag_name, description, 10-50字描述)",
                    "content": "语言简练，关键信息为主",
                    "tags": "1-5个，必须先注册"
                },
                "cleanup": [
                    "1. 查看所有标签: project_tags_info(project_id)",
                    "2. 合并重复标签: tag_merge(project_id, old_tag, new_tag)",
                    "3. 删除未使用标签: tag_delete(project_id, tag_name, force)",
                    "4. 检查关联条目"
                ]
            },
            "best_practices": [
                "使用英文标签，便于国际化",
                "标签命名遵循 '小写+短词' 原则",
                "避免过度标签化（每条≤5个）",
                "查询时优先使用 tags 参数服务端过滤，而非全量获取后手动筛选",
                "定期整理标签，移除不再使用的"
            ]
        }
    }


def _build_english_guidelines() -> dict:
    """Build English usage guidelines.

    Returns:
        English guidelines dictionary
    """
    return {
        "version": "1.1",
        "last_updated": "2026-03-22",
        "language": "en",
        "guidelines": {
            "project_naming": {
                "title": "Project Naming Convention",
                "priority": "highest",
                "workflow": [
                    "1. Check project documentation (CLAUDE.md, README.md)",
                    "2. Check package.json, pyproject.toml, or other config files",
                    "3. Ask user for project name",
                    "4. Record in project documentation"
                ],
                "examples": [
                    "From README.md: '电商平台' → 'E-commerce Platform'",
                    "From package.json: 'my-app' → 'My App'",
                    "User confirms: 'My project is Project X'"
                ]
            },
            "groups": {
                "title": "Groups Description",
                "description": "Project memory is divided into 4 groups for different types of content",
                "groups_list": [
                    {
                        "name": "features",
                        "alias": "功能, feat",
                        "description": "Feature list - Record feature requirements and progress",
                        "use_case": "Record before implementing new features"
                    },
                    {
                        "name": "notes",
                        "alias": "笔记, note",
                        "description": "Development notes - Record technical decisions, debugging process, experience summary",
                        "use_case": "Record for technical decisions/debugging/experience"
                    },
                    {
                        "name": "fixes",
                        "alias": "修复, fix",
                        "description": "Bug fixes - Record bug fix process and results",
                        "use_case": "Record when fixing bugs"
                    },
                    {
                        "name": "standards",
                        "alias": "规范, 标准, standard",
                        "description": "Project standards - Record development standards, best practices, code style",
                        "use_case": "Record when establishing project standards"
                    }
                ]
            },
            "tag_standards": {
                "title": "Recommended Standard Tag Names",
                "standard_tags": {
                    "standard": "Standards, conventions, best practices",
                    "urgent": "Urgent, high priority",
                    "bug": "Bug related",
                    "feature": "New feature",
                    "refactor": "Refactoring",
                    "docs": "Documentation",
                    "test": "Testing",
                    "api": "API related",
                    "frontend": "Frontend",
                    "backend": "Backend",
                    "database": "Database",
                    "security": "Security",
                    "performance": "Performance optimization"
                },
                "tag_limits": {
                    "max_per_item": 5,
                    "recommendation": "Best to keep tags per item ≤ 5"
                }
            },
            "memory_workflow": {
                "title": "Memory Workflow",
                "description": "Unified workflow covering query, recording, and maintenance",
                "query_flow": [
                    "Step 0: Get project list to identify project_id → project_list",
                    "Step 1: View group overview → project_groups_list(project_id) → understand features/notes/fixes/standards groups",
                    "Step 2: Query tag info → project_tags_info(project_id) → view registered tags",
                    "Step 3: Query by tags → project_get(project_id, group_name, tags='tag1,tag2') → server-side filtered list",
                    "Step 4: Query details → project_get(project_id, group_name, item_id) → get specific item details"
                ],
                "query_tips": [
                    "Tags use OR logic: tags='api,backend' matches any tag",
                    "Composable filters: project_get(project_id, group_name, status='pending', tags='urgent')",
                    "❌ Avoid fetching full data then filtering manually; use tags parameter for server-side filtering"
                ],
                "recording_guide": {
                    "when": {
                        "features": "Record before implementing new features",
                        "notes": "Record for technical decisions/debugging/experience",
                        "fixes": "Record when fixing bugs",
                        "standards": "Record when establishing project standards"
                    },
                    "tag_registration": "New tags must be registered first: tag_register(project_id, tag_name, description, 10-50 char description)",
                    "content": "Keep it concise, focus on key information",
                    "tags": "1-5 tags, must register first"
                },
                "cleanup": [
                    "1. View all tags: project_tags_info(project_id)",
                    "2. Merge duplicate tags: tag_merge(project_id, old_tag, new_tag)",
                    "3. Delete unused tags: tag_delete(project_id, tag_name, force)",
                    "4. Check related items"
                ]
            },
            "best_practices": [
                "Use English tags for internationalization",
                "Follow 'lowercase+short-word' naming convention",
                "Avoid over-tagging (≤5 per item)",
                "Use tags parameter for server-side filtering instead of fetching full data",
                "Regularly organize tags and remove unused ones"
            ]
        }
    }


def _build_guidelines_content(lang: str) -> dict:
    """根据语言构建指南内容.

    Args:
        lang: 语言选择 (zh/en)

    Returns:
        指南内容字典
    """
    if lang.lower() == "en":
        return _build_english_guidelines()
    return _build_chinese_guidelines()
