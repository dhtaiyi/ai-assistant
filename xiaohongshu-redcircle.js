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
    
    // 先截图原始状态
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-before.png',
        fullPage: false 
    });
    
    // 根据用户标注，点击页面中间偏下的位置
    console.log('📍 点击标注位置...');
    
    // 先找到可能的切换按钮
    const tabs = await page.$$('[class*="tab"], [class*="switch"], button');
    console.log('找到的元素:', tabs.length);
    
    // 点击页面中间位置 (根据截图中的标注)
    await page.mouse.click(960, 480);
    
    await page.waitForTimeout(2000);
    
    // 截图点击后状态
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-after.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 点击完成!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-after.png');
    
    await new Promise(() => {});
})();
