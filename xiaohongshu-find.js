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
    
    console.log('🔍 分析页面结构...');
    
    // 获取所有按钮
    const buttons = await page.$$('button');
    console.log('按钮数量:', buttons.length);
    
    for (let i = 0; i < buttons.length; i++) {
        const text = await buttons[i].innerText() || '';
        const html = await buttons[i].innerHTML() || '';
        if (text.trim() || html.includes('qr') || html.includes('QR')) {
            console.log(`按钮 ${i}: "${text.trim()}"`);
        }
    }
    
    // 获取所有可点击元素
    const clickables = await page.$$('[role="button"], [class*="btn"], [class*="button"]');
    console.log('可点击元素:', clickables.length);
    
    // 截图
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-analyze.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 截图已保存: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-analyze.png');
    
    await new Promise(() => {});
})();
