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
    
    // 截图原始状态
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-phone-orig.png',
        fullPage: false 
    });
    
    console.log('📍 切换到手机号登录模式...');
    
    // 尝试点击切换到手机号登录
    // 查找包含"手机号"的元素
    const phoneMode = await page.$('[class*="phone"], [class*="手机"], [class*="mobile"]');
    
    if (phoneMode) {
        console.log('✅ 找到手机号登录切换按钮');
        await phoneMode.click();
    } else {
        // 点击页面中上部位置（之前手机号登录的位置）
        await page.mouse.click(960, 380);
        console.log('✅ 点击页面位置');
    }
    
    await page.waitForTimeout(3000);
    
    // 截图切换后状态
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-phone-mode.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 切换完成!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-phone-mode.png');
    
    await new Promise(() => {});
})();
