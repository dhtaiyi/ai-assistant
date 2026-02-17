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
    
    console.log('📸 截图当前状态...');
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-now.png',
        fullPage: false 
    });
    
    // 获取所有输入框
    const inputs = await page.$$('input');
    console.log('\n📋 输入框数量:', inputs.length);
    
    // 获取所有按钮
    const buttons = await page.$$('button');
    console.log('📋 按钮数量:', buttons.length);
    
    console.log('\n📋 按钮列表:');
    for (let i = 0; i < Math.min(buttons.length, 10); i++) {
        const text = await buttons[i].innerText() || '';
        if (text.trim()) {
            console.log(`  ${i+1}. "${text.trim().substring(0, 20)}"`);
        }
    }
    
    console.log('\n✅ 截图已保存: /root/.openclaw/workspace/xiaohongshu-now.png');
    console.log('💡 请查看截图，告诉我当前状态');
    
    await new Promise(() => {});
})();
