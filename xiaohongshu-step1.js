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
    
    // 2. 点击发送验证码
    console.log('🔘 点击发送验证码...');
    const sendBtn = await page.$('button:has-text("发送验证码")');
    if (sendBtn) {
        await sendBtn.click();
        console.log('✅ 已点击发送验证码');
    }
    
    await page.waitForTimeout(3000);
    
    // 3. 截图
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-step1.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 验证码已发送!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-step1.png');
    
    await new Promise(() => {});
})();
