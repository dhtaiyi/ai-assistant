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
    
    // 获取当前页面截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-当前.png',
        fullPage: false 
    });
    
    // 获取鼠标当前坐标位置的元素
    const element = await page.evaluate(() => {
        // 返回鼠标位置的元素信息
        return {
            url: window.location.href,
            title: document.title
        };
    });
    
    console.log('');
    console.log('✅ 当前页面已截图');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-当前.png');
    console.log('标题:', element.title);
    
    await new Promise(() => {});
})();
