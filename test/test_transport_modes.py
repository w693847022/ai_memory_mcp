#!/usr/bin/env python
"""测试不同传输模式的启动和功能."""

import subprocess
import time
import requests
import sys

def test_transport_mode(transport, port):
    """测试指定的传输模式."""
    print(f"\n=== 测试 {transport.upper()} 模式 ===")

    # 启动服务器
    cmd = [
        sys.executable, "run.py",
        "--transport", transport,
        "--host", "127.0.0.1",
        "--port", str(port)
    ]

    proc = subprocess.Popen(
        cmd,
        cwd="/home/wrs/code/mcp_test",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    # 等待服务器启动
    time.sleep(3)

    try:
        if transport == "stdio":
            print("✓ stdio 模式需要通过 MCP 客户端测试")
            return True
        else:
            # 测试 HTTP 端点
            base_url = f"http://127.0.0.1:{port}"

            # 健康检查
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✓ 服务器响应正常")
            else:
                print(f"✗ 服务器响应异常: {response.status_code}")
                return False

            print(f"✓ {transport} 模式基础测试通过")
            return True

    except requests.exceptions.ConnectionError:
        print(f"✗ 无法连接到服务器")
        return False
    except Exception as e:
        print(f"✗ 测试出错: {e}")
        return False
    finally:
        # 停止服务器
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

if __name__ == "__main__":
    # 测试 SSE 模式
    print("测试 SSE 模式...")
    test_transport_mode("sse", 8888)

    # 测试 Streamable HTTP 模式
    print("\n测试 Streamable HTTP 模式...")
    test_transport_mode("streamable-http", 8889)
