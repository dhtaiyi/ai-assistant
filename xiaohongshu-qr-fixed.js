const { chromium } = require('playwright');

(async () => {
    console.log('🚀 启动浏览器...');
    const browser = await chromium.launch({ 
        headless: true,
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
    
    // 等待页面完全加载
    await page.waitForTimeout(5000);
    
    console.log('📸 截图完整页面...');
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-full.png',
        fullPage: true 
    });
    
    // 尝试多种方式定位二维码
    console.log('🔍 查找二维码...');
    
    // 方法1: canvas 元素
    let qrEl = await page.$('canvas');
    
    // 方法2: img 标签 (二维码图片)
    if (!qrEl) {
        qrEl = await page.$('img[src*="qrcode"], img[src*="qr"]');
    }
    
    // 方法3: 包含 qrcode 的 div
    if (!qrEl) {
        qrEl = await page.$('[class*="qrcode"], [class*="qr-code"]');
    }
    
    // 方法4: 查找较大的图片
    if (!qrEl) {
        const imgs = await page.$$('img');
        for (const img of imgs) {
            const box = await img.boundingBox();
            if (box && box.width > 100 && box.height > 100) {
                qrEl = img;
                break;
            }
        }
    }
    
    if (qrEl) {
        console.log('✅ 找到二维码元素');
        await qrEl.screenshot({ 
            path: '/root/.openclaw/workspace/xiaohongshu-qr-only.png' 
        });
    } else {
        console.log('⚠️ 未找到二维码，保存完整页面');
    }
    
    console.log('');
    console.log('✅ 完成!');
    console.log('📁 完整页面: /root/.openclaw/workspace/xiaohongshu-full.png');
    if (qrEl) {
        console.log('📁 二维码: /root/.openclaw/workspace/xiaohongshu-qr-only.png');
    }
    
    await browser.close();
})();
