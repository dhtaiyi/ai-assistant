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
        console.log('✅ 手机号已填写');
    }
    
    await page.waitForTimeout(1000);
    
    // 2. 点击发送验证码
    console.log('🔘 点击发送验证码 (1600, 535)...');
    await page.mouse.click(1600, 535);
    
    await page.waitForTimeout(3000);
    
    // 3. 填写验证码 417084
    console.log('🔢 填写验证码: 417084');
    const codeInput = await page.$('input[placeholder*="验证码"]');
    if (codeInput) {
        await codeInput.click();
        await codeInput.fill('417084');
        console.log('✅ 验证码已填写');
    }
    
    await page.waitForTimeout(1000);
    
    // 4. 点击登录按钮
    console.log('🔘 点击登录按钮 (1600, 650)...');
    await page.mouse.click(1600, 650);
    
    await page.waitForTimeout(5000);
    
    // 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-done.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 完成! 登录中...');
    console.log('验证码: 417084');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-done.png');
    
    await new Promise(() => {});
})();
