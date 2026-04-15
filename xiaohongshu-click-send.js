const { chromium } = require('playwright');

(async () => {
    console.log('🚀 连接浏览器...');
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
    
    // 检查当前状态
    const phoneInput = await page.$('input[placeholder="手机号"]');
    if (phoneInput) {
        const value = await phoneInput.inputValue();
        console.log('📱 手机号当前值:', value || '(空)');
        
        if (value !== '16621600217') {
            console.log('📝 重新填写手机号...');
            await phoneInput.fill('16621600217');
        }
    }
    
    // 点击"发送验证码"按钮
    console.log('🔍 查找发送验证码按钮...');
    
    // 尝试多种方式查找
    const sendCodeBtn = await page.$('button:has-text("发送验证码")');
    
    if (sendCodeBtn) {
        console.log('✅ 找到按钮，点击...');
        await sendCodeBtn.click();
    } else {
        // 查找包含验证码的按钮
        const allButtons = await page.$$('button');
        for (const btn of allButtons) {
            const text = await btn.innerText() || '';
            if (text.includes('验证码') && !text.includes('请输入')) {
                console.log('✅ 找到验证码按钮:', text.trim());
                await btn.click();
                break;
            }
        }
    }
    
    await page.waitForTimeout(3000);
    
    // 截图
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-code-sent.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 验证码已发送!');
    console.log('📁 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-code-sent.png');
    console.log('');
    console.log('💡 请查看手机，收到验证码后告诉我');
    
    await new Promise(() => {});
})();
