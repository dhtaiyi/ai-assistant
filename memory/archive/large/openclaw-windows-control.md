# OpenClaw Windows多节点控制研究

**创建时间:** 2026-02-20
**目标:** 实现Windows系统OpenClaw的远程同步控制

---

## 现有基础

### 已验证能力
- ✅ OpenClaw支持Windows (headless node host)
- ✅ nodes工具可用于控制远程节点
- ✅ NAS代理 (port 13128) 用于外部网络访问
- ✅ GitHub同步机制
- ✅ 跨会话记忆能力

### 待研究
- 🔄 Windows节点配置方法
- 🔄 多节点同步机制
- 🔄 远程控制方案

---

## OpenClaw多节点架构

### 架构组件

```
┌─────────────────────────────────────────────────────────┐
│                   OpenClaw 云端 (Linux)                 │
│  ┌─────────────────────────────────────────────────┐  │
│  │ OpenClaw 主节点                                   │  │
│  │ - 任务调度                                       │  │
│  │ - 子代理管理                                     │  │
│  │ - GitHub同步                                     │  │
│  └─────────────────────────────────────────────────┘  │
│                        │                               │
│                        │ NAS代理 (13128)               │
│                        ▼                               │
│                   外部网络                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   OpenClaw Windows 节点                 │
│  ┌─────────────────────────────────────────────────┐  │
│  │ OpenClaw (headless模式)                         │  │
│  │ - 任务执行                                       │  │
│  │ - 浏览器控制                                     │  │
│  │ - 本地存储同步                                   │  │
│  └─────────────────────────────────────────────────┘  │
│                        │                               │
│                        │ SSH/WinRM                    │
│                        ▼                               │
│                   远程控制                            │
└─────────────────────────────────────────────────────────┘
```

### 节点通信机制

#### 1. Nodes工具 (原生方案)
```bash
# 查看可用节点
openclaw nodes list

# 控制远程节点
openclaw nodes run --node windows-node "command"

# 同步文件
openclaw nodes sync --from local --to windows-node
```

#### 2. Gateway远程访问
```bash
# 通过Tailscale远程访问
openclaw gateway remote

# SSH远程控制
openclaw gateway ssh --target windows
```

#### 3. API远程调用
```bash
# 调用Windows节点API
curl -X POST http://windows-node:4000/api/execute \
  -d '{"command": "python script.py"}'
```

---

## Windows部署方案

### 方案1: 直接安装

#### 系统要求
- Windows 10/11 或 Windows Server 2019+
- Node.js 22+
- 4GB RAM
- 10GB 磁盘空间

#### 安装步骤
```powershell
# 1. 安装Node.js 22+
winget install OpenJS.NodeJS.LTS

# 2. 安装OpenClaw
npm install -g @openclaw/openclaw

# 3. 配置为服务
openclaw gateway install --windows-service

# 4. 开机自启动
Set-Service -Name "OpenClaw" -StartupType Automatic
```

#### 配置文件
```json
{
  "node": {
    "id": "windows-node-001",
    "name": "Windows Workstation",
    "platform": "windows",
    "headless": true
  },
  "gateway": {
    "remote": {
      "enabled": true,
      "method": ["ssh", "tailscale"]
    }
  },
  "sync": {
    "github": {
      "enabled": true,
      "repo": "dhtaiyi/ai-assistant"
    }
  }
}
```

### 方案2: Docker容器

```powershell
# 安装Docker Desktop for Windows
winget install Docker.DockerDesktop

# 运行OpenClaw容器
docker run -d \
  --name openclaw-windows \
  -p 4000:4000 \
  -v C:\OpenClaw\workspace:/root/.openclaw/workspace \
  -e NODE_ENV=production \
  openclaw/openclaw:latest

# 配置开机自启动
docker update --restart=always openclaw-windows
```

### 方案3: WSL2 (推荐)

```powershell
# 1. 安装WSL2
wsl --install -d Ubuntu

# 2. 在WSL中安装OpenClaw
wsl -d Ubuntu
sudo apt update && sudo apt install -y nodejs npm
npm install -g @openclaw/openclaw

# 3. 配置Windows互操作
# 允许WSL访问Windows网络
# 配置共享文件夹

# 4. 开机自启动 (通过Windows任务计划程序)
```

---

## 数据同步机制

### 同步策略

#### 1. Git自动同步
```bash
# 在Windows节点上配置
cd /root/.openclaw/workspace
git config user.name "Windows-Node"
git config user.email "windows@ai-assistant"

# 设置自动拉取
echo "0 */6 * * * git pull origin main" >> crontab

# 设置自动推送
git config push.autoSetupRemote true
```

#### 2. 工作区同步脚本

```powershell
# sync-to-cloud.ps1
$workspace = "C:\Users\Username\OpenClaw\workspace"
$cloud = "root@cloud-server:/path/to/workspace"

# 同步到云端
rsync -avz --delete `
  -e ssh `
  $workspace `
  $cloud

# 拉取更新
rsync -avz `
  -e ssh `
  $cloud `
  $workspace
```

#### 3. 实时同步 (Watchman)

```javascript
// watch-sync.js
const chokidar = require('chokidar');
const { exec } = require('child_process');

const watcher = chokidar.watch('/root/.openclaw/workspace', {
  ignored: /node_modules|\.git/,
  persistent: true
});

watcher.on('change', (path) => {
  console.log(`File ${path} has been changed`);
  
  // 自动提交并推送
  exec('git add -A && git commit -m "sync: auto-update" && git push', 
    (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${stderr}`);
      } else {
        console.log('Synced to cloud');
      }
    });
});
```

---

## 远程控制方案

### 1. SSH远程控制

#### Windows配置
```powershell
# 安装OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 启动服务
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic

# 配置防火墙
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server' -Protocol TCP -LocalPort 22 -Action Allow
```

#### 连接方式
```bash
# 从云端连接Windows
ssh administrator@windows-ip

# 执行命令
ssh user@windows-ip "cd /root/.openclaw/workspace && python3 script.py"

# 端口转发
ssh -L 4000:localhost:4000 user@windows-ip
```

### 2. Tailscale远程访问

```powershell
# 安装Tailscale
winget install Tailscale.Tailscale

# 登录并连接
tailscale up --auth-key xxx

# 从云端访问
tailscale ip --list
ssh user@100.x.x.x
```

### 3. OpenClaw Gateway远程

```bash
# 配置远程访问
openclaw gateway configure --remote-enabled

# 查看远程节点
openclaw nodes list

# 在Windows节点上注册
openclaw nodes register --name "windows-node" --gateway cloud-gateway
```

---

## 完整部署清单

### Phase 1: Windows节点搭建
- [ ] 安装Node.js 22+
- [ ] 安装OpenClaw
- [ ] 配置为系统服务
- [ ] 设置开机自启动
- [ ] 安装并配置SSH
- [ ] 安装Tailscale

### Phase 2: 数据同步
- [ ] 配置GitHub自动同步
- [ ] 设置工作区同步脚本
- [ ] 配置实时同步 (可选)
- [ ] 测试同步完整性

### Phase 3: 远程控制
- [ ] 测试SSH连接
- [ ] 测试Tailscale访问
- [ ] 配置OpenClaw Gateway
- [ ] 设置节点注册

### Phase 4: 监控和维护
- [ ] 配置日志监控
- [ ] 设置告警机制
- [ ] 制定备份策略
- [ ] 文档化运维手册

---

## 预期效果

### 功能对比

| 功能 | 现状 (Linux) | 目标 (Windows) |
|------|-------------|---------------|
| 任务执行 | ✅ | ✅ |
| 浏览器控制 | ✅ Playwright | ✅ Playwright |
| GitHub同步 | ✅ | ✅ |
| 跨会话记忆 | ✅ | ✅ |
| 远程访问 | 直接 | SSH/Tailscale |
| 开机自启动 | systemd | Windows服务 |

### 使用场景

1. **多设备协同**
   - 云端运行主任务
   - Windows执行浏览器自动化

2. **容灾备份**
   - 代码实时同步
   - 故障时快速切换

3. **性能扩展**
   - Windows处理重任务
   - Linux处理轻量任务

---

## 下一步行动

### 立即执行
1. 准备Windows测试环境
2. 编写自动化部署脚本
3. 设计监控方案

### 长期规划
1. 建立多节点管理平台
2. 实现智能任务分发
3. 优化同步效率

---

*文档维护: 2026-02-20*
*状态: 研究阶段*
