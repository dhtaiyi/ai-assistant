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
    
    // 1. 点击手机号输入框
    console.log('📱 点击手机号输入框...');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        console.log('✅ 已点击输入框');
    }
    
    await page.waitForTimeout(500);
    
    // 2. 输入手机号
    console.log('📝 输入手机号: 16621600217');
    await page.keyboard.type('16621600217');
    console.log('✅ 已输入');
    
    await page.waitForTimeout(1000);
    
    // 3. 获取鼠标坐标
    const pos = await page.evaluate(() => {
        return {
            x: Math.round(window.mouseX || 0),
            y: Math.round(window.mouseY || 0),
            width: window.innerWidth,
            height: window.innerHeight
        };
    });
    
    // 也可以直接用 page.mouse 获取
    const mouse = page.mouse;
    const point = await mouse.position();
    
    console.log('');
    console.log('🎯 鼠标坐标:');
    console.log('   X:', point.x);
    console.log('   Y:', point.y);
    console.log('   屏幕: 1920x1080');
    
    // 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-coords.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 截图: /root/.openclaw/workspace/xiaohongshu-coords.png');
    
    await new Promise(() => {});
})();
