# OpenClaw 多 Agent 创建教程

来源: CSDN - 真的能行！openclaw+飞书创建多agent执行任务的方法与教程

## 核心要点

### 1. 创建独立 Agent vs 子 Agent
- 默认创建的是临时子 Agent，用完即丢
- 需要用正确的方法创建独立 Agent

### 2. 创建流程

#### 阶段1：基础配置（必须）

1. 运行命令创建 Agent：
```bash
openclaw agents add {agent-name} --workspace ~/.openclaw/workspace-{agent-name}
```

2. 在 workspace 中创建必要文件：
- AGENT.md
- SKILL.md
- README.md
- QUICKSTART.md
- IDENTITY.md
- MEMORY.md
- SOUL.md
- TOOLS.md
- USER.md
- HEARTBEAT.md

3. 设置身份：
```bash
openclaw agents set-identity --agent {agent-name} --from-identity
```

4. （可选）配置路由绑定：
```bash
openclaw agents bind --agent {agent-name} --bind {channel}:{account}
```

5. 配置飞书群聊绑定 (bindings)

6. 重启 Gateway

7. 测试 Agent 响应

#### 阶段2：自我进化配置

- 智能技能搜索
- 建立自我提升系统
- 建立学习记录机制

#### 阶段3：持续进化机制

- 定期技能检查
- 使用中学习
- 主动推荐

### 3. 飞书群聊不@也能回复

配置 requireMention 为 false：
```json
{
  "channels": {
    "feishu": {
      "groupPolicy": "open",
      "requireMention": false
    }
  }
}
```

### 4. 招聘 Agent 模板

```
你是一个Agent管理专家，帮我创建和管理Agent，名字叫做"xxx"，绑定的飞书群聊ID是【xxx】。

【核心定位】
你的主要能力是...

【性格】
你是这样一个 Agent...
```

## 注意事项

1. workspace 位置要正确：~/.openclaw/workspace-{agent-name}
2. 操作前备份重要文件
3. 服务器建议先快照
