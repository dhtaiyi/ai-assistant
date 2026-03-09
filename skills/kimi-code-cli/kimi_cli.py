#!/usr/bin/env python3
"""
Kimi Code CLI 调用脚本
"""
import subprocess
import sys
import os

KIMI_BIN = "/root/.local/bin/kimi"

def run_kimi(prompt: str, work_dir: str = None):
    """调用 Kimi CLI 执行任务"""
    env = os.environ.copy()
    
    cmd = [KIMI_BIN, "term"]
    if work_dir:
        cmd.extend(["-w", work_dir])
    
    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=300,
            env=env
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout: Kimi CLI 执行超时"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def check_login():
    """检查是否已登录"""
    try:
        result = subprocess.run(
            [KIMI_BIN, "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "Not logged in" in result.stdout or "未登录" in result.stdout:
            return False
        return True
    except:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kimi_cli.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    result = run_kimi(prompt)
    
    if result["success"]:
        print(result["stdout"])
    else:
        print(f"Error: {result.get('error')}", file=sys.stderr)
        sys.exit(1)
