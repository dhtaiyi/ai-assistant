# OpenClaw 远程浏览器控制

## 简介

让 OpenClaw AI 能够远程操作 Chrome 浏览器的完整解决方案。

## 系统架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   OpenClaw AI   │────▶│  HTTP Server   │────▶│ Chrome Extension│
│  (AI 助手)      │     │  (Python :9999) │     │ (浏览器控制)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 组件

| 组件 | 文件 | 说明 |
|------|------|------|
| Chrome扩展 | `manifest.json` | 接收API命令并执行浏览器操作 |
| 后台服务 | `background.js` | 处理来自服务器的请求 |
| 控制界面 | `popup.html` | 手动控制界面 |
| HTTP服务器 | `server.py` | 提供API接口 |
| 客户端库 | `client.py` | Python客户端SDK |
| 集成脚本 | `openclaw_integration.py` | OpenClaw专用集成 |

## 快速开始

### 1. 安装 Chrome 扩展

1. 打开 Chrome，地址栏输入 `chrome://extensions/`
2. 打开「开发者模式」（右上角）
3. 点击「加载已解压的扩展程序」
4. 选择 `browser-remote/` 文件夹

### 2. 启动 HTTP 服务器

```bash
cd browser-remote
python server.py
```

服务器将监听端口 `9999`。

### 3. 测试连接

```bash
python client.py
```

## API 使用

### 基础操作

```python
from openclaw_integration import OpenClawBrowser

browser = OpenClawBrowser()

# 打开网页
browser.go_to('https://www.xiaohongshu.com')

# 点击元素
browser.click('.btn-primary')

# 输入文本
browser.type('input[placeholder="标题"]', '我的笔记')

# 滚动页面
browser.scroll_down(500)

# 等待
browser.wait(2)
```

### 小红书专用

```python
# 打开小红书
browser.xiaohongshu_open()

# 检查登录状态
browser.xiaohongshu_check_login()

# 发布笔记
browser.xiaohongshu_publish('标题', '正文内容')
```

### 直接调用 API

```bash
# 导航
curl -X POST http://localhost:9999/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": {"type": "navigate", "url": "https://www.xiaohongshu.com"}}'

# 点击
curl -X POST http://localhost:9999/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": {"type": "click", "selector": ".btn-primary"}}'

# 滚动
curl -X POST http://localhost:9999/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": {"type": "scroll", "direction": "down", "amount": 500}}'

# 获取页面信息
curl http://localhost:9999/api/page
```

## 命令列表

| 命令 | 参数 | 说明 |
|------|------|------|
| navigate | url | 打开URL |
| click | selector, index | 点击元素 |
| type | selector, text | 输入文本 |
| scroll | direction, amount | 滚动页面 |
| wait | duration | 等待(毫秒) |
| screenshot | - | 截图 |
| evaluate | script | 执行JS代码 |
| getPageInfo | - | 获取页面信息 |
| findElement | selector | 查找元素 |
| executeScript | code | 执行脚本 |

## 文件结构

```
browser-remote/
├── manifest.json           # Chrome扩展配置
├── background.js          # 后台服务
├── popup.html            # 控制界面
├── popup.js              # 界面逻辑
├── server.py             # HTTP服务器
├── client.py             # Python客户端
├── openclaw_integration.py # OpenClaw集成
├── README.md             # 说明文档
└── icons/                # 图标文件
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## OpenClaw 集成

### 在 OpenClaw 中使用

```python
from openclaw_integration import OpenClawBrowser

def monitor_xiaohongshu():
    """监控小红书"""
    browser = OpenClawBrowser()
    
    # 打开小红书
    browser.xiaohongshu_open()
    browser.wait(3)
    
    # 检查登录状态
    login_status = browser.xiaohongshu_check_login()
    
    if login_status.get('logged_in'):
        # 获取页面信息
        info = browser.get_info()
        print(f"当前页面: {info.get('title')}")
        
        return True
    else:
        print("请先登录小红书")
        return False
```

## 注意事项

1. **需要 Chrome 扩展支持**
   - 必须安装并启用扩展
   - 扩展需要保持运行

2. **权限问题**
   - 可能需要手动允许跨域请求
   - 部分网站可能有防护

3. **网络延迟**
   - API调用有网络延迟
   - 建议添加 `wait()` 命令

4. **稳定性**
   - 长时间运行可能不稳定
   - 建议定期重启服务

## 故障排除

### 问题1: 连接失败
```bash
# 检查扩展是否安装
chrome://extensions/

# 检查服务器是否运行
curl http://localhost:9999/api/status
```

### 问题2: 点击失败
```python
# 先查找元素
result = browser.find('.btn')
print(result)

# 确保元素存在再点击
if result.get('success') and result.get('result'):
    browser.click('.btn')
```

### 问题3: 权限错误
- 检查 `manifest.json` 中的 `host_permissions`
- 确保已授权目标网站

## 未来功能

- [ ] 自动登录支持
- [ ] 多标签页管理
- [ ] 截图分析
- [ ] 批量操作
- [ ] 定时任务
- [ ] 错误重试

## License

MIT
