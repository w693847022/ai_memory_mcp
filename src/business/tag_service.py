"""Tag Service Module - 标签管理业务逻辑服务.

提供标签注册、更新、删除、合并等业务逻辑。
"""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any


class TagService:
    """标签管理业务逻辑服务类."""

    def __init__(self, storage):
        """初始化标签服务.

        Args:
            storage: 存储层实例（需要实现 _load_project, _save_project 方法）
        """
        self.storage = storage

    def _validate_tag_name(self, tag_name: str) -> bool:
        """验证标签名称格式.

        Args:
            tag_name: 标签名称

        Returns:
            是否有效
        """
        pattern = r'^[a-zA-Z0-9_-]{1,30}$'
        return bool(re.match(pattern, tag_name))

    def _validate_description(self, description: str) -> bool:
        """验证描述长度（3-200字符）.

        Args:
            description: 描述文本

        Returns:
            是否有效
        """
        return 3 <= len(description) <= 200

    def _check_tags_registered(self, project_data: Dict[str, Any], tags: List[str]) -> Dict[str, Any]:
        """检查标签是否已注册.

        Args:
            project_data: 项目数据
            tags: 标签列表

        Returns:
            检查结果
        """
        tag_registry = project_data.get("tag_registry", {})
        unregistered = [tag for tag in tags if tag not in tag_registry]

        if unregistered:
            return {
                "success": False,
                "error": f"标签未注册：{', '.join(unregistered)}。\n建议先使用 project_tags_info 查询已注册标签，确认无合适标签后再使用 tag_register 注册新标签",
                "unregistered_tags": unregistered
            }

        return {"success": True}

    def register_tag(
        self,
        project_id: str,
        tag_name: str,
        summary: str,
        aliases: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """注册新标签到项目标签库.

        Args:
            project_id: 项目ID
            tag_name: 标签名称
            summary: 标签语义摘要（10-200字符）
            aliases: 别名列表（可选）

        Returns:
            操作结果
        """
        # 验证标签名称
        if not self._validate_tag_name(tag_name):
            return {
                "success": False,
                "error": f"标签名称格式无效：'{tag_name}'。只允许英文字母、数字、下划线、连字符，长度1-30字符"
            }

        # 验证摘要长度
        if not self._validate_description(summary):
            return {
                "success": False,
                "error": f"摘要长度无效：需要3-200字符，当前为 {len(summary)} 字符"
            }

        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        tag_registry = project_data.get("tag_registry", {})

        # 检查标签是否已注册
        if tag_name in tag_registry:
            return {
                "success": False,
                "error": f"标签 '{tag_name}' 已经注册",
                "tag_info": tag_registry[tag_name]
            }

        # 注册新标签
        tag_registry[tag_name] = {
            "summary": summary,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "aliases": aliases or []
        }

        project_data["tag_registry"] = tag_registry
        project_data["info"]["updated_at"] = datetime.now().isoformat()

        if self.storage._save_project(project_id, project_data):
            return {
                "success": True,
                "message": f"标签 '{tag_name}' 已成功注册",
                "tag_name": tag_name,
                "tag_info": tag_registry[tag_name]
            }

        return {"success": False, "error": "保存数据失败"}

    def update_tag(
        self,
        project_id: str,
        tag_name: str,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """更新已注册标签的语义信息.

        Args:
            project_id: 项目ID
            tag_name: 标签名称
            summary: 新的摘要（可选）

        Returns:
            操作结果
        """
        if summary is not None and not self._validate_description(summary):
            return {
                "success": False,
                "error": f"摘要长度无效：需要3-200字符，当前为 {len(summary)} 字符"
            }

        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        tag_registry = project_data.get("tag_registry", {})

        if tag_name not in tag_registry:
            return {
                "success": False,
                "error": f"标签 '{tag_name}' 未注册"
            }

        # 更新摘要
        if summary is not None:
            tag_registry[tag_name]["summary"] = summary

        project_data["tag_registry"] = tag_registry
        project_data["info"]["updated_at"] = datetime.now().isoformat()

        if self.storage._save_project(project_id, project_data):
            return {
                "success": True,
                "message": f"标签 '{tag_name}' 已更新",
                "tag_info": tag_registry[tag_name]
            }

        return {"success": False, "error": "保存数据失败"}

    def delete_tag(
        self,
        project_id: str,
        tag_name: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """删除标签注册.

        Args:
            project_id: 项目ID
            tag_name: 标签名称
            force: 是否强制删除（即使标签正在使用）

        Returns:
            操作结果
        """
        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        tag_registry = project_data.get("tag_registry", {})

        if tag_name not in tag_registry:
            return {
                "success": False,
                "error": f"标签 '{tag_name}' 未注册"
            }

        # 检查标签是否正在使用
        usage_count = tag_registry[tag_name].get("usage_count", 0)

        if usage_count > 0 and not force:
            return {
                "success": False,
                "error": f"标签 '{tag_name}' 正在被 {usage_count} 个条目使用，请使用 force=True 强制删除"
            }

        # 删除标签
        del tag_registry[tag_name]

        project_data["tag_registry"] = tag_registry
        project_data["info"]["updated_at"] = datetime.now().isoformat()

        if self.storage._save_project(project_id, project_data):
            return {
                "success": True,
                "message": f"标签 '{tag_name}' 已删除"
            }

        return {"success": False, "error": "保存数据失败"}

    def merge_tags(
        self,
        project_id: str,
        old_tag: str,
        new_tag: str
    ) -> Dict[str, Any]:
        """合并标签：将所有 old_tag 的引用迁移到 new_tag.

        Args:
            project_id: 项目ID
            old_tag: 旧标签名称（将被删除）
            new_tag: 新标签名称（合并目标）

        Returns:
            操作结果
        """
        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        tag_registry = project_data.get("tag_registry", {})

        # 检查两个标签都已注册
        if old_tag not in tag_registry:
            return {
                "success": False,
                "error": f"旧标签 '{old_tag}' 未注册"
            }

        if new_tag not in tag_registry:
            return {
                "success": False,
                "error": f"新标签 '{new_tag}' 未注册"
            }

        if old_tag == new_tag:
            return {
                "success": False,
                "error": "旧标签和新标签不能相同"
            }

        # 统计需要迁移的条目数量
        migrated_count = 0

        # 获取所有组名称
        from business.core.groups import get_all_groups
        all_groups = get_all_groups()

        # 在所有分组中迁移标签
        for group_name in all_groups:
            items = project_data.get(group_name, [])
            for item in items:
                tags = item.get("tags", [])
                if old_tag in tags:
                    tags.remove(old_tag)
                    if new_tag not in tags:
                        tags.append(new_tag)
                    item["tags"] = tags
                    migrated_count += 1

        # 更新使用计数
        old_usage = tag_registry[old_tag].get("usage_count", 0)
        new_usage = tag_registry[new_tag].get("usage_count", 0)
        tag_registry[new_tag]["usage_count"] = new_usage + old_usage

        # 删除旧标签
        del tag_registry[old_tag]

        project_data["tag_registry"] = tag_registry
        project_data["info"]["updated_at"] = datetime.now().isoformat()

        if self.storage._save_project(project_id, project_data):
            return {
                "success": True,
                "message": f"已将标签 '{old_tag}' 合并到 '{new_tag}'，迁移了 {migrated_count} 个条目",
                "migrated_count": migrated_count
            }

        return {"success": False, "error": "保存数据失败"}

    def list_all_registered_tags(self, project_id: str) -> Dict[str, Any]:
        """列出项目中所有已注册的标签.

        Args:
            project_id: 项目ID

        Returns:
            所有已注册标签的列表
        """
        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        tag_registry = project_data.get("tag_registry", {})

        from business.core.groups import get_all_groups
        groups = get_all_groups()

        # 构建标签列表
        tags_list = []
        for tag_name, tag_info in tag_registry.items():
            # 统计该标签在哪些分组中被使用
            tag_groups = []
            group_counts = {}
            for group in groups:
                items = project_data.get(group, [])
                count = sum(1 for item in items if tag_name in item.get("tags", []))
                if count > 0:
                    tag_groups.append(group)
                    group_counts[group] = count

            tags_list.append({
                "tag": tag_name,
                "summary": tag_info.get("summary", ""),
                "usage_count": tag_info.get("usage_count", 0),
                "created_at": tag_info.get("created_at", ""),
                "aliases": tag_info.get("aliases", []),
                "groups": tag_groups,
                "group_counts": group_counts
            })

        # 按注册时间排序（最新的在前）
        tags_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return {
            "success": True,
            "project_id": project_id,
            "tags": tags_list,
            "total_tags": len(tags_list)
        }

    def list_group_tags(
        self,
        project_id: str,
        group_name: str
    ) -> Dict[str, Any]:
        """列出指定分组下的所有标签及使用次数.

        Args:
            project_id: 项目ID
            group_name: 分组名称

        Returns:
            标签列表及每个标签的条目数量
        """
        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        from business.core.groups import get_all_groups
        if group_name not in get_all_groups():
            return {"success": False, "error": f"分组 '{group_name}' 不存在"}

        # 从 tag_registry 获取所有注册标签
        tag_registry = project_data.get("tag_registry", {})
        items = project_data.get(group_name, [])

        # 统计每个注册标签的使用次数
        tag_counts = {}
        for tag in tag_registry.keys():
            count = sum(1 for item in items if tag in item.get("tags", []))
            if count > 0:
                tag_counts[tag] = count

        # 按使用次数排序并包含语义信息
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        tags_list = []
        for tag, count in sorted_tags:
            tag_info = tag_registry.get(tag, {})
            tags_list.append({
                "tag": tag,
                "count": count,
                "summary": tag_info.get("summary", "未注册"),
                "usage_count": tag_info.get("usage_count", 0),
                "created_at": tag_info.get("created_at", ""),
                "is_registered": tag in tag_registry
            })

        return {
            "success": True,
            "project_id": project_id,
            "group": group_name,
            "tags": tags_list,
            "total_tags": len(tags_list)
        }

    def list_unregistered_tags(
        self,
        project_id: str,
        group_name: str
    ) -> Dict[str, Any]:
        """列出指定分组下所有未注册的标签.

        Args:
            project_id: 项目ID
            group_name: 分组名称

        Returns:
            未注册标签列表
        """
        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        from business.core.groups import get_all_groups
        if group_name not in get_all_groups():
            return {"success": False, "error": f"分组 '{group_name}' 不存在"}

        # 获取所有使用的标签
        used_tags = set()
        items = project_data.get(group_name, [])

        for item in items:
            item_tags = item.get("tags", [])
            used_tags.update(item_tags)

        # 获取已注册的标签
        tag_registry = project_data.get("tag_registry", {})

        # 找出未注册的标签
        unregistered_tags = used_tags - set(tag_registry.keys())

        # 统计每个未注册标签的使用次数
        unregistered_tag_counts = {}
        for tag in unregistered_tags:
            count = sum(1 for item in items if tag in item.get("tags", []))
            unregistered_tag_counts[tag] = count

        # 按使用次数排序
        sorted_tags = sorted(unregistered_tag_counts.items(), key=lambda x: x[1], reverse=True)

        tags_list = []
        for tag, count in sorted_tags:
            tags_list.append({
                "tag": tag,
                "count": count,
                "suggestion": "建议使用 tag_register 注册此标签"
            })

        return {
            "success": True,
            "project_id": project_id,
            "group": group_name,
            "tags": tags_list,
            "total_tags": len(tags_list)
        }

    def query_by_tag(
        self,
        project_id: str,
        group_name: str,
        tag: str
    ) -> Dict[str, Any]:
        """查询指定分组下某标签的所有条目.

        Args:
            project_id: 项目ID
            group_name: 分组名称
            tag: 标签名称

        Returns:
            该标签下的所有条目列表
        """
        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        from business.core.groups import get_all_groups
        if group_name not in get_all_groups():
            return {"success": False, "error": f"分组 '{group_name}' 不存在"}

        items = project_data.get(group_name, [])
        matched_items = []

        for item in items:
            item_tags = item.get("tags", [])
            if tag in item_tags:
                matched_items.append(item)

        # 获取标签注册信息
        tag_registry = project_data.get("tag_registry", {})
        tag_info = tag_registry.get(tag, {})
        is_registered = tag in tag_registry

        return {
            "success": True,
            "project_id": project_id,
            "group": group_name,
            "tag": tag,
            "total": len(matched_items),
            "items": matched_items,
            "tag_info": {
                "summary": tag_info.get("summary", "未注册"),
                "usage_count": tag_info.get("usage_count", 0),
                "created_at": tag_info.get("created_at", ""),
                "is_registered": is_registered
            } if is_registered else None
        }

    def add_item_tag(
        self,
        project_id: str,
        group_name: str,
        item_id: str,
        tag: str
    ) -> Dict[str, Any]:
        """为条目添加单个标签.

        Args:
            project_id: 项目ID
            group_name: 分组名称
            item_id: 条目ID
            tag: 要添加的标签

        Returns:
            操作结果
        """
        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        from business.core.groups import get_all_groups
        if group_name not in get_all_groups():
            return {"success": False, "error": f"分组 '{group_name}' 不存在"}

        # 强制注册检查：标签必须先注册才能使用
        tag_registry = project_data.get("tag_registry", {})
        if tag not in tag_registry:
            return {
                "success": False,
                "error": f"标签 '{tag}' 未注册，请先使用 tag_register 注册该标签"
            }

        items = project_data.get(group_name, [])
        item_index = None

        for i, item in enumerate(items):
            if item.get("id") == item_id:
                item_index = i
                break

        if item_index is None:
            return {"success": False, "error": f"条目ID '{item_id}' 不存在"}

        current_tags = items[item_index].get("tags", [])
        if tag not in current_tags:
            current_tags.append(tag)
            items[item_index]["tags"] = current_tags

            # 更新使用计数
            tag_registry[tag]["usage_count"] = tag_registry[tag].get("usage_count", 0) + 1
            project_data["tag_registry"] = tag_registry

            project_data["info"]["updated_at"] = datetime.now().isoformat()

            if self.storage._save_project(project_id, project_data):
                return {
                    "success": True,
                    "message": f"已为条目 '{item_id}' 添加标签 '{tag}'",
                    "tags": current_tags
                }
            return {"success": False, "error": "保存数据失败"}

        return {"success": True, "message": f"标签 '{tag}' 已存在", "tags": current_tags}

    def remove_item_tag(
        self,
        project_id: str,
        group_name: str,
        item_id: str,
        tag: str
    ) -> Dict[str, Any]:
        """从条目移除单个标签.

        Args:
            project_id: 项目ID
            group_name: 分组名称
            item_id: 条目ID
            tag: 要移除的标签

        Returns:
            操作结果
        """
        project_data = self.storage._load_project(project_id)
        if project_data is None:
            return {"success": False, "error": f"项目 '{project_id}' 不存在"}

        from business.core.groups import get_all_groups
        if group_name not in get_all_groups():
            return {"success": False, "error": f"分组 '{group_name}' 不存在"}

        items = project_data.get(group_name, [])
        item_index = None

        for i, item in enumerate(items):
            if item.get("id") == item_id:
                item_index = i
                break

        if item_index is None:
            return {"success": False, "error": f"条目ID '{item_id}' 不存在"}

        current_tags = items[item_index].get("tags", [])
        if tag in current_tags:
            current_tags.remove(tag)
            items[item_index]["tags"] = current_tags

            # 更新使用计数
            tag_registry = project_data.get("tag_registry", {})
            if tag in tag_registry:
                current_count = tag_registry[tag].get("usage_count", 0)
                tag_registry[tag]["usage_count"] = max(0, current_count - 1)
                project_data["tag_registry"] = tag_registry

            project_data["info"]["updated_at"] = datetime.now().isoformat()

            if self.storage._save_project(project_id, project_data):
                return {
                    "success": True,
                    "message": f"已从条目 '{item_id}' 移除标签 '{tag}'",
                    "tags": current_tags
                }
            return {"success": False, "error": "保存数据失败"}

        return {"success": True, "message": f"标签 '{tag}' 不存在", "tags": current_tags}
