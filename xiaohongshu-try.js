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
    
    console.log('\n🔍 检查页面...');
    
    // 查找手机号输入框
    console.log('查找 input[placeholder="手机号"]...');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    
    if (phoneInput) {
        console.log('✅ 找到手机号输入框');
        await phoneInput.click();
        await phoneInput.fill('16621600217');
        await phoneInput.dispatchEvent('input');
        console.log('✅ 已填写: 16621600217');
    } else {
        console.log('❌ 未找到');
    }
    
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-try.png',
        fullPage: false 
    });
    
    console.log('\n✅ 完成');
    
    await new Promise(() => {});
})();
