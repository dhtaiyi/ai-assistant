const { chromium } = require('playwright');
const fs = require('fs');

async function testWithCookie() {
  // 读取保存的 cookie
  let cookies = [];
  try {
    const cookieData = fs.readFileSync('/root/.openclaw/workspace/xiaohongshu-cookies.json', 'utf-8');
    const cookieObj = JSON.parse(cookieData);
    cookies = cookieObj.map(c => ({
      name: c.name,
      value: c.value,
      domain: c.domain,
      path: c.path,
      expires: c.expires,
      httpOnly: c.httpOnly,
      secure: c.secure,
      sameSite: c.sameSite
    }));
    console.log('✅ 读取到', cookies.length, '个 Cookie');
  } catch (e) {
    console.log('❌ Cookie 读取失败:', e.message);
  }
  
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
  });
  
  // 添加 Cookie
  if (cookies.length > 0) {
    await context.addCookies(cookies);
    console.log('✅ Cookie 已添加');
  }
  
  const page = await context.newPage();
  
  try {
    console.log('正在访问小红书...');
    await page.goto('https://www.xiaohongshu.com/', { timeout: 30000, waitUntil: 'networkidle' });
    
    await page.waitForTimeout(3000);
    
    console.log('✅ 页面加载成功');
    console.log('标题:', await page.title());
    
    // 检查是否已登录
    const isLoggedIn = await page.evaluate(() => {
      return document.querySelector('.user-name') !== null || 
             document.querySelector('[class*="user"]') !== null;
    });
    
    console.log('登录状态:', isLoggedIn ? '✅ 已登录' : '❌ 未登录');
    
  } catch (e) {
    console.log('❌ 加载失败:', e.message);
  }
  
  await browser.close();
}

testWithCookie();
