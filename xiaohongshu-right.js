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
    
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await phoneInput.fill('16621600217');
    }
    
    await page.waitForTimeout(1000);
    
    await page.mouse.click(1600, 535);
    
    await page.waitForTimeout(3000);
    
    const codeInput = await page.$('input[placeholder*="验证码"]');
    if (codeInput) {
        await codeInput.click();
        await codeInput.fill('417084');
        console.log('✅ 验证码: 417084');
    }
    
    await page.waitForTimeout(1000);
    
    console.log('🔘 点击登录 (1600, 660)...');
    await page.mouse.click(1600, 660);
    
    await page.waitForTimeout(5000);
    
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-right-pos.png',
        fullPage: false 
    });
    
    console.log('✅ 完成!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-right-pos.png');
    
    await new Promise(() => {});
})();
