const { chromium } = require('playwright');

async function login() {
  const browser = await chromium.launch({
    headless: false,
    proxy: {
      server: 'http://127.0.0.1:13128',
      bypass: 'localhost'
    }
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    viewport: { width: 1280, height: 800 },
    locale: 'zh-CN',
  });
  
  const page = await context.newPage();
  
  console.log('正在打开小红书登录页...');
  await page.goto('https://www.xiaohongshu.com/explore', { timeout: 60000 });
  
  console.log('请在浏览器中手动登录...');
  console.log('手机号: 16621600217');
  
  // 等待用户手动登录
  await page.waitForTimeout(120000); // 等待2分钟
  
  // 保存 Cookie
  const cookies = await context.cookies();
  console.log('保存 Cookie 数量:', cookies.length);
  
  // 保存到文件
  const fs = require('fs');
  fs.writeFileSync('/root/.openclaw/workspace/xiaohongshu-cookies.json', JSON.stringify(cookies, null, 2));
  console.log('✅ Cookie 已保存到 xiaohongshu-cookies.json');
  
  await browser.close();
}

login();
