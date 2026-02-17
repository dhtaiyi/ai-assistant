const { chromium } = require('playwright');

async function testWithProxy() {
  const browser = await chromium.launch({
    headless: true,
    proxy: {
      server: 'http://127.0.0.1:13128',
      bypass: 'localhost'
    }
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  const page = await context.newPage();
  
  try {
    console.log('正在访问小红书...');
    await page.goto('https://www.xiaohongshu.com/explore', { timeout: 30000 });
    console.log('✅ 页面加载成功');
    console.log('标题:', await page.title());
    
    // 获取页面内容片段
    const content = await page.content();
    console.log('页面长度:', content.length);
    
  } catch (e) {
    console.log('❌ 加载失败:', e.message);
  }
  
  await browser.close();
}

testWithProxy();
