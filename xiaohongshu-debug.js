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
    
    // 截图当前状态
    await page.screenshot({ 
        path: '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-debug.png',
        fullPage: false 
    });
    
    // 分析页面结构
    const pageInfo = await page.evaluate(() => {
        const result = {
            inputs: [],
            buttons: []
        };
        
        // 获取所有输入框
        const inputs = document.querySelectorAll('input');
        inputs.forEach((input, i) => {
            result.inputs.push({
                index: i,
                type: input.type,
                placeholder: input.placeholder || '',
                id: input.id || '',
                className: input.className || '',
                name: input.name || '',
                value: input.value || '',
                visible: input.offsetParent !== null
            });
        });
        
        // 获取所有按钮
        const buttons = document.querySelectorAll('button');
        buttons.forEach((btn, i) => {
            const text = btn.innerText || btn.textContent || '';
            if (text.trim()) {
                result.buttons.push({
                    index: i,
                    text: text.trim().substring(0, 20)
                });
            }
        });
        
        // 获取包含"手机号"的元素
        const allElements = document.querySelectorAll('*');
        const phoneElements = [];
        allElements.forEach((el, i) => {
            if (el.innerText && el.innerText.includes('手机号')) {
                phoneElements.push({
                    tag: el.tagName,
                    className: el.className,
                    innerText: el.innerText.substring(0, 50)
                });
            }
        });
        
        result.phoneElements = phoneElements.slice(0, 5);
        
        return result;
    });
    
    console.log('\n🔍 输入框分析:');
    pageInfo.inputs.forEach(i => {
        if (i.visible) {
            console.log(`  ${i.index}. type=${i.type} placeholder="${i.placeholder}" value="${i.value}"`);
        }
    });
    
    console.log('\n🔍 包含"手机号"的元素:');
    pageInfo.phoneElements.forEach(el => {
        console.log(`  - ${el.tagName}: ${el.innerText.substring(0, 30)}...`);
    });
    
    console.log('\n✅ 截图已保存: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-debug.png');
    
    await new Promise(() => {});
})();
