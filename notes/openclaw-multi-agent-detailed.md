# OpenClaw 多 Agent 完整配置教程

来源: https://anool.net/?id=115

## 核心要点

### 1. tools.agentToAgent 配置 ⭐
```json
"tools": {
  "agentToAgent": {
    "enabled": true,
    "allow": ["aiboss", "aicontent", "ainews", "aicode", "aitask"]
  }
}
```

### 2. 5 个 Agent 角色设计

| Agent ID | 名称 | 职责 |
|----------|------|------|
| aiboss | 大管家 | 总协调助手 |
| aicontent | 内容助理 | 文章写作、视频脚本 |
| ainews | 资讯助理 | AI 行业资讯收集 |
| aicode | 代码助理 | 代码审查、技术方案 |
| aitask | 任务助理 | 任务跟踪、提醒 |

### 3. agents 配置
```json
"agents": {
  "list": [
    {
      "id": "aiboss",
      "default": true,
      "name": "aiboss",
      "workspace": "/root/.openclaw/workspace-boss",
      "model": { "primary": "glmcode/glm-4.7" }
    }
  ]
}
```

### 4. channels.feishu 配置
```json
"channels": {
  "feishu": {
    "enabled": true,
    "accounts": {
      "aiboss": { "appId": "cli_xxx", "appSecret": "xxx" }
    }
  }
}
```

### 5. bindings 路由配置
```json
"bindings": [
  {
    "match": { "channel": "feishu", "accountId": "aiboss" },
    "agentId": "aiboss"
  }
]
```

## 常见坑

1. Bot 无法上线 - 需要配置"长连接事件订阅"
2. Agent 无法协作 - 需要在 AGENTS.md 中配置团队成员
3. Workspace 数据混乱 - 确保每个 Agent 独立路径
4. 消息路由错误 - accountId 和 agentId 必须匹配
5. ID 大小写 - 所有 ID 必须纯小写

## 完整配置模板

见原文附录
