"""MCP 项目管理工具模块.

提供项目管理相关的 MCP 工具函数。
"""

from typing import Optional, Dict, List, Union

from ._shared import _get_client, _tool_response, _error_response, _parse_tags


# ===================
# Project Memory Tools
# ===================

def project_register(name: str, path: str = "", summary: str = "", tags: str = "") -> str:
    """注册一个新项目.

    Args:
        name: 项目名称
        path: 项目路径（可选）
        summary: 项目摘要（可选）
        tags: 项目标签，逗号分隔（可选）

    Returns:
        JSON 格式的注册结果
    """
    client = _get_client()
    result = client.register_project(name=name, path=path, summary=summary, tags=tags)
    if result.get("success"):
        data = result.get("data")
        return _tool_response(result, data if data else None)
    return _tool_response(result)


def project_rename(project_id: str, new_name: str) -> str:
    """重命名项目（修改 name 字段并重命名目录）.

    Args:
        project_id: 项目 UUID
        new_name: 新的项目名称

    Returns:
        JSON 格式的操作结果
    """
    client = _get_client()
    result = client.rename_project(project_id, new_name)
    data = {"old_name": result.get("old_name"), "new_name": result.get("new_name")} if result.get("success") else None
    return _tool_response(result, data)


def project_list(
    view_mode: str = "summary",
    page: int = 1,
    size: int = 0,
    name_pattern: str = "",
    include_archived: bool = False
) -> str:
    """列出所有项目.

    Args:
        view_mode: 视图模式 (可选): "summary"(精简，默认) 或 "detail"(完整)
        page: 页码 (可选): 从 1 开始，默认为 1
        size: 每页条数 (可选): 根据 view_mode 决定默认值
        name_pattern: 项目名称正则过滤 (可选): 正则表达式匹配项目名称，默认不过滤
        include_archived: 是否包含归档项目 (可选): 默认 false，传入 true 时显示归档项目

    Returns:
        JSON 格式的项目列表
    """
    from business.core.utils import validate_view_mode, validate_regex_pattern, resolve_default_size, paginate, apply_view_mode

    # 验证 view_mode 参数
    is_valid, error_msg = validate_view_mode(view_mode)
    if not is_valid:
        return _error_response(error_msg)

    # 验证 name_pattern 正则有效性
    name_regex, error_msg = validate_regex_pattern(name_pattern, "name_pattern")
    if error_msg:
        return _error_response(error_msg)

    # 根据 view_mode 设置 size 默认值
    size = resolve_default_size(size, view_mode)

    client = _get_client()
    result = client.project_list(
        view_mode=view_mode,
        page=page,
        size=size,
        name_pattern=name_pattern,
        include_archived=include_archived
    )

    if not result.get("success"):
        return _tool_response(result)

    data = result.get("data", {})
    projects = data.get("projects", [])
    total = data.get("total", 0)

    # name_pattern 过滤
    if name_regex:
        projects = [p for p in projects if name_regex.search(p.get("name", ""))]

    # 分页处理
    pr, err = paginate(projects, page, size)
    if err:
        return _error_response(err)
    assert pr is not None
    projects, pagination_meta, filtered_total = pr.items, pr.pagination_meta, pr.filtered_total

    # view_mode 字段过滤
    filtered_projects = apply_view_mode(projects, view_mode, ["id", "name", "summary", "tags", "status"])
    if view_mode == "summary":
        for p in filtered_projects:
            if p.get("status") is None:
                p["status"] = "active"

    response_data = {
        "total": total,
        "filtered_total": filtered_total,
        "projects": filtered_projects
    }

    if pagination_meta:
        response_data.update(pagination_meta)

    if name_pattern:
        response_data["filters"] = {"name_pattern": name_pattern}

    return _tool_response({"success": True}, response_data, f"共 {filtered_total} 个项目")


def project_groups_list(project_id: str) -> str:
    """列出项目的所有分组（内置组 + 自定义组）.

    Args:
        project_id: 项目ID

    Returns:
        JSON 格式的分组列表及统计信息
    """
    client = _get_client()
    result = client.list_groups(project_id)

    if not result.get("success"):
        return _tool_response(result)

    data = result.get("data", {})
    response_data = {
        "project_id": project_id,
        "groups": data.get("groups", [])
    }
    return _tool_response(result, response_data, "获取分组成功")


def project_tags_info(
    project_id: str,
    group_name: str = "",
    tag_name: str = "",
    unregistered_only: bool = False,
    page: int = 1,
    size: int = 0,
    view_mode: str = "summary",
    summary_pattern: str = "",
    tag_name_pattern: str = ""
) -> str:
    """查询标签信息（统一接口）.

    Args:
        project_id: 项目ID
        group_name: 分组名称 (可选)
        tag_name: 标签名称 (为空则返回所有标签)
        unregistered_only: 仅返回未注册标签
        page: 页码 (可选): 从 1 开始，默认为 1
        size: 每页条数 (可选): 根据 view_mode 决定默认值
        view_mode: 视图模式 (可选): "summary"(精简，默认) 或 "detail"(完整)
        summary_pattern: 摘要正则过滤 (可选)
        tag_name_pattern: 标签名正则过滤 (可选)

    Returns:
        JSON 格式的标签信息
    """
    from business.core.utils import validate_view_mode, validate_regex_pattern, resolve_default_size, apply_view_mode

    # 统一参数验证
    is_valid, error_msg = validate_view_mode(view_mode)
    if not is_valid:
        return _error_response(error_msg)

    summary_regex, error_msg = validate_regex_pattern(summary_pattern, "summary_pattern")
    if error_msg:
        return _error_response(error_msg)

    tag_name_regex, error_msg = validate_regex_pattern(tag_name_pattern, "tag_name_pattern")
    if error_msg:
        return _error_response(error_msg)

    size = resolve_default_size(size, view_mode)

    client = _get_client()
    result = client.project_tags_info(
        project_id=project_id,
        group_name=group_name,
        tag_name=tag_name,
        unregistered_only=unregistered_only,
        page=page,
        size=size,
        view_mode=view_mode,
        summary_pattern=summary_pattern,
        tag_name_pattern=tag_name_pattern
    )

    if not result.get("success"):
        return _tool_response(result)

    data = result.get("data", {})

    # 标签列表需要正则过滤
    if summary_regex or tag_name_regex:
        tags_list = data.get("tags", [])
        filtered = []
        for tag_item in tags_list:
            if summary_regex and not summary_regex.search(tag_item.get("summary", "")):
                continue
            if tag_name_regex and not tag_name_regex.search(tag_item.get("tag", "")):
                continue
            filtered.append(tag_item)
        data["tags"] = filtered
        data["filtered_total"] = len(filtered)

    return _tool_response(result, data, result.get("message", "操作成功"))


def project_add(
    project_id: str,
    group: str,
    content: str = "",
    summary: str = "",
    status: Optional[str] = None,
    severity: str = "medium",
    related: Union[str, Dict[str, List[str]], None] = "",
    tags: str = ""
) -> str:
    """添加项目条目（统一接口）.

    Args:
        project_id: 项目ID
        group: 分组类型
        content: 补充描述
        summary: 摘要（所有分组必填）
        status: 状态（仅 features/fixes 使用）
        severity: 严重程度（仅 fixes 使用，默认 "medium"）
        related: 关联条目
        tags: 标签列表，逗号分隔

    Returns:
        JSON 格式的操作结果
    """
    client = _get_client()
    result = client.project_add(
        project_id=project_id,
        group=group,
        content=content,
        summary=summary,
        status=status,
        severity=severity,
        related=related,
        tags=tags
    )

    if result.get("success"):
        data = result.get("data")
        return _tool_response(result, data)
    return _tool_response(result)


def project_update(
    project_id: str,
    group: str,
    item_id: str,
    content: Optional[str] = None,
    summary: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    related: Optional[Union[str, Dict[str, List[str]]]] = None,
    tags: Optional[str] = None
) -> str:
    """更新项目条目（统一接口）.

    Args:
        project_id: 项目ID
        group: 分组类型
        item_id: 条目ID
        content: 内容更新（可选）
        summary: 摘要更新（可选）
        status: 状态更新（可选）
        severity: 严重程度更新（仅 fixes）
        related: 关联条目更新（可选）
        tags: 标签更新（可选）

    Returns:
        JSON 格式的操作结果
    """
    client = _get_client()
    result = client.project_update(
        project_id=project_id,
        group=group,
        item_id=item_id,
        content=content,
        summary=summary,
        status=status,
        severity=severity,
        related=related,
        tags=tags
    )

    if result.get("success"):
        data = result.get("data")
        return _tool_response(result, data)
    return _tool_response(result)


def project_delete(
    project_id: str,
    group: str,
    item_id: str
) -> str:
    """删除项目条目（统一接口）.

    Args:
        project_id: 项目ID
        group: 分组类型
        item_id: 条目ID

    Returns:
        JSON 格式的操作结果
    """
    from business.core.groups import validate_group_name

    # 验证 group 有效性
    is_valid, error_msg = validate_group_name(group)
    if not is_valid:
        return _error_response(error_msg)

    if not item_id:
        return _error_response("item_id 参数不能为空")

    client = _get_client()
    result = client.project_delete(project_id=project_id, group=group, item_id=item_id)
    data = {"project_id": project_id, "group": group, "item_id": item_id, "deleted": True} if result.get("success") else None
    return _tool_response(result, data)


def project_remove(
    project_id: str,
    mode: str = "archive"
) -> str:
    """归档或永久删除项目（统一接口）.

    Args:
        project_id: 项目ID
        mode: 操作模式 - "archive"(归档，默认) 或 "delete"(永久删除)

    Returns:
        JSON 格式的操作结果
    """
    client = _get_client()
    result = client.remove_project(project_id=project_id, mode=mode)
    if result.get("success"):
        data = {"project_id": project_id, "mode": mode}
        return _tool_response(result, data, result.get("message", "操作成功"))
    return _tool_response(result)


def project_item_tag_manage(
    project_id: str,
    group_name: str,
    item_id: str,
    operation: str,
    tag: str = "",
    tags: str = ""
) -> str:
    """管理条目标签（统一接口）.

    Args:
        project_id: 项目ID
        group_name: 分组名称
        item_id: 条目ID
        operation: 操作类型 - "set"|"add"|"remove"
        tag: 单个标签 (operation="add"|"remove"时)
        tags: 标签列表逗号分隔 (operation="set"时)

    Returns:
        JSON 格式的操作结果
    """
    from business.core.groups import validate_group_name

    is_valid, error_msg = validate_group_name(group_name)
    if not is_valid:
        return _error_response(error_msg)

    client = _get_client()
    result = client.manage_item_tags(
        project_id=project_id,
        group_name=group_name,
        item_id=item_id,
        operation=operation,
        tag=tag,
        tags=tags
    )
    return _tool_response(result, result.get("data"))


def project_get(
    project_id: str,
    group_name: str = "",
    item_id: str = "",
    status: str = "",
    severity: str = "",
    tags: str = "",
    page: int = 1,
    size: int = 0,
    view_mode: str = "summary",
    summary_pattern: str = "",
    created_after: str = "",
    created_before: str = "",
    updated_after: str = "",
    updated_before: str = ""
) -> str:
    """获取项目信息或查询条目列表/详情.

    查询模式:
        1. 整个项目信息 - 不传 group_name
        2. 分组列表模式 - 传 group_name，不传 item_id (根据 view_mode 决定返回字段)
        3. 条目详情模式 - 传 group_name + item_id (含完整 content)

    Args:
        project_id: 项目ID
        group_name: 分组名称 (可选)
        item_id: 条目ID (可选): 查询单个条目时指定
        status: 状态过滤 (可选)
        severity: 严重程度过滤 (可选)
        tags: 标签过滤 (可选)
        page: 页码 (可选): 从 1 开始，默认为 1
        size: 每页条数 (可选): 根据 view_mode 决定默认值
        view_mode: 视图模式 (可选): "summary"(精简，默认) 或 "detail"(完整)
        summary_pattern: 摘要正则过滤 (可选)
        created_after: 创建时间起始 (可选): YYYY-MM-DD
        created_before: 创建时间截止 (可选): YYYY-MM-DD
        updated_after: 修改时间起始 (可选): YYYY-MM-DD
        updated_before: 修改时间截止 (可选): YYYY-MM-DD

    Returns:
        JSON 格式的项目信息、条目列表或单个条目详情
    """
    from business.core.utils import validate_view_mode, validate_regex_pattern, resolve_default_size, apply_view_mode
    from business.core.groups import validate_group_name, is_group_with_status

    # 验证 view_mode 参数
    is_valid, error_msg = validate_view_mode(view_mode)
    if not is_valid:
        return _error_response(error_msg)

    # 验证 summary_pattern 正则有效性
    summary_regex, error_msg = validate_regex_pattern(summary_pattern, "summary_pattern")
    if error_msg:
        return _error_response(error_msg)

    # 验证时间范围参数格式 (YYYY-MM-DD)
    from datetime import datetime
    for param_name, param_val in [
        ("created_after", created_after),
        ("created_before", created_before),
        ("updated_after", updated_after),
        ("updated_before", updated_before),
    ]:
        if param_val:
            try:
                datetime.strptime(param_val, "%Y-%m-%d")
            except ValueError:
                return _error_response(f"无效的日期格式: {param_val} (要求 YYYY-MM-DD)")

    # 根据 view_mode 设置 size 默认值
    size = resolve_default_size(size, view_mode)

    client = _get_client()
    result = client.project_get(
        project_id=project_id,
        group_name=group_name,
        item_id=item_id,
        status=status,
        severity=severity,
        tags=tags,
        page=page,
        size=size,
        view_mode=view_mode,
        summary_pattern=summary_pattern,
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before
    )

    if not result.get("success"):
        return _tool_response(result)

    data = result.get("data", {})

    # 如果指定了 group_name 但没有 item_id，需要额外过滤
    if group_name and not item_id:
        is_valid, error_msg = validate_group_name(group_name)
        if not is_valid:
            return _error_response(error_msg)

        items = data.get("items", [])

        # tags 过滤：OR 逻辑
        tag_list = _parse_tags(tags) if tags else []

        # 应用过滤条件
        if is_group_with_status(group_name):
            if status:
                items = [f for f in items if f.get("status") == status]
            if severity:
                items = [f for f in items if f.get("severity") == severity]

        if tag_list:
            items = [f for f in items if any(tag in f.get("tags", []) for tag in tag_list)]

        # summary 正则过滤 + 时间范围过滤
        if summary_regex or created_after or created_before or updated_after or updated_before:
            new_filtered = []
            for item in items:
                if summary_regex and not summary_regex.search(item.get("summary", "")):
                    continue
                created = (item.get("created_at") or "")[:10]
                if created_after and created < created_after:
                    continue
                if created_before and created > created_before:
                    continue
                updated = (item.get("updated_at") or "")[:10]
                if updated_after and (not updated or updated < updated_after):
                    continue
                if updated_before and (not updated or updated > updated_before):
                    continue
                new_filtered.append(item)
            items = new_filtered

        # 更新过滤后的数据
        data["items"] = items
        data["filtered_total"] = len(items)

    return _tool_response(result, data, result.get("message", "操作成功"))


def project_stats() -> str:
    """获取全局统计信息.

    Returns:
        JSON 格式的统计数据
    """
    client = _get_client()
    result = client.project_stats()
    if result.get("success"):
        data = result.get("data", {})
        return _tool_response(result, data, "获取统计成功")
    return _tool_response(result)
