# 📌 小红书Cookie获取书签

## 方法1：书签脚本（最简单）

### 步骤1：创建书签
1. 在浏览器中，鼠标右键点击书签栏
2. 选择"添加网页"或"新建书签"
3. 填写：
   - **名称**: 📋 获取小红书Cookie
   - **网址**: javascript:(function(){const cookies=document.cookie.split(';').map(c=>c.trim()).join('; ');navigator.clipboard.writeText(cookies).then(()=>alert('Cookie已复制到剪贴板!\n\n'+cookies)).catch(()=>prompt('Ctrl+C复制:',cookies));})();

### 步骤2：使用
1. 打开小红书 https://www.xiaohongshu.com
2. 确保已登录
3. 点击书签 "📋 获取小红书Cookie"
4. Cookie已复制到剪贴板！

### 步骤3：发送到服务器
```bash
# 在服务器上运行
echo "粘贴Cookie:"
read cookie

# 保存Cookie
echo "COOKIE=\"$cookie\"" > /root/.openclaw/workspace/xiaohongshu-cookie.txt

# 测试搜索
python3 /root/.openclaw/workspace/xiaohongshu-use-cookie.py
```

---

## 方法2：油猴脚本（自动）

### 安装油猴扩展
1. Chrome/Edge: 安装 "Tampermonkey"
2. Firefox: 安装 "Tampermonkey"

### 创建脚本
1. 点击油猴图标 → "添加新脚本"
2. 替换为以下代码：

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
    
    // 创建浮动按钮
    const btn = document.createElement('div');
    btn.innerHTML = '📋 Cookie';
    btn.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: #ff2442;
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        z-index: 99999;
        font-size: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    
    btn.onclick = function() {
        const cookies = document.cookie.split(';').map(c => c.trim()).join('; ');
        GM_setClipboard(cookies);
        alert('Cookie已复制!\n\n点击确定后粘贴到服务器');
        // 复制后打开新窗口提示
        window.open('about:blank', '_blank', 'width=400,height=200');
    };
    
    document.body.appendChild(btn);
})();
```

3. 保存
4. 访问小红书时，右上角会出现红色按钮
5. 点击即可复制Cookie

---

## 方法3：快速测试（复制当前Cookie）

如果书签方法太麻烦，直接：

1. 浏览器打开小红书并登录
2. F12 → Console（控制台）
3. 粘贴：
```javascript
copy(document.cookie);
console.log('Cookie已复制:', document.cookie);
```
4. Ctrl+V粘贴到服务器

