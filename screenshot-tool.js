/**
 * 简单截图工具
 */

const { chromium } = require('playwright');

(async () => {
    const url = process.argv[2] || 'https://www.baidu.com';
    const filename = process.argv[3] || 'screenshot.png';
    
    console.log(`📸 截图: ${url} → ${filename}`);
    
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.screenshot({ path: filename, fullPage: true });
    
    console.log('✅ 完成!');
    await browser.close();
})();
