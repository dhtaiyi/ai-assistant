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
    
    console.log('🔍 查找所有元素...');
    
    // 获取页面 HTML 分析
    const pageInfo = await page.evaluate(() => {
        const elements = [];
        
        // 查找所有 svg 元素 (三角形可能是 svg)
        document.querySelectorAll('svg').forEach(el => {
            elements.push({
                tag: 'svg',
                html: el.outerHTML.substring(0, 200),
                visible: el.offsetParent !== null
            });
        });
        
        // 查找所有图标类元素
        document.querySelectorAll('[class*="icon"], [class*="svg"], [class*="triangle"]').forEach(el => {
            if (el.offsetParent !== null) {
                elements.push({
                    tag: el.tagName,
                    className: el.className,
                    html: el.outerHTML.substring(0, 100)
                });
            }
        });
        
        return elements;
    });
    
    console.log('找到的元素:');
    pageInfo.forEach((el, i) => {
        console.log(`${i+1}. ${el.tag}: ${el.className || el.html.substring(0, 50)}`);
    });
    
    // 截图
    await page.screenshot({ 
        path: '/root/.openclaw/workspace/xiaohongshu-triangle.png',
        fullPage: false 
    });
    
    console.log('');
    console.log('✅ 截图: /root/.openclaw/workspace/xiaohongshu-triangle.png');
    
    await new Promise(() => {});
})();
