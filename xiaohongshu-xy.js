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
    
    // 点击输入框并输入手机号
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await page.keyboard.type('16621600217');
    }
    
    await page.waitForTimeout(1000);
    
    // 通过 JS 获取鼠标坐标
    const pos = await page.evaluate(() => {
        // Playwright 在无头模式下可能没有 mouseX/mouseY
        // 我们返回当前焦点元素的位置
        const active = document.activeElement;
        const rect = active ? active.getBoundingClientRect() : null;
        return {
            activeTag: active?.tagName,
            activePlaceholder: active?.placeholder,
            rect: rect ? {
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                w: Math.round(rect.width),
                h: Math.round(rect.height),
                centerX: Math.round(rect.x + rect.width/2),
                centerY: Math.round(rect.y + rect.height/2)
            } : null,
            viewport: {
                w: window.innerWidth,
                h: window.innerHeight
            }
        };
    });
    
    console.log('');
    console.log('🎯 鼠标/焦点位置:');
    console.log('   活动元素:', pos.activeTag, `(${pos.activePlaceholder})`);
    if (pos.rect) {
        console.log('   元素位置: X=', pos.rect.x, 'Y=', pos.rect.y);
        console.log('   元素中心: X=', pos.rect.centerX, 'Y=', pos.rect.centerY);
        console.log('   元素大小: W=', pos.rect.w, 'H=', pos.rect.h);
    }
    console.log('   视口大小:', pos.viewport.w, 'x', pos.viewport.h);
    console.log('');
    
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-xy.png',
        fullPage: false 
    });
    
    console.log('✅ 截图: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-xy.png');
    
    await new Promise(() => {});
})();
