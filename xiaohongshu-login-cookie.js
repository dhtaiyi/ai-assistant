const { chromium } = require('playwright');
const fs = require('fs');

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
    
    await page.waitForTimeout(3000);
    
    // 1. 输入手机号
    console.log('📱 输入手机号: 16621600217');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await phoneInput.fill('16621600217');
        console.log('✅ 已输入手机号');
    }
    
    await page.waitForTimeout(1000);
    
    // 2. 点击发送验证码
    console.log('🔘 点击发送验证码 (1600, 535)...');
    await page.mouse.click(1600, 535);
    
    await page.waitForTimeout(3000);
    
    // 截图
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-wait-code.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 验证码已发送!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-wait-code.png');
    console.log('');
    console.log('💡 请在微信告诉我6位验证码');
    console.log('');
    console.log('我会：填写验证码 → 点击登录 → 保存Cookie');
    
    // 等待用户输入验证码后继续...
    console.log('');
    console.log('⏳ 等待验证码中...');
    
    await new Promise(() => {});
})();
