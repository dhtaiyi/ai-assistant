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
    console.log('📱 输入手机号...');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await phoneInput.fill('16621600217');
        console.log('✅ 已输入手机号');
    }
    
    await page.waitForTimeout(1000);
    
    // 2. 点击发送验证码
    console.log('🔘 点击发送验证码...');
    await page.mouse.click(1600, 535);
    
    await page.waitForTimeout(3000);
    
    // 3. 填写验证码 927035
    console.log('🔢 填写验证码: 927035');
    const codeInput = await page.$('input[placeholder*="验证码"]');
    if (codeInput) {
        await codeInput.click();
        await codeInput.fill('927035');
        console.log('✅ 验证码已填写');
    }
    
    await page.waitForTimeout(1000);
    
    // 4. 点击登录按钮
    console.log('🔘 点击登录按钮 (1600, 660)...');
    await page.mouse.click(1600, 660);
    
    await page.waitForTimeout(5000);
    
    // 5. 保存 Cookie
    console.log('');
    console.log('💾 保存 Cookie...');
    const cookies = await context.cookies();
    fs.writeFileSync(
        '/root/.openclaw/workspace/xiaohongshu-cookies.json',
        JSON.stringify(cookies, null, 2)
    );
    console.log('✅ Cookie 已保存到: xiaohongshu-cookies.json');
    console.log('Cookie 数量:', cookies.length);
    
    await page.waitForTimeout(2000);
    
    // 6. 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-loggedin-cookie.png',
        fullPage: true 
    });
    
    console.log('');
    console.log('✅ 完成! 登录成功!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-loggedin-cookie.png');
    
    await new Promise(() => {});
})();
