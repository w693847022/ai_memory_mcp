#!/usr/bin/env python
"""简单测试 MCP 服务器传输模式."""

import subprocess
import sys
import time
import os

def test_stdio_mode():
    """测试 stdio 模式启动."""
    print("\n=== 测试 STDIO 模式 ===")
    proc = subprocess.Popen(
        [sys.executable, "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(2)
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=2)
    print("✓ stdio 模式启动成功")
    print(f"  输出: {stdout[:100] if stdout else '(waiting for input)'}...")
    return True

def test_sse_mode():
    """测试 SSE 模式启动."""
    print("\n=== 测试 SSE 模式 ===")
    proc = subprocess.Popen(
        [sys.executable, "run.py", "--transport", "sse", "--host", "127.0.0.1", "--port", "8888"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    time.sleep(3)
    output = ""
    try:
        output = proc.stdout.read()
    except:
        pass
    proc.terminate()
    proc.wait(timeout=3)

    if "Uvicorn running" in output or "Started server" in output:
        print("✓ SSE 模式启动成功")
        return True
    else:
        print("✗ SSE 模式启动失败")
        print(f"  输出: {output[:200]}")
        return False

def test_streamable_http_mode():
    """测试 Streamable HTTP 模式启动."""
    print("\n=== 测试 STREAMABLE-HTTP 模式 ===")
    proc = subprocess.Popen(
        [sys.executable, "run.py", "--transport", "streamable-http", "--host", "127.0.0.1", "--port", "8889"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    time.sleep(3)
    output = ""
    try:
        output = proc.stdout.read()
    except:
        pass
    proc.terminate()
    proc.wait(timeout=3)

    if "Uvicorn running" in output or "Started server" in output:
        print("✓ Streamable HTTP 模式启动成功")
        return True
    else:
        print("✗ Streamable HTTP 模式启动失败")
        print(f"  输出: {output[:200]}")
        return False

def test_help():
    """测试帮助信息."""
    print("\n=== 测试帮助信息 ===")
    result = subprocess.run(
        [sys.executable, "run.py", "--help"],
        capture_output=True,
        text=True
    )
    if "--transport" in result.stdout and "--host" in result.stdout:
        print("✓ 帮助信息正确显示")
        return True
    else:
        print("✗ 帮助信息显示失败")
        return False

def test_custom_port():
    """测试自定义端口."""
    print("\n=== 测试自定义端口 ===")
    proc = subprocess.Popen(
        [sys.executable, "run.py", "--transport", "sse", "--port", "9999"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    time.sleep(3)
    output = ""
    try:
        output = proc.stdout.read()
    except:
        pass
    proc.terminate()
    proc.wait(timeout=3)

    if "9999" in output:
        print("✓ 自定义端口配置正确")
        return True
    else:
        print("✗ 自定义端口配置失败")
        return False

if __name__ == "__main__":
    os.chdir("/home/wrs/code/mcp_test")

    results = []
    results.append(("帮助信息", test_help()))
    results.append(("STDIO 模式", test_stdio_mode()))
    results.append(("SSE 模式", test_sse_mode()))
    results.append(("Streamable HTTP 模式", test_streamable_http_mode()))
    results.append(("自定义端口", test_custom_port()))

    print("\n" + "="*50)
    print("测试结果汇总:")
    print("="*50)
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        sys.exit(1)
