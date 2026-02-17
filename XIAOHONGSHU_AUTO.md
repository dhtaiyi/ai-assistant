# 🎯 小红书搜索自动化方案

## 概述

由于小红书的Cookie会过期，需要定期从浏览器获取新的Cookie。

本方案提供3种自动获取Cookie的方法。

---

## 📋 方法1：书签脚本（推荐 ⭐）

### 安装步骤

1. **创建书签**
   - 浏览器右键点击书签栏
   - 选择"添加网页"
   - 名称: `📋 小红书Cookie`
   - 网址: 复制下面的代码

```javascript
javascript:(function(){const%20cookies=document.cookie.split('%3B').map(c=>c.trim()).join('%3B%20');navigator.clipboard.writeText(cookies).then(()=>alert('Cookie%E5%B7%B2%E5%A4%8D%E5%88%B0%E5%89%AA%E8%B4%B4%E6%9D%BF!%5Cn%5Cn'+cookies)).catch(()=>prompt('Ctrl+C%E5%A4%8D%E5%88%B0:',cookies));})();
```

2. **使用方法**
   - 打开小红书并登录
   - 点击书签
   - Cookie已复制到剪贴板

3. **发送到服务器**
   ```bash
   # 在服务器终端粘贴Cookie
   echo 'COOKIE="粘贴"' > /root/.openclaw/workspace/xiaohongshu-cookie.txt
   
   # 测试搜索
   python3 /root/.openclaw/workspace/xiaohongshu-use-cookie.py
   ```

---

## 📋 方法2：油猴脚本（自动按钮）

### 安装步骤

1. **安装油猴扩展**
   - Chrome/Edge: 安装 "Tampermonkey"
   - 地址: https://chrome.google.com/webstore/detail/tampermonkey

2. **创建脚本**
   - 点击油猴图标 → "添加新脚本"
   - 删除默认代码
   - 粘贴以下代码：

```javascript
// ==UserScript==
// @name         小红书Cookie助手
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  一键获取小红书Cookie
// @author       OpenClaw
// @match        https://www.xiaohongshu.com/*
// @grant        GM_setClipboard
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';
    
    const btn = document.createElement('div');
    btn.innerHTML = '📋 Cookie';
    btn.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: #ff2442;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        cursor: pointer;
        z-index: 99999;
        font-size: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    `;
    
    btn.onclick = function() {
        const cookies = document.cookie.split(';').map(c => c.trim()).join('; ');
        GM_setClipboard(cookies);
        alert('Cookie已复制!\n\n立即粘贴到服务器');
    };
    
    document.body.appendChild(btn);
})();
```

3. **使用**
   - 访问小红书，右上角出现红色按钮
   - 点击按钮，Cookie复制到剪贴板

---

## 📋 方法3：控制台命令（最快）

### 使用步骤

1. 打开小红书并登录
2. F12 → Console（控制台）
3. 粘贴并回车：
```javascript
copy(document.cookie);
console.log('Cookie已复制:', document.cookie);
```

4. Cookie已复制，粘贴到服务器

---

## 🔄 自动化测试流程

```bash
# 1. 获取Cookie（浏览器）
#    书签/油猴/Console任选一种

# 2. 保存到服务器
echo 'COOKIE="粘贴的Cookie"' > /root/.openclaw/workspace/xiaohongshu-cookie.txt

# 3. 运行测试
python3 /root/.openclaw/workspace/xiaohongshu-use-cookie.py
```

---

## 📁 相关文件

| 文件 | 功能 |
|------|------|
| `/root/.openclaw/workspace/xiaohongshu-use-cookie.py` | Cookie版搜索脚本 |
| `/root/.openclaw/workspace/xiaohongshu-cookie.txt` | Cookie保存文件 |
| `/root/.openclaw/workspace/xiaohongshu-bookmark.md` | 书签脚本说明 |
| `/root/.openclaw/workspace/XIAOHONGSHU_AUTO.md` | 本文档 |

---

## 💡 使用建议

**书签脚本最简单** - 创建一次，随时使用
**油猴脚本最方便** - 访问时自动显示按钮
**控制台最快** - 只需复制粘贴两行代码

---

## ⚠️ 注意事项

1. Cookie会过期，需要定期更新
2. 建议每周更新一次Cookie
3. 如果搜索失败，首先检查Cookie是否有效

