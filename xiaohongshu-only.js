const { chromium } = require('playwright');

(async () => {
    console.log('🚀 启动浏览器...');
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });
    
    const page = await context.newPage();
    
    console.log('📱 打开小红书...');
    await page.goto('https://creator.xiaohongshu.com/', { 
        waitUntil: 'networkidle',
        timeout: 30000 
    });
    
    await page.waitForTimeout(8000);
    
    console.log('📸 截图（不做任何点击）...');
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-only.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 完成! (未点击任何位置)');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-only.png');
    
    await new Promise(() => {});
})();
