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
    
    // 点击用户标注的位置
    console.log('📍 点击标注位置...');
    await page.mouse.click(960, 420);
    
    await page.waitForTimeout(3000);
    
    // 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-clicked.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 点击完成!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-clicked.png');
    
    await new Promise(() => {});
})();
