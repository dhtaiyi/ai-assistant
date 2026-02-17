const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    console.log('🚀 启动浏览器（持久化模式）...');
    
    // 检查是否有保存的 Cookie
    const cookieFile = '/root/.openclaw/workspace/xiaohongshu-cookies.json';
    const userDataDir = '/root/.openclaw/workspace/xiaohongshu-user-data';
    
    // 如果有保存的 Cookie，尝试恢复登录状态
    if (fs.existsSync(cookieFile)) {
        console.log('📂 发现保存的 Cookie，尝试恢复登录状态...');
        
        const browser = await chromium.launch({ 
            headless: false,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const context = await browser.newContext({
            viewport: { width: 1920, height: 1080 }
        });
        
        // 加载 Cookie
        const cookies = JSON.parse(fs.readFileSync(cookieFile, 'utf8'));
        await context.addCookies(cookies);
        console.log('✅ 已加载 Cookie:', cookies.length, '个');
        
        // 打开页面
        const page = await context.newPage();
        await page.goto('https://creator.xiaohongshu.com/', { 
            waitUntil: 'networkidle',
            timeout: 30000 
        });
        
        await page.waitForTimeout(3000);
        
        // 截图确认登录状态
        await page.screenshot({ 
            path: '/root/.openclaw/workspace/xiaohongshu-persisted.png',
            fullPage: true 
        });
        
        console.log('');
        console.log('✅ 登录状态已恢复！');
        console.log('📁 截图: xiaohongshu-persisted.png');
        console.log('');
        console.log('💡 浏览器保持打开，登录状态持续有效');
        console.log('按 Ctrl+C 停止');
        
        // 保持浏览器打开
        await new Promise(() => {});
        
    } else {
        console.log('❌ 未找到 Cookie 文件');
        console.log('请先登录一次以保存 Cookie');
    }
})();
