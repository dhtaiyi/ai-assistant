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
    
    // 等待二维码加载 (小红书可能需要更长的时间)
    console.log('⏳ 等待二维码加载...');
    await page.waitForTimeout(10000);
    
    // 使用 JavaScript 查找所有 canvas 和二维码元素
    const pageInfo = await page.evaluate(() => {
        // 查找 canvas
        const canvases = document.querySelectorAll('canvas');
        const canvasInfo = Array.from(canvases).map(c => ({
            width: c.width,
            height: c.height,
            className: c.className,
            id: c.id
        }));
        
        // 查找所有图片
        const imgs = document.querySelectorAll('img');
        const imgInfo = Array.from(imgs).map(img => ({
            src: img.src.substring(0, 100),
            width: img.width,
            height: img.height,
            className: img.className
        })).filter(img => img.width > 50 && img.height > 50);  // 只保留较大的图片
        
        // 查找包含 qrcode 的元素
        const qrElements = document.querySelectorAll('*');
        const qrs = Array.from(qrElements).filter(el => {
            const html = el.outerHTML.toLowerCase();
            return html.includes('qrcode') || html.includes('qr-code') || html.includes('qr_code');
        }).map(el => ({
            tag: el.tagName,
            className: el.className,
            id: el.id
        }));
        
        return { canvasInfo, imgInfo: imgInfo.slice(0, 10), qrs: qrs.slice(0, 5) };
    });
    
    console.log('\n🔍 页面分析:');
    console.log('- Canvas 数量:', pageInfo.canvasInfo.length);
    console.log('- 大图片数量:', pageInfo.imgInfo.length);
    console.log('- QR元素:', pageInfo.qrs.length);
    
    if (pageInfo.imgInfo.length > 0) {
        console.log('\n📷 大图片列表:');
        pageInfo.imgInfo.forEach((img, i) => {
            console.log(`  ${i+1}. ${img.width}x${img.height} - ${img.src.substring(0, 60)}...`);
        });
    }
    
    // 截取包含二维码的区域 (通常是页面右侧或中间)
    console.log('\n📸 截取可能包含二维码的区域...');
    
    // 尝试找到登录表单区域
    const loginForm = await page.$('form, .login, [class*="login"]');
    
    if (loginForm) {
        await loginForm.screenshot({ 
            path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-login-area.png' 
        });
        console.log('✅ 已截取登录区域');
    }
    
    // 截取页面中间区域 (二维码通常在这里)
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-center.png',
        clip: { x: 600, y: 100, width: 720, height: 700 }
    });
    console.log('✅ 已截取页面中央区域 (600, 100, 720, 700)');
    
    // 尝试对每个大图片截图
    for (let i = 0; i < Math.min(pageInfo.imgInfo.length, 5); i++) {
        const img = await page.$(`img[src="${pageInfo.imgInfo[i].src.substring(0, 100)}"]`);
        if (img) {
            try {
                await img.screenshot({ 
                    path: `/home/dhtaiyi/.openclaw/workspace/xiaohongshu-img-${i+1}.png` 
                });
                console.log(`✅ 已截取图片 ${i+1}`);
            } catch (e) {}
        }
    }
    
    console.log('\n📁 生成的文件:');
    console.log('1. /home/dhtaiyi/.openclaw/workspace/xiaohongshu-full.png - 完整页面');
    if (loginForm) {
        console.log('2. /home/dhtaiyi/.openclaw/workspace/xiaohongshu-login-area.png - 登录区域');
    }
    console.log('3. /home/dhtaiyi/.openclaw/workspace/xiaohongshu-center.png - 中央区域');
    
    await browser.close();
})();
