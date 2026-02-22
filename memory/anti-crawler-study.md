# 反爬虫机制与对抗技术

> 学习日期: 2026-02-22

---

## 一、常见反爬虫机制

### 1. 基础反爬

| 机制 | 描述 | 对抗方法 |
|------|------|----------|
| User-Agent检测 | 检测爬虫标识 | 伪装真实浏览器UA |
| IP频率限制 | 同一IP请求过快封禁 | 使用代理IP池 |
| Cookie/Session | 检测登录状态 | 模拟登录/保持Cookie |
| Referer检测 | 检测来源页面 | 伪造Referer |

### 2. 中级反爬

| 机制 | 描述 | 对抗方法 |
|------|------|----------|
| 验证码 | OCR/滑块/点选 | 第三方打码平台/AI识别 |
| JS渲染 | 内容动态生成 | Selenium/Playwright |
| 加密参数 | 请求签名加密 | 逆向JS/Selenium |
| IP代理池 | 检测数据中心IP | 住宅代理 |

### 3. 高级反爬

| 机制 | 描述 | 对抗方法 |
|------|------|----------|
| 浏览器指纹 | 检测自动化特征 | 伪装指纹/undetected-chromedriver |
| 行为分析 | 检测异常操作模式 | 模拟人类行为 |
| 设备指纹 | 检测虚拟机/容器 | 真实设备/手机农场 |
| 人机验证 | 行为验证码 | 机器学习模型 |

---

## 二、对抗技术详解

### 1. 代理IP池

```python
# 代理轮换示例
import requests

proxies = [
    "http://user:pass@proxy1.com:8080",
    "http://user:pass@proxy2.com:8080",
    "socks5://user:pass@proxy3.com:1080",
]

for proxy in proxies:
    try:
        r = requests.get(url, proxies={"http": proxy, "https": proxy})
        if r.status_code == 200:
            break
    except:
        continue
```

**代理类型对比：**
| 类型 | 隐匿性 | 速度 | 成本 |
|------|--------|------|------|
| 数据中心IP | 低 | 快 | 便宜 |
| 住宅代理 | 高 | 慢 | 昂贵 |
| 移动代理 | 很高 | 中等 | 很贵 |

### 2. 浏览器自动化

```python
from playwright.sync_api import sync_playwright

def get_browser_with_stealth():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 有头模式更难检测
            args=[
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        # 添加stealth插件
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )
        
        return browser, context
```

### 3. 请求伪装

```python
import requests
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

# 随机延迟
import time
time.sleep(random.uniform(1, 3))
```

### 4. 模拟人类行为

```python
import random
import time
from playwright.sync_api import Page

def human_scroll(page: Page):
    """模拟人类滚动行为"""
    for _ in range(random.randint(3, 8)):
        scroll_amount = random.randint(300, 800)
        page.mouse.wheel(0, scroll_amount)
        time.sleep(random.uniform(0.5, 1.5))

def human_click(page: Page, selector: str):
    """模拟人类点击"""
    # 先移动到元素附近
    element = page.locator(selector)
    box = element.bounding_box()
    if box:
        x = box['x'] + random.randint(0, int(box['width']))
        y = box['y'] + random.randint(0, int(box['height']))
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.1, 0.3))
        element.click()
```

---

## 三、工具推荐

### 1. 浏览器自动化

| 工具 | 特点 | 反检测 |
|------|------|--------|
| Playwright | 现代化官方支持 | 需额外配置 |
| Selenium | 历史悠久，生态丰富 | undetected-chromedriver |
| Puppeteer | Node.js首选 | puppeteer-extra-plugin-stealth |

### 2. 代理服务

| 服务商 | 类型 | 价格 |
|--------|------|------|
| luminati (Bright Data) | 住宅/数据中心 | 昂贵 |
| oxylabs | 住宅/数据中心 | 昂贵 |
| smartproxy | 数据中心 | 中等 |
| ipidea | 住宅 | 中等 |
| 芝麻代理 | 国内 | 便宜 |

### 3. 验证码解决

| 服务商 | 类型 |
|--------|------|
| 2Captcha | 通用 |
| Anti-Captcha | 通用 |
| 打码兔 | 国内 |
| 超级鹰 | 国内 |

---

## 四、实战案例

### 案例1: 同花顺反爬

**问题:** 同花顺封锁了数据中心IP

**解决方案:**
1. 使用住宅代理（昂贵）
2. 使用手机APP API（需要逆向）
3. 换其他数据源（如东方财富、新浪财经）

### 案例2: 知乎反爬

**问题:** 需要登录、验证码、频率限制

**解决方案:**
1. 登录获取Cookie
2. 使用Selenium模拟登录
3. 使用代理池轮换IP
4. 控制请求频率

---

## 五、最佳实践

1. **遵守规则**
   - 查看robots.txt
   - 遵守网站使用条款
   - 设置合理的爬取频率

2. **道德爬虫**
   - 只爬取公开数据
   - 不要泄露/出售数据
   - 注明数据来源

3. **技术选型**
   - 优先简单方案
   - 根据目标网站选择工具
   - 做好失败重试机制

---

## 六、相关资源

- [Playwright文档](https://playwright.dev/python/)
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
- [住宅代理对比](https://github.com/_ADDR_/proxy-providers)

---

*持续更新中...*
