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
        console.log('✅ 已输入手机号');
    }
    
    await page.waitForTimeout(1000);
    
    // 点击按钮 (1600, 495)
    console.log('🔘 点击按钮 (1600, 495)...');
    await page.mouse.click(1600, 495);
    
    await page.waitForTimeout(1000);
    
    // 截图（不做任何标记）
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-raw.png',
        fullPage: false 
    });
    
    console.log('✅ 原始截图已保存');
    
    await new Promise(() => {});
})();
