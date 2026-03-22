#!/usr/bin/env python3
"""测试 MCP 工具函数返回值是否为有效的 JSON 格式。"""

import json
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import ApiResponse


def test_api_response():
    """测试 ApiResponse 类的基本功能。"""
    print("=== 测试 ApiResponse 类 ===")

    # 测试成功响应
    response = ApiResponse(success=True, data={"key": "value"}, message="操作成功")
    result = json.loads(response.to_json())
    assert result["success"] == True
    assert result["data"]["key"] == "value"
    assert result["message"] == "操作成功"
    print("✓ 成功响应测试通过")

    # 测试失败响应
    response = ApiResponse(success=False, error="操作失败")
    result = json.loads(response.to_json())
    assert result["success"] == False
    assert result["error"] == "操作失败"
    print("✓ 失败响应测试通过")

    # 测试 from_result 方法
    result_dict = {"success": True, "project_id": "test_project", "message": "注册成功"}
    response = ApiResponse.from_result(result_dict)
    result = json.loads(response.to_json())
    assert result["success"] == True
    assert result["data"]["project_id"] == "test_project"
    print("✓ from_result 测试通过")

    print("")


def test_json_parsing():
    """测试返回的 JSON 字符串可以被正确解析。"""
    print("=== 测试 JSON 解析 ===")

    # 测试各种数据类型的序列化
    test_cases = [
        {
            "success": True,
            "data": {
                "string": "测试",
                "number": 123,
                "float": 123.45,
                "bool": True,
                "null": None,
                "list": [1, 2, 3],
                "dict": {"nested": "value"}
            },
            "message": "测试消息"
        },
        {
            "success": False,
            "error": "错误消息"
        }
    ]

    for test_case in test_cases:
        response = ApiResponse(**test_case)
        json_str = response.to_json()
        parsed = json.loads(json_str)
        assert parsed == test_case or (
            parsed["success"] == test_case["success"] and
            (parsed.get("error") == test_case.get("error") or
             parsed.get("message") == test_case.get("message"))
        )
        print(f"✓ 测试用例通过: {test_case.get('message', test_case.get('error', '无消息'))}")

    print("")


def test_required_fields():
    """测试必需字段的存在性。"""
    print("=== 测试必需字段 ===")

    # success 字段总是存在
    response = ApiResponse(success=True)
    result = json.loads(response.to_json())
    assert "success" in result
    print("✓ success 字段存在")

    # 成功时，data 可以不存在
    response = ApiResponse(success=True)
    result = json.loads(response.to_json())
    assert "data" not in result or result["data"] is None
    print("✓ 成功时 data 可以为 None")

    # 失败时，error 存在
    response = ApiResponse(success=False, error="错误")
    result = json.loads(response.to_json())
    assert "error" in result
    print("✓ 失败时 error 字段存在")

    # message 字段可选
    response = ApiResponse(success=True)
    result = json.loads(response.to_json())
    assert "message" not in result
    print("✓ message 字段可选")

    print("")


def test_unicode():
    """测试 Unicode 字符的正确处理。"""
    print("=== 测试 Unicode 处理 ===")

    test_data = {
        "chinese": "中文测试",
        "emoji": "😀🎉",
        "mixed": "English中文日本語",
        "special": "特殊字符: <>&\"'"
    }

    response = ApiResponse(success=True, data=test_data)
    json_str = response.to_json()
    result = json.loads(json_str)

    assert result["data"]["chinese"] == "中文测试"
    assert result["data"]["emoji"] == "😀🎉"
    assert result["data"]["mixed"] == "English中文日本語"
    assert result["data"]["special"] == "特殊字符: <>&\"'"
    print("✓ Unicode 处理正确")

    print("")


if __name__ == "__main__":
    try:
        test_api_response()
        test_json_parsing()
        test_required_fields()
        test_unicode()
        print("=" * 50)
        print("所有测试通过! ✓")
        print("=" * 50)
    except AssertionError as e:
        print(f"✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
