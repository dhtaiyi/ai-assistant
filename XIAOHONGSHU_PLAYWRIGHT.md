# 🎯 小红书Playwright自动化方案

## 概述

由于服务器环境无法完全模拟浏览器行为（IP、指纹等差异），采用Playwright自动化浏览器来执行搜索。

---

## 📁 已创建的脚本

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `xiaohongshu-playwright.py` | 简单自动化搜索 | 无头运行，自动搜索 |
| `xiaohongshu-auto.py` | 交互式自动化 | 可见浏览器，需要登录 |

---

## 🚀 使用方法

### 方法1：无头模式（自动）
```bash
python3 /root/.openclaw/workspace/xiaohongshu-playwright.py
```
- 完全自动化
- 无需人工干预
- 但可能需要已登录的浏览器环境

### 方法2：交互模式（推荐）
```bash
python3 /root/.openclaw/workspace/xiaohongshu-auto.py
```
- 显示浏览器窗口
- 需要手动登录一次
- 登录后自动执行搜索

---

## ⚠️ 服务器限制

当前服务器**没有图形界面**，无法显示浏览器窗口。

### 解决方案

#### 方案A：使用本地机器运行
```bash
# 在你的电脑上安装Playwright
pip3 install playwright
playwright install chromium

# 运行脚本
python3 /root/.openclaw/workspace/xiaohongshu-auto.py
```

#### 方案B：使用虚拟显示
```bash
# 安装虚拟显示
apt-get install xvfb

# 使用虚拟显示运行
xvfb-run python3 /root/.openclaw/workspace/xiaohongshu-auto.py
```

#### 方案C：使用远程浏览器服务
- BrowserStack
- LambdaTest
- Sauce Labs

---

## 📊 测试结果对比

| 方案 | Cookie | 搜索 | 备注 |
|------|---------|------|------|
| 直接请求 | ✅ 有效 | ❌ 461 | IP/指纹差异 |
| Playwright自动化 | ✅ 自动 | ⚠️ 待测试 | 完全模拟浏览器 |

---

## 🎯 下一步建议

### 如果你有图形界面
1. 运行 `python3 /root/.openclaw/workspace/xiaohongshu-auto.py`
2. 浏览器窗口打开后登录小红书
3. 脚本自动执行搜索
4. 获取Cookie和搜索结果

### 如果没有图形界面
1. 在本地电脑安装Playwright
2. 运行脚本
3. 将结果保存到文件
4. 上传到服务器

---

## 🔧 技术原理

Playwright自动化的工作流程：

```
1. 启动 Chromium 浏览器
2. 创建新浏览器上下文（隔离Cookie）
3. 访问小红书
4. 登录（如需要）
5. 执行搜索操作
6. 提取搜索结果
7. 关闭浏览器
```

**优势**：
- 完全模拟真实浏览器行为
- 自动处理所有Cookie和验证
- 不会被识别为机器人

**劣势**：
- 速度较慢（需要加载整个页面）
- 资源消耗较大
- 需要图形界面或虚拟显示

---

## 💡 替代方案

如果Playwright不可用，还可以考虑：

1. **Selenium** - 类似的浏览器自动化工具
2. **Puppeteer** - Node.js版本的Playwright
3. **Requests-HTML** - 简化版的请求库
4. **curl** - 命令行HTTP工具

---

## 📁 相关文件

- `/root/.openclaw/workspace/xiaohongshu-playwright.py` - 简单版
- `/root/.openclaw/workspace/xiaohongshu-auto.py` - 交互版
- `/root/.openclaw/workspace/xiaohongshu-use-cookie.py` - Cookie版
- `/root/.openclaw/workspace/xiaohongshu-cookie.txt` - Cookie文件

