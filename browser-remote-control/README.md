# OpenClaw 远程浏览器控制

**完整远程控制方案，我可以远程操作你的浏览器！**

## 架构

```
┌─────────────────┐         ┌─────────────────┐
│   我的AI (我)    │◄──────►│  你的电脑       │
│  client.py      │  HTTP   │  server.py      │
└─────────────────┘         └────────┬────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │  Chrome扩展     │
                           │  background.js  │
                           └────────┬────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │  Chrome浏览器   │
                           │  执行实际操作   │
                           └─────────────────┘
```

## 安装步骤

### 步骤1：安装Chrome扩展

1. 打开 `chrome://extensions/`
2. 开启「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `browser-remote-control/` 文件夹

### 步骤2：运行服务器

```bash
cd browser-remote-control
python server.py --port 9999
```

服务器会显示地址，例如 `http://localhost:9999`

### 步骤3：扩展连接服务器

1. 点击扩展图标
2. 输入服务器地址：`http://localhost:9999`
3. 点击「连接」

---

## 使用方法

### 我控制你的浏览器

```bash
# 导航到同花顺
python client.py -s http://localhost:9999 -c navigate -p https://www.10jqka.com.cn

# 点击元素
python client.py -s http://localhost:9999 -c click -p .btn-primary

# 获取股票数据
python client.py -s http://localhost:9999 -c getStockData

# 交互模式
python client.py -s http://localhost:9999 -i
```

### 交互模式命令

```
navigate <url>     - 导航
click <selector>   - 点击
type <sel> <text>  - 输入
scroll <dir>       - 滚动
stock              - 股票数据
info               - 页面信息
html               - HTML源码
```

## API

### 发送命令

```bash
curl -X POST http://localhost:9999/command \
  -H "Content-Type: application/json" \
  -d '{"command": {"type": "navigate", "url": "https://www.10jqka.com.cn"}}'
```

### 获取结果

```bash
curl http://localhost:9999/result?id=<command_id>
```

## 文件结构

```
browser-remote-control/
├── manifest.json      # Chrome扩展配置
├── background.js     # 后台服务（接收命令并执行）
├── popup.html       # 扩展popup界面
├── server.py        # Python服务器（用户运行）
├── client.py        # Python客户端（我运行）
└── README.md        # 说明文档
```

## 完整流程

1. **你**：安装扩展，运行 `python server.py`
2. **你**：扩展连接服务器
3. **我**：运行 `python client.py` 发送命令
4. **你的浏览器**：执行命令并返回结果

## 注意事项

- 服务器和扩展需要在同一台电脑
- 保持服务器运行
- 防火墙可能需要开放端口

## 问题排查

| 问题 | 解决 |
|------|------|
| 连接失败 | 检查服务器是否运行 |
| 命令无响应 | 检查扩展是否连接 |
| 权限错误 | 以管理员身份运行 |
