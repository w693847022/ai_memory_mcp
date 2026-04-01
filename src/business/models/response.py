"""统一的 API 响应格式类."""

import json
from dataclasses import dataclass
from typing import Optional, Any, Dict


@dataclass
class ApiResponse:
    """统一的 API 响应格式类"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        response: Dict[str, Any] = {"success": self.success}
        if self.data is not None:
            response["data"] = self.data
        if self.error is not None:
            response["error"] = self.error
        if self.message is not None:
            response["message"] = self.message
        return response

    def to_json(self, compact: bool = True) -> str:
        """转换为 JSON 字符串.

        Args:
            compact: 是否使用紧凑格式（无缩进），默认 True
        """
        if compact:
            return json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"))
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_result(cls, result: Dict[str, Any]) -> "ApiResponse":
        if result.get("success"):
            data = {k: v for k, v in result.items() if k not in ["success", "error", "message"]}
            return cls(success=True, data=data if data else None,
                      message=result.get("message", "操作成功"))
        return cls(success=False, error=result.get("error", "未知错误"))
