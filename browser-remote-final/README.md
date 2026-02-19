# OpenClaw 远程浏览器控制

**完整方案，让我可以主动控制你的浏览器！**

## 工作原理

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   我的AI     │  HTTP   │  Python     │  HTTP   │  Chrome     │
│  (发送命令)   │◄──────►│  服务器     │◄──────►│  扩展       │
└─────────────┘         └─────────────┘         └─────────────┘
                              │
                              │ 轮询
                              ▼
                         ┌─────────────┐
                         │  你的电脑   │
                         │  执行操作   │
                         └─────────────┘
```

## 安装步骤

### 1. 安装Chrome扩展

1. 打开 `chrome://extensions/`
2. 开启「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `browser-remote-final/` 文件夹

### 2. 运行服务器

```bash
cd browser-remote-final
python server.py
```

服务器会显示地址，例如：`http://localhost:9999`

### 3. 扩展连接服务器

1. 点击扩展图标
2. 输入服务器地址
3. 点击「连接服务器」

## 使用方法

### 我控制你的浏览器

1. 我发送命令到服务器
2. 服务器保存命令
3. 扩展轮询获取命令
4. 扩展执行命令并返回结果
5. 我查看结果

### 控制面板

打开浏览器访问 `http://localhost:9999`

```
📤 发送命令：
  - navigate: 导航
  - click: 点击
  - getStockData: 股票数据
  - getPageInfo: 页面信息
```

## 文件结构

```
browser-remote-final/
├── manifest.json      # Chrome扩展配置
├── background.js    # 后台服务（执行命令）
├── popup.html      # 扩展界面（连接服务器）
├── server.py       # Python服务器
└── README.md       # 说明文档
```

## 快速开始

```bash
# 1. 安装扩展
# 2. 运行服务器
python server.py

# 3. 扩展连接
# 4. 我就可以控制了！
```

## 注意事项

- 需要Python 3
- 保持服务器运行
- 扩展需要保持连接
