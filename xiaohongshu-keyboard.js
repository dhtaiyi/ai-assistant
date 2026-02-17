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
    
    // 1. 点击手机号输入框
    console.log('📱 点击手机号输入框...');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        console.log('✅ 已点击输入框');
    }
    
    await page.waitForTimeout(1000);
    
    // 2. 输入手机号
    console.log('📝 输入手机号: 16621600217');
    await page.keyboard.type('16621600217');
    console.log('✅ 已输入手机号');
    
    await page.waitForTimeout(1000);
    
    // 3. 按两次 Tab
    console.log('🔘 按 Tab 键...');
    await page.keyboard.press('Tab');
    await page.waitForTimeout(500);
    await page.keyboard.press('Tab');
    console.log('✅ 已按两次 Tab');
    
    await page.waitForTimeout(500);
    
    // 4. 按空格键
    console.log('🔘 按空格键...');
    await page.keyboard.press('Space');
    console.log('✅ 已按空格键');
    
    await page.waitForTimeout(3000);
    
    // 5. 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-keyboard.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 完成!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-keyboard.png');
    
    await new Promise(() => {});
})();
