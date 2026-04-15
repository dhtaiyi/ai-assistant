const { chromium } = require('playwright');

(async () => {
    console.log('🚀 启动浏览器...');
    const browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 }
    });
    
    const page = await context.newPage();
    
    console.log('📱 打开小红书...');
    await page.goto('https://creator.xiaohongshu.com/', { 
        waitUntil: 'networkidle',
        timeout: 30000 
    });
    
    // 等待二维码加载
    await page.waitForTimeout(3000);
    
    console.log('📸 截图完整页面...');
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-qrcode.png',
        fullPage: false 
    });
    
    // 尝试多种方式找二维码
    const selectors = [
        'canvas',
        '.qrcode',
        '[class*="qr"]',
        '[class*="code"]',
        'img[alt*="qr" i]',
        'img[alt*="code" i]'
    ];
    
    for (const sel of selectors) {
        const el = await page.$(sel);
        if (el) {
            console.log(`✅ 找到: ${sel}`);
            await el.screenshot({ 
                path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-only.png' 
            });
            break;
        }
    }
    
    console.log('');
    console.log('✅ 截图完成!');
    console.log('📁 完整页面: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-qrcode.png');
    console.log('📁 二维码: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-qr-only.png (如果有)');
    
    await browser.close();
})();
