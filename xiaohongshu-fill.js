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
    
    // 点击输入框并填写手机号
    console.log('📱 填写手机号...');
    
    await page.evaluate(() => {
        // 查找所有输入框
        const inputs = document.querySelectorAll('input');
        for (const input of inputs) {
            // 找到父元素包含"手机号"的输入框
            let parent = input.parentElement;
            while (parent && parent.tagName !== 'BODY') {
                if (parent.innerText && parent.innerText.includes('手机号')) {
                    // 点击输入框
                    input.click();
                    input.focus();
                    // 填写手机号
                    input.value = '16621600217';
                    // 触发事件
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log('✅ 已填写手机号');
                    break;
                }
                parent = parent.parentElement;
            }
        }
    });
    
    await page.waitForTimeout(2000);
    
    // 截图确认
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-filled.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 截图已保存: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-filled.png');
    console.log('');
    console.log('💡 请查看截图，确认手机号是否正确填写');
    
    await new Promise(() => {});
})();
