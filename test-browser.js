const { chromium } = require('playwright');

(async () => {
    console.log('启动浏览器...');
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    await page.goto('https://www.baidu.com');
    const title = await page.title();
    
    console.log('✅ 浏览器工作正常');
    console.log('页面标题:', title);
    
    await browser.close();
    process.exit(0);
})();
