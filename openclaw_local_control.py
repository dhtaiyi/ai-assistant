#!/usr/bin/env python3
"""
OpenClaw 本地控制工具

功能：
1. 查看Gateway状态
2. 列出会话
3. 发送消息到会话
4. 执行ACP命令
5. 重启Gateway

用法：
    python3 openclaw_local_control.py status      # 查看状态
    python3 openclaw_local_control.py sessions    # 列出会话
    python3 openclaw_local_control.py send "消息" # 发送消息
    python3 openclaw_local_control.py exec "ls -la" # 执行命令
    python3 openclaw_local_control.py restart     # 重启Gateway
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# 配置
GATEWAY_PORT = 18789
GATEWAY_URL = f"http://localhost:{GATEWAY_PORT}"
WORKSPACE = "/home/dhtaiyi/.openclaw/workspace"


def run_command(cmd: str, shell: bool = True) -> tuple:
    """执行shell命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            cwd=WORKSPACE
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def cmd_status():
    """查看Gateway状态"""
    print("📊 Gateway 状态")
    print("-" * 40)
    code, stdout, stderr = run_command("openclaw gateway status")
    print(stdout)
    return code == 0


def cmd_sessions():
    """列出所有会话"""
    print("📋 会话列表")
    print("-" * 40)
    code, stdout, stderr = run_command("openclaw sessions --json")
    if code == 0:
        try:
            sessions = json.loads(stdout)
            if isinstance(sessions, list):
                for s in sessions[:10]:  # 只显示前10个
                    if isinstance(s, dict):
                        key = s.get('key', 'N/A')[:30]
                        updated = s.get('updated', 'N/A')[:19]
                        messages = s.get('messageCount', 0)
                        print(f"  • {key}")
                        print(f"    更新: {updated} | 消息: {messages}")
            else:
                print(json.dumps(sessions, indent=2))
        except json.JSONDecodeError:
            print(stdout)
    else:
        print(f"❌ 错误: {stderr}")
    return code == 0


def cmd_send(message: str):
    """发送消息到主会话"""
    print(f"📤 发送消息到主会话")
    print("-" * 40)
    print(f"消息: {message[:100]}..." if len(message) > 100 else f"消息: {message}")
    
    # 通过agent命令发送，使用明确的会话ID
    cmd = f'openclaw agent --session-id 155e31f0-35f3-4921-b2ae-ab1b387604f6 --message "{message}"'
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        print("✅ 消息已发送")
    else:
        print(f"❌ 错误: {stderr}")
    return code == 0


def cmd_exec(command: str):
    """执行命令"""
    print(f"⚡ 执行命令")
    print("-" * 40)
    print(f"命令: {command}")
    
    # 通过ACP执行
    cmd = f'openclaw acp --session main --require-existing <<< \'{{"type":"shell","command":"{command}"}}\''
    code, stdout, stderr = run_command(cmd)
    
    print("\n输出:")
    print(stdout)
    if stderr:
        print(f"错误: {stderr}")
    return code == 0


def cmd_restart():
    """重启Gateway"""
    print("🔄 重启Gateway")
    print("-" * 40)
    code, stdout, stderr = run_command("openclaw gateway restart")
    if code == 0:
        print("✅ 重启命令已发送")
        # 等待一下
        import time
        time.sleep(3)
        print("⏳ 等待Gateway重新启动...")
        cmd_status()
    else:
        print(f"❌ 错误: {stderr}")
    return code == 0


def cmd_logs(lines: int = 50):
    """查看日志"""
    print(f"📜 Gateway 日志 (最近{lines}行)")
    print("-" * 40)
    code, stdout, stderr = run_command(f"openclaw logs --tail {lines}")
    print(stdout)
    return code == 0


def cmd_browser(action: str = "status"):
    """浏览器控制"""
    print(f"🌐 浏览器 {action}")
    print("-" * 40)
    if action == "status":
        code, stdout, stderr = run_command("openclaw browser status")
        print(stdout)
    elif action == "open":
        code, stdout, stderr = run_command("openclaw browser open --targetUrl https://www.baidu.com")
        print("✅ 已打开浏览器")
    elif action == "screenshot":
        code, stdout, stderr = run_command("openclaw browser screenshot")
        print("📸 截图已保存")
    return code == 0


def cmd_help():
    """显示帮助"""
    print("""
🌸 OpenClaw 本地控制工具

用法:
    python3 openclaw_local_control.py <命令> [参数]

命令:
    status              查看Gateway状态
    sessions            列出所有会话
    send <消息>         发送消息到主会话
    exec <命令>         执行shell命令
    restart             重启Gateway
    logs [行数]         查看日志 (默认50行)
    browser status      浏览器状态
    browser open        打开浏览器
    browser screenshot  截图
    help                显示此帮助

示例:
    python3 openclaw_local_control.py status
    python3 openclaw_local_control.py sessions
    python3 openclaw_local_control.py send "Hello from CLI"
    python3 openclaw_local_control.py exec "ls -la"
    python3 openclaw_local_control.py logs 100
""")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    # 根据命令执行
    if command == "status":
        cmd_status()
    elif command == "sessions":
        cmd_sessions()
    elif command == "send":
        message = " ".join(args) if args else "Hello from CLI"
        cmd_send(message)
    elif command == "exec":
        command = " ".join(args) if args else "ls -la"
        cmd_exec(command)
    elif command == "restart":
        cmd_restart()
    elif command == "logs":
        lines = int(args[0]) if args else 50
        cmd_logs(lines)
    elif command == "browser":
        action = args[0] if args else "status"
        cmd_browser(action)
    elif command == "help" or command == "--help" or command == "-h":
        cmd_help()
    else:
        print(f"❌ 未知命令: {command}")
        cmd_help()


if __name__ == "__main__":
    main()
