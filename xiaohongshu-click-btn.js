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
    
    // 1. 输入手机号
    console.log('📱 输入手机号...');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await phoneInput.fill('16621600217');
        console.log('✅ 已输入手机号');
    }
    
    await page.waitForTimeout(1000);
    
    // 2. 点击按钮 (1600, 495)
    console.log('🔘 点击按钮 (1600, 495)...');
    await page.mouse.click(1600, 495);
    console.log('✅ 已点击');
    
    await page.waitForTimeout(3000);
    
    // 3. 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-clicked-btn.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 完成!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-clicked-btn.png');
    
    await new Promise(() => {});
})();
