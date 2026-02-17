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
    
    // 截图原始状态
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-orig.png',
        fullPage: false 
    });
    
    console.log('📸 原始页面截图已保存');
    console.log('');
    print('💡 请告诉我点击位置的具体坐标或描述');
    
    await new Promise(() => {});
})();
