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
    
    // 使用 Playwright 直接填写
    console.log('📱 填写手机号...');
    
    // 找到 placeholder="手机号" 的输入框
    const phoneInput = await page.$('input[placeholder="手机号"]');
    
    if (phoneInput) {
        console.log('✅ 找到手机号输入框');
        
        // 点击并填写
        await phoneInput.click();
        await phoneInput.fill('16621600217');
        await phoneInput.dispatchEvent('input');
        
        console.log('✅ 已填写: 16621600217');
    } else {
        console.log('❌ 未找到手机号输入框');
    }
    
    await page.waitForTimeout(2000);
    
    // 截图确认
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-filled2.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 截图已保存');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-filled2.png');
    
    await new Promise(() => {});
})();
