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
    
    await page.waitForTimeout(3000);
    
    // 输入手机号
    console.log('📱 输入手机号...');
    const inputs = await page.$$('input');
    for (const input of inputs) {
        const placeholder = await input.getAttribute('placeholder') || '';
        if (placeholder.includes('手机')) {
            await input.fill('16621600217');
            console.log('✅ 已输入手机号');
            break;
        }
    }
    
    // 点击"发送验证码"
    console.log('🔍 查找发送验证码按钮...');
    const buttons = await page.$$('button');
    
    for (const btn of buttons) {
        const text = await btn.innerText() || '';
        if (text.includes('发送验证码') || text.includes('获取验证码')) {
            console.log('✅ 找到验证码按钮: "' + text.trim() + '"');
            await btn.click();
            console.log('✅ 已点击发送验证码');
            break;
        }
    }
    
    await page.waitForTimeout(2000);
    
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-sent.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 验证码已发送!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-sent.png');
    console.log('');
    console.log('💡 等待验证码...');
    
    await new Promise(() => {});
})();
