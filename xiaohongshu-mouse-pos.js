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
    console.log('✅ 已输入手机号');
    
    await page.waitForTimeout(1000);
    
    // 3. 获取鼠标当前位置
    const mousePos = await page.mouse;
    console.log('📍 鼠标位置:', mousePos);
    
    // 截图
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-mouse.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 截图已保存!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-mouse.png');
    console.log('');
    console.log('💡 鼠标在输入手机号后停留在输入框内');
    
    await new Promise(() => {});
})();
