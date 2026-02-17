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
    
    // 截图当前状态
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-home.png',
        fullPage: true 
    });
    
    console.log('');
    console.log('✅ 已打开首页');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-home.png');
    console.log('');
    console.log('💡 请查看截图，告诉我"发布笔记"按钮的位置');
    
    await new Promise(() => {});
})();
