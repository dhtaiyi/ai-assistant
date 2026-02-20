# OpenClaw 本地点对点控制研究

**创建时间:** 2026-02-20
**状态:** ✅ 已实现基础功能

---

## 概述

OpenClaw 本地控制是指在运行OpenClaw的同一台机器上，通过命令行工具直接与OpenClaw Gateway通信，实现：
- 查看Gateway状态
- 管理会话
- 发送消息到会话
- 执行远程命令
- 控制浏览器等

---

## 当前环境

### Gateway运行状态
- **端口:** 18789
- **PID:** 695325
- **状态:** ✅ 运行中
- **绑定:** 0.0.0.0 (所有网卡)
- **Dashboard:** http://10.0.0.15:18789/

### 会话信息
| 会话 | ID | 类型 | 最后更新 |
|------|-----|------|----------|
| agent:main:main | 155e31f0-... | direct | 刚刚 |
| agent:main:wecom:dm:nizheng | 6081b40e-... | direct | 刚刚 |
| agent:main:wecom:group:nizheng | 19be4fb8-... | group | 之前 |

---

## 控制方式

### 方式1: 命令行工具

```bash
# 查看状态
openclaw gateway status

# 列出会话
openclaw sessions --json

# 发送消息
openclaw agent --session-id <会话ID> --message "消息内容"

# 查看日志
openclaw logs --tail 50

# 重启Gateway
openclaw gateway restart
```

### 方式2: 控制脚本

已创建两个控制脚本：

1. **Python版本** - `openclaw_local_control.py`
   - 功能全面
   - 易于扩展
   - 支持参数解析

2. **Bash版本** - `openclaw_ctrl.sh`
   - 轻量级
   - 依赖少
   - 快速执行

### 使用示例

```bash
# Bash脚本用法
./openclaw_ctrl.sh status          # 查看状态
./openclaw_ctrl.sh sessions         # 列出会话
./openclaw_ctrl.sh send "消息"     # 发送消息
./openclaw_ctrl.sh logs 50         # 查看日志
./openclaw_ctrl.sh restart         # 重启Gateway
./openclaw_ctrl.sh browser         # 浏览器状态

# Python脚本用法
python3 openclaw_local_control.py status
python3 openclaw_local_control.py sessions
python3 openclaw_local_control.py send "消息"
python3 openclaw_local_control.py logs 100
```

---

## 集成到小雨助手

### 方案1: 直接调用脚本

```python
import subprocess

def cmd_openclaw(command):
    """执行OpenClaw命令"""
    result = subprocess.run(
        ['bash', '/root/.openclaw/workspace/openclaw_ctrl.sh', command],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### 方案2: 导入Python模块

```python
from openclaw_local_control import cmd_status, cmd_sessions, cmd_send

# 查看状态
print(cmd_status())

# 发送消息
cmd_send("Hello from小雨助手")
```

### 方案3: 通过ACP协议

```python
import asyncio
import websockets

async def send_acp_message(message):
    """通过ACP发送消息"""
    async with websockets.connect("ws://localhost:18789") as ws:
        await ws.send(json.dumps({
            "type": "agent:turn",
            "sessionId": "主会话ID",
            "message": message
        }))
        response = await ws.recv()
        return response
```

---

## 高级功能

### 1. 实时消息监听

```python
import asyncio
import websockets

async def listen_messages():
    """监听所有消息"""
    uri = "ws://localhost:18789"
    async with websockets.connect(uri) as ws:
        await ws.send('{"type":"subscribe","channels":["all"]}')
        async for message in ws:
            print(f"收到: {message}")

# 运行监听器
asyncio.run(listen_messages())
```

### 2. 会话自动选择

```python
def get_main_session():
    """获取主会话ID"""
    import subprocess
    result = subprocess.run(
        ['openclaw', 'sessions', '--json'],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    for session in data.get('sessions', []):
        if 'agent:main:main' in session.get('key', ''):
            return session.get('sessionId')
    return None
```

### 3. 批量操作

```bash
#!/bin/bash
# 批量发送消息到多个会话

sessions=("会话ID1" "会话ID2" "会话ID3")

for session in "${sessions[@]}"; do
    openclaw agent --session-id "$session" --message "批量测试消息"
    sleep 1
done
```

---

## 架构图

```
┌─────────────────────────────────────────┐
│         本地终端 (SSH/本地)               │
│  ┌─────────────────────────────────┐   │
│  │ 控制脚本 (openclaw_ctrl.sh)      │   │
│  │ 或 Python模块 (openclaw_*.py)   │   │
│  └─────────────────────────────────┘   │
│                  │                       │
│                  ▼                       │
│         openclaw 命令行工具               │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         OpenClaw Gateway (端口18789)      │
│  ┌─────────────────────────────────┐   │
│  │ 会话管理器                        │   │
│  │ 消息路由器                        │   │
│  │ 代理连接                          │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                  │
                  ▼
        各种通道 (WeCom, WhatsApp等)
```

---

## 应用场景

### 1. 自动化运维
```bash
# 定时检查Gateway状态
0 * * * * /root/.openclaw/workspace/openclaw_ctrl.sh status >> /var/log/openclaw.log
```

### 2. 批量消息发送
```bash
# 发送公告到多个会话
for session in $(get_session_ids); do
    ./openclaw_ctrl.sh send "系统公告: ..."
done
```

### 3. 集成到CI/CD
```python
# 在部署脚本中发送通知
def notify_deployment(status):
    message = f"部署{'成功' if status else '失败'}"
    subprocess.run(['./openclaw_ctrl.sh', 'send', message])
```

### 4. 监控系统集成
```bash
# 检查Gateway状态，异常时告警
if ! ./openclaw_ctrl.sh status | grep -q "running"; then
    ./openclaw_ctrl.sh send "⚠️ Gateway已停止!"
fi
```

---

## 文件清单

| 文件 | 用途 | 状态 |
|------|------|------|
| `openclaw_local_control.py` | Python控制模块 | ✅ |
| `openclaw_ctrl.sh` | Bash控制脚本 | ✅ |
| `memory/openclaw-local-control.md` | 研究文档 | ✅ |

---

## 下一步计划

### 短期
- [ ] 完善错误处理
- [ ] 添加更多命令支持
- [ ] 集成到小雨助手

### 长期
- [ ] Web界面控制
- [ ] 实时消息推送
- [ ] 多节点统一管理

---

*文档维护: 2026-02-20*
