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
    
    console.log('📱 打开小红书创作服务平台...');
    await page.goto('https://creator.xiaohongshu.com/', { 
        waitUntil: 'networkidle',
        timeout: 30000 
    });
    
    await page.waitForTimeout(5000);
    
    // 刷新页面几次确保加载
    console.log('🔄 刷新页面...');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(5000);
    
    console.log('📸 截图...');
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-fresh.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 完成!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-fresh.png');
    
    await new Promise(() => {});
})();
