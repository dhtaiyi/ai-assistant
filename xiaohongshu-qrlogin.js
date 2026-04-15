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
    
    console.log('📸 截图完整页面...');
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-qrlogin.png',
        fullPage: true 
    });
    
    console.log('');
    console.log('✅ 截图完成!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-qrlogin.png');
    console.log('');
    console.log('💡 请用手机小红书扫描二维码登录');
    
    await new Promise(() => {});
})();
