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
        path: '/root/.openclaw/workspace/xiaohongshu-status.png',
        fullPage: false 
    });
    
    // 获取页面 HTML 结构
    const pageInfo = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.innerText.substring(0, 30),
            html: b.innerHTML.substring(0, 50)
        }));
        
        const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
            type: i.type,
            placeholder: i.placeholder,
            name: i.name
        }));
        
        return { buttons: buttons.slice(0, 10), inputs };
    });
    
    console.log('\n🔍 按钮列表:');
    pageInfo.buttons.forEach((b, i) => {
        if (b.text.trim()) console.log(`${i+1}. ${b.text}`);
    });
    
    console.log('\n🔍 输入框:');
    pageInfo.inputs.forEach(i => {
        console.log(`- ${i.type}: ${i.placeholder || i.name || 'unknown'}`);
    });
    
    console.log('\n✅ 截图已保存: /root/.openclaw/workspace/xiaohongshu-status.png');
    
    await new Promise(() => {});
})();
