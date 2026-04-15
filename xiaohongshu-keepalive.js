const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    console.log('🚀 恢复小红书登录状态...');
    
    const cookieFile = '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookies.json';
    
    if (!fs.existsSync(cookieFile)) {
        console.log('❌ Cookie 文件不存在');
        process.exit(1);
    }
    
    console.log('📂 加载 Cookie...');
    
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
    console.log('✅ 已加载', cookies.length, '个 Cookie');
    
    const page = await context.newPage();
    
    console.log('📱 打开小红书创作服务平台...');
    await page.goto('https://creator.xiaohongshu.com/', { 
        waitUntil: 'networkidle',
        timeout: 30000 
    });
    
    await page.waitForTimeout(3000);
    
    // 截图确认
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-restored.png',
        fullPage: true 
    });
    
    console.log('');
    console.log('✅ 登录状态已恢复！');
    console.log('📁 截图: xiaohongshu-restored.png');
    console.log('');
    console.log('💡 浏览器保持打开中...');
    console.log('按 Ctrl+C 停止');
    
    // 保持运行
    await new Promise(() => {});
})();
