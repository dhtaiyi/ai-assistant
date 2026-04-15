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
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
    extraHTTPHeaders: {
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
      'Referer': 'https://www.xiaohongshu.com/',
    }
  });
  
  const page = await context.newPage();
  
  // 添加随机的鼠标移动和滚动来模拟真人行为
  await page.addInitScript(() => {
    window.navigator.webdriver = false;
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
  });
  
  try {
    console.log('正在访问小红书首页...');
    await page.goto('https://www.xiaohongshu.com/', { timeout: 30000, waitUntil: 'networkidle' });
    
    // 模拟滚动
    await page.evaluate(() => window.scrollBy(0, 500));
    await page.waitForTimeout(2000);
    
    console.log('✅ 页面加载成功');
    console.log('标题:', await page.title());
    
    // 检查是否有验证
    const content = await page.content();
    if (content.includes('验证') || content.includes('Security')) {
      console.log('⚠️ 检测到安全验证页面');
    } else {
      console.log('🎉 成功绕过风控！');
    }
    
  } catch (e) {
    console.log('❌ 加载失败:', e.message);
  }
  
  await browser.close();
}

testWithProxy();
