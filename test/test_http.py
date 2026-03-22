#!/usr/bin/env python
"""测试 HTTP/SSE 模式的 MCP 服务器."""

import subprocess
import time
import requests
import json
import sys

def test_http_server():
    """测试HTTP服务器功能."""

    print("=== 启动 SSE 服务器 ===")
    # 在后台启动服务器
    server_proc = subprocess.Popen(
        [sys.executable, "src/server.py",
         "--transport", "sse",
         "--host", "127.0.0.1",
         "--port", "8888"],
        cwd="/home/wrs/code/mcp_test",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    # 等待服务器启动
    time.sleep(2)

    try:
        base_url = "http://127.0.0.1:8888"

        print("\n=== 测试1: 服务器信息 ===")
        response = requests.get(f"{base_url}/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 服务器状态: {data.get('status')}")
            print(f"✓ 传输模式: {data.get('transport')}")
        else:
            print(f"✗ 失败: {response.text}")

        print("\n=== 测试2: 健康检查 ===")
        response = requests.get(f"{base_url}/health")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 状态: {data.get('status')}")
        else:
            print(f"✗ 失败: {response.text}")

        print("\n=== 测试3: SSE 端点 ===")
        response = requests.get(f"{base_url}/sse", stream=True, timeout=2)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Content-Type: {response.headers.get('Content-Type')}")
            # 读取第一行
            for line in response.iter_lines():
                if line:
                    print(f"✓ 收到: {line.decode()}")
                    break
        else:
            print(f"✗ 失败: {response.text}")

        print("\n=== 测试4: API 认证 ===")
        # 测试没有 API Key 时的请求（应该失败）
        response = requests.post(
            f"{base_url}/mcp/call",
            json={"tool": "project_list", "params": {}}
        )
        if response.status_code == 200:
            print("✓ 无需认证（未启用API Key）")
        else:
            print(f"✓ 需要认证: {response.status_code}")

        print("\n=== 测试5: 直接工具调用 ===")
        response = requests.post(
            f"{base_url}/mcp/call",
            json={
                "tool": "project_list",
                "params": {}
            }
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✓ 工具调用成功")
                print(f"  结果预览: {data['result'][:100]}...")
            else:
                print(f"✗ 调用失败: {data.get('error')}")
        else:
            print(f"✗ 失败: {response.text}")

        print("\n=== 测试6: 统计查询 ===")
        response = requests.post(
            f"{base_url}/mcp/call",
            json={
                "tool": "stats_summary",
                "params": {"type": "full"}
            }
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✓ 统计查询成功")
                result = data['result']
                if "总调用次数" in result:
                    print(f"  总调用: {result.split('总调用次数: ')[1].split('\\n')[0]}")
            else:
                print(f"✗ 查询失败: {data.get('error')}")
        else:
            print(f"✗ 失败: {response.text}")

        print("\n=== 所有测试完成 ===")

    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请检查服务器是否正常启动")
    except Exception as e:
        print(f"✗ 测试出错: {e}")
    finally:
        # 停止服务器
        print("\n=== 停止服务器 ===")
        server_proc.terminate()
        server_proc.wait(timeout=5)
        print("✓ 服务器已停止")

if __name__ == "__main__":
    test_http_server()
