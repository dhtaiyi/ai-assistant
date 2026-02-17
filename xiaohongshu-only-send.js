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
    console.log('📝 填写手机号: 16621600217');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await phoneInput.fill('16621600217');
        console.log('✅ 手机号已填写');
    }
    
    await page.waitForTimeout(2000);
    
    // 2. 只点击"发送验证码"按钮（不是登录按钮）
    console.log('🔘 点击发送验证码按钮...');
    const sendBtn = await page.$('button:has-text("发送验证码")');
    if (sendBtn) {
        await sendBtn.click();
        console.log('✅ 已点击发送验证码按钮');
    } else {
        console.log('❌ 未找到发送验证码按钮');
    }
    
    await page.waitForTimeout(3000);
    
    // 3. 截图（不要点击登录）
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-just-send.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 只点击了发送验证码!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-just-send.png');
    console.log('');
    console.log('💡 请查看手机验证码');
    
    await new Promise(() => {});
})();
