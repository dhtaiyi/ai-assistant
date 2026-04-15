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
    
    // 输入手机号
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await phoneInput.fill('16621600217');
    }
    
    await page.waitForTimeout(500);
    
    // 点击发送验证码
    await page.mouse.click(1600, 535);
    
    await page.waitForTimeout(3000);
    
    // 填写验证码
    const codeInput = await page.$('input[placeholder*="验证码"]');
    if (codeInput) {
        await codeInput.click();
        await codeInput.fill('771141');
    }
    
    await page.waitForTimeout(1000);
    
    // 点击登录按钮 (1600, 600)
    console.log('🔘 点击登录按钮 (1600, 600)...');
    await page.mouse.click(1600, 600);
    
    await page.waitForTimeout(5000);
    
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-real-btn.png',
        fullPage: false 
    });
    
    console.log('✅ 完成!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-real-btn.png');
    
    await new Promise(() => {});
})();
