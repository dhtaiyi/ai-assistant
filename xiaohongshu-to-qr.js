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
    
    await page.waitForTimeout(5000);
    
    // 截图二维码登录页面
    console.log('📸 截图二维码登录页面...');
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-mode.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 截图完成!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-mode.png');
    console.log('');
    console.log('💡 请标注红圈位置，我点击后重新截图');
    
    await new Promise(() => {});
})();
