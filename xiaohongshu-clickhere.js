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
    
    console.log('📱 填写手机号...');
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        await phoneInput.click();
        await phoneInput.fill('16621600217');
        console.log('✅ 已填写手机号');
    }
    
    // 点击用户指定的位置 (需要根据图片中的坐标)
    // 用户说点击"这个位置"，我假设在页面中间某个位置
    console.log('📍 点击指定位置...');
    
    // 先截图标记点击位置
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-before-click.png',
        fullPage: false 
    });
    
    // 尝试点击页面中间区域
    await page.mouse.click(960, 400);  // 中间偏上位置
    
    await page.waitForTimeout(2000);
    
    // 点击发送验证码按钮
    console.log('🔍 点击发送验证码...');
    const sendBtn = await page.$('button:has-text("发送验证码")');
    if (sendBtn) {
        await sendBtn.click();
        console.log('✅ 已点击发送验证码');
    }
    
    await page.waitForTimeout(2000);
    
    // 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-after-click.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 完成!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-after-click.png');
    console.log('');
    console.log('💡 请查看截图');
    
    await new Promise(() => {});
})();
