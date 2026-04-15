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
    
    console.log('⏳ 等待页面加载...');
    await page.waitForTimeout(5000);
    
    // 输入手机号
    console.log('📱 输入手机号...');
    
    // 查找手机号输入框
    const phoneInput = await page.$('input[type="tel"], input[placeholder*="手机"], input[name*="phone"]');
    
    if (phoneInput) {
        console.log('✅ 找到手机号输入框');
        await phoneInput.fill('16621600217');
        console.log('✅ 已输入: 16621600217');
        
        // 查找发送验证码按钮
        console.log('🔍 查找验证码按钮...');
        const sendBtn = await page.$('button:has-text("发送验证码"), button:has-text("获取验证码"), button[type="submit"]');
        
        if (sendBtn) {
            console.log('✅ 找到验证码按钮，点击...');
            await sendBtn.click();
            await page.waitForTimeout(2000);
            console.log('✅ 已发送验证码');
        } else {
            console.log('⚠️ 未找到验证码按钮');
        }
    } else {
        console.log('⚠️ 未找到手机号输入框');
    }
    
    // 截图确认
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-phone.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 已输入手机号，等待验证码...');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-phone.png');
    console.log('');
    console.log('💡 请告诉我收到的验证码');
    
    await new Promise(() => {});
})();
