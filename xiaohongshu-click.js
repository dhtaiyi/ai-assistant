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
    
    // 查找并点击"二维码登录"按钮
    console.log('🔍 查找二维码登录按钮...');
    
    const qrButton = await page.$('button:has-text("二维码"), [class*="qr"]:has-text("二维码"), .qrcode-btn, [class*="qrcode"]');
    
    if (qrButton) {
        console.log('✅ 找到二维码按钮，点击...');
        await qrButton.click();
        await page.waitForTimeout(3000);
    } else {
        // 尝试用 JavaScript 查找
        console.log('🔍 尝试其他方式查找...');
        
        // 查找包含"二维码"文本的元素
        const elements = await page.$$('button, div, span, a');
        for (const el of elements) {
            const text = await el.innerText().catch(() => '');
            if (text.includes('二维码') && text.length < 20) {
                console.log(`✅ 找到: "${text}"`);
                await el.click();
                await page.waitForTimeout(3000);
                break;
            }
        }
    }
    
    console.log('📸 截图完整二维码...');
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-final.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 截图完成!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-final.png');
    console.log('');
    console.log('💡 请扫码登录');
    
    // 保持打开
    await new Promise(() => {});
})();
