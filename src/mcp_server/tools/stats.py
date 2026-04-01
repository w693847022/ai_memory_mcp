"""MCP 统计工具模块.

提供统计相关的 MCP 工具函数。
"""

from ._shared import _get_client, _tool_response


def stats_summary(
    type: str = "",
    tool_name: str = "",
    project_id: str = "",
    date: str = ""
) -> str:
    """获取统计摘要（统一接口）.

    Args:
        type: 统计类型 - "tool"|"project"|"client"|"ip"|"daily"|"full"|""(所有)
        tool_name: 工具名称 (type="tool"时)
        project_id: 项目ID (type="project"时)
        date: 日期 YYYY-MM-DD (type="daily"时)

    Returns:
        JSON 格式的统计摘要
    """
    client = _get_client()
    result = client.stats_summary(
        type=type,
        tool_name=tool_name,
        project_id=project_id,
        date=date
    )
    return _tool_response(result, result.get("data"))


def stats_cleanup(retention_days: int = 30) -> str:
    """手动清理过期统计数据.

    Args:
        retention_days: 保留天数（默认30天），超过此天数的数据将被清理

    Returns:
        JSON 格式的清理结果摘要
    """
    client = _get_client()
    result = client.stats_cleanup(retention_days=retention_days)
    return _tool_response(result, result.get("data"))
