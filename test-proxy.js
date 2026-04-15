const { chromium } = require('playwright');

async function testWithProxy() {
  const browser = await chromium.launch({
    headless: false,
    proxy: {
      server: 'http://127.0.0.1:13128',
      bypass: 'localhost'
    }
  });
  
  const page = await browser.newPage();
  
  try {
    await page.goto('https://www.xiaohongshu.com/explore', { timeout: 30000 });
    console.log('✅ 页面加载成功');
    console.log('标题:', await page.title());
  } catch (e) {
    console.log('❌ 加载失败:', e.message);
  }
  
  await browser.close();
}

testWithProxy();
