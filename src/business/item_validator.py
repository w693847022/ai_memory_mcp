"""Item Validator Module - 条目验证逻辑.

提供条目字段验证功能，包括组名、状态、严重程度、内容长度、摘要长度、标签数量、关联参数等验证。
所有验证方法均为静态方法（无IO），get_all_configs 为异步实例方法。
"""

import json
from typing import Optional, List, Dict, Any, Tuple, Union

from src.models.group import (
    UnifiedGroupConfig,
    RESERVED_FIELDS,
)


class ItemValidator:
    """条目验证服务类."""

    def __init__(self, storage):
        self.storage = storage

    async def get_all_configs(self, project_id: str) -> Dict[str, UnifiedGroupConfig]:
        """从 _groups.json 加载全部组配置（内置+自定义合并后）.

        Args:
            project_id: 项目ID

        Returns:
            Dict[str, UnifiedGroupConfig] 组名到配置的映射
        """
        group_configs = await self.storage.get_group_configs(project_id)
        return group_configs.get("groups", {})

    @staticmethod
    def is_reserved_field(field_name: str) -> bool:
        """检测字段名是否为系统保留字段."""
        return field_name in RESERVED_FIELDS

    @staticmethod
    def validate_group_name(
        group_name: str,
        all_configs: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """验证组名是否合法.

        Args:
            group_name: 组名称
            all_configs: 所有组配置（从存储加载）

        Returns:
            (是否有效, 错误信息)
        """
        if group_name in RESERVED_FIELDS:
            return False, f"组名 '{group_name}' 与系统配置字段冲突"

        if group_name in all_configs:
            return True, None

        valid_groups = ", ".join(sorted(all_configs.keys()))
        return False, f"无效的分组类型: {group_name} (支持: {valid_groups})"

    @staticmethod
    def validate_status(
        status: str,
        config: Optional[UnifiedGroupConfig] = None,
    ) -> Tuple[bool, Optional[str]]:
        """验证状态值是否合法."""
        if config is None:
            config = UnifiedGroupConfig()

        if not config.enable_status:
            return True, None

        status_values = config.status_values if config.status_values else ["pending", "in_progress", "completed"]
        if status in status_values:
            return True, None
        valid_values = ", ".join(status_values)
        return False, f"无效的 status 值: {status} (有效值: {valid_values})"

    @staticmethod
    def validate_severity(
        severity: str,
        config: Optional[UnifiedGroupConfig] = None,
    ) -> Tuple[bool, Optional[str]]:
        """验证严重程度值是否合法."""
        if config is None:
            config = UnifiedGroupConfig(enable_severity=True)

        if not config.enable_severity:
            return True, None

        severity_values = config.severity_values if config.severity_values else ["critical", "high", "medium", "low"]
        if severity in severity_values:
            return True, None
        return False, f"无效的 severity 值: {severity} (有效值: {', '.join(severity_values)})"

    @staticmethod
    def validate_content_length(
        content: str,
        config: Optional[UnifiedGroupConfig] = None,
        min_bytes: Optional[int] = None,
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """验证内容长度（字节验证）."""
        content_bytes = len(content.encode('utf-8'))
        effective_min_bytes = min_bytes or 1

        if config is not None:
            max_bytes = config.content_max_bytes
            if content_bytes < effective_min_bytes:
                return False, f"内容过短：至少需要 {effective_min_bytes} 字节", content_bytes
            if content_bytes > max_bytes:
                return False, f"内容过长：{content_bytes} 字节，最大允许 {max_bytes} 字节", content_bytes
            return True, None, content_bytes

        return True, None, content_bytes

    @staticmethod
    def validate_summary_length(
        summary: str,
        config: Optional[UnifiedGroupConfig] = None,
        min_bytes: Optional[int] = None,
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """验证摘要长度（字节验证）."""
        summary_bytes = len(summary.encode('utf-8'))
        effective_min_bytes = min_bytes or 1

        if config is not None:
            max_bytes = config.summary_max_bytes
            if summary_bytes < effective_min_bytes:
                return False, f"摘要过短：至少需要 {effective_min_bytes} 字节", summary_bytes
            if summary_bytes > max_bytes:
                return False, f"摘要过长：{summary_bytes} 字节，最大允许 {max_bytes} 字节", summary_bytes
            return True, None, summary_bytes

        return True, None, summary_bytes

    @staticmethod
    def validate_related(
        related: Optional[Union[str, Dict[str, List[str]]]],
        group_name: str,
        config: Optional[UnifiedGroupConfig] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, List[str]]]]:
        """解析并验证 related 参数."""
        if related is None or related == "":
            return True, "", None

        if config is None:
            return True, "", None

        if not config.allow_related:
            return False, f"分组 '{group_name}' 不支持关联功能", None

        allowed_related_to = config.allowed_related_to
        if not allowed_related_to:
            return True, "", None

        if isinstance(related, dict):
            related_dict = related
        else:
            try:
                related_dict = json.loads(related)
            except json.JSONDecodeError:
                return False, "related 参数 JSON 格式无效", None

        for rel_group in related_dict.keys():
            if rel_group not in allowed_related_to:
                return False, f"分组 '{group_name}' 只能关联 {', '.join(allowed_related_to)}，不能关联 '{rel_group}'", None

        return True, "", related_dict

    @staticmethod
    def validate_tags_count(
        tag_list: List[str],
        config: Optional[UnifiedGroupConfig] = None,
    ) -> Tuple[bool, Optional[str]]:
        """验证标签数量是否超过配置限制.

        Args:
            tag_list: 标签列表
            config: 组配置对象

        Returns:
            (is_valid, error_message) 二元组
        """
        if not tag_list:
            return True, None

        if config is None:
            config = UnifiedGroupConfig()

        count = len(tag_list)
        max_allowed = config.max_tags

        if count > max_allowed:
            return False, f"标签数量超限：当前 {count} 个，最大允许 {max_allowed} 个"

        return True, None
