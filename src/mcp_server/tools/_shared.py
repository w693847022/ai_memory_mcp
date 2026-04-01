"""MCP 工具共享函数模块.

提供工具函数、共用导入和响应构建函数。
"""

from typing import Optional

# 导入 HTTP 客户端
from clients.business_client import get_business_client, BusinessApiClient

# 获取全局 HTTP 客户端
_business_client: Optional[BusinessApiClient] = None


def _get_client() -> BusinessApiClient:
    """获取或创建 business API 客户端."""
    global _business_client
    if _business_client is None:
        _business_client = get_business_client()
    return _business_client


# ===================
# Helper Functions
# ===================

def _parse_tags(tags_str: str) -> list:
    """解析标签字符串为列表."""
    if not tags_str:
        return []
    return [t.strip() for t in tags_str.split(",") if t.strip()]


def _tool_response(result, success_data=None, success_message=None):
    """构建工具响应."""
    from business.models.response import ApiResponse
    if result.get("success"):
        msg = success_message or result.get("message", "操作成功")
        return ApiResponse(success=True, data=success_data, message=msg).to_json()
    return ApiResponse(success=False, error=result.get("error", "未知错误")).to_json()


def _error_response(error):
    """构建错误响应."""
    from business.models.response import ApiResponse
    return ApiResponse(success=False, error=error).to_json()
