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
    
    // 1. 输入手机号 (右边中间输入框)
    console.log('📱 输入手机号...');
    
    // 使用 JavaScript 直接定位
    const phoneResult = await page.evaluate(() => {
        const inputs = document.querySelectorAll('input');
        let phoneInput = null;
        let codeInput = null;
        
        for (const input of inputs) {
            const parent = input.parentElement;
            if (parent && parent.innerText.includes('手机号')) {
                phoneInput = input;
            }
            if (parent && parent.innerText.includes('验证码')) {
                codeInput = input;
            }
        }
        
        return { phoneInput: !!phoneInput, codeInput: !!codeInput };
    });
    
    console.log('手机号输入框:', phoneResult.phoneInput ? '✅' : '❌');
    console.log('验证码输入框:', phoneResult.codeInput ? '✅' : '❌');
    
    // 使用 JavaScript 直接操作 DOM
    await page.evaluate(() => {
        const inputs = document.querySelectorAll('input');
        for (const input of inputs) {
            const parent = input.parentElement;
            if (parent && parent.innerText.includes('手机号')) {
                input.value = '16621600217';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    });
    
    console.log('✅ 已输入手机号');
    
    // 截图确认
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-layout.png',
        fullPage: false 
    });
    
    // 查找并点击发送验证码按钮
    console.log('🔍 查找发送验证码按钮...');
    await page.evaluate(() => {
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.innerText.includes('发送验证码')) {
                btn.click();
                console.log('✅ 已点击发送验证码');
            }
        }
    });
    
    await page.waitForTimeout(2000);
    
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-code-sent.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 验证码已发送!');
    console.log('📁 /root/.openclaw/workspace/xiaohongshu-code-sent.png');
    console.log('');
    console.log('💡 请告诉我收到的验证码');
    
    await new Promise(() => {});
})();
