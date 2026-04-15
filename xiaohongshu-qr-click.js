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
    
    // 查找短信登录按钮旁边的二维码按钮
    console.log('🔍 查找二维码按钮...');
    
    // 方法1: 查找包含二维码图标的按钮
    const qrIconBtn = await page.$('[class*="qr"], [class*="QR"], [class*="code"]');
    
    if (qrIconBtn) {
        console.log('✅ 找到二维码图标按钮，点击...');
        await qrIconBtn.click();
        await page.waitForTimeout(3000);
    } else {
        // 方法2: 查找短信登录按钮
        console.log('🔍 查找短信登录按钮旁边的二维码...');
        
        const smsBtn = await page.$('button:has-text("短信")');
        if (smsBtn) {
            // 查找附近的二维码图标
            const nearby = await smsBtn.$('..');
            if (nearby) {
                const qrNear = await nearby.$('[class*="qr"], svg[class*="qr"], img[class*="qr"]');
                if (qrNear) {
                    console.log('✅ 找到附近二维码，点击...');
                    await qrNear.click();
                    await page.waitForTimeout(3000);
                }
            }
        }
        
        // 方法3: 查找页面中所有按钮和图标
        if (!qrIconBtn) {
            console.log('🔍 遍历所有按钮...');
            const allButtons = await page.$$('button, [role="button"], .clickable');
            for (const btn of allButtons) {
                const html = await btn.innerHTML().catch(() => '');
                if (html.includes('qr') || html.includes('QR') || html.includes('svg')) {
                    console.log('✅ 找到QR相关元素，点击...');
                    await btn.click();
                    await page.waitForTimeout(3000);
                    break;
                }
            }
        }
    }
    
    // 等待二维码完全显示
    console.log('⏳ 等待二维码加载...');
    await page.waitForTimeout(5000);
    
    // 截图整个登录区域
    console.log('📸 截图完整二维码...');
    
    const loginForm = await page.$('.login, form, [class*="login"], [class*="auth"]');
    if (loginForm) {
        await loginForm.screenshot({ 
            path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-click.png' 
        });
        console.log('✅ 已截取登录区域');
    } else {
        await page.screenshot({ 
            path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-click.png',
            fullPage: false 
        });
        console.log('✅ 已截图');
    }
    
    console.log('');
    console.log('✅ 完成!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-click.png');
    
    await new Promise(() => {});
})();
