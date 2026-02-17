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
    
    // 1. 填写手机号
    console.log('📝 填写手机号...');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await phoneInput.fill('16621600217');
        console.log('✅ 手机号已填写');
    }
    
    await page.waitForTimeout(1000);
    
    // 2. 点击发送验证码
    console.log('🔘 点击发送验证码...');
    const sendBtn = await page.$('button:has-text("发送验证码")');
    if (sendBtn) {
        await sendBtn.click();
        console.log('✅ 已点击发送验证码');
    }
    
    await page.waitForTimeout(3000);
    
    // 3. 填写验证码 847652
    console.log('🔢 填写验证码: 847652');
    const codeInput = await page.$('input[placeholder*="验证码"]');
    if (codeInput) {
        await codeInput.click();
        await codeInput.fill('847652');
        console.log('✅ 验证码已填写');
    } else {
        console.log('❌ 未找到验证码输入框');
    }
    
    await page.waitForTimeout(1000);
    
    // 4. 点击登录按钮
    console.log('🔘 点击登录按钮...');
    const loginBtn = await page.$('button:has-text("登 录")');
    if (loginBtn) {
        await loginBtn.click();
        console.log('✅ 已点击登录');
    }
    
    await page.waitForTimeout(5000);
    
    // 5. 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-success.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 完成! 登录中...');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-success.png');
    
    await new Promise(() => {});
})();
