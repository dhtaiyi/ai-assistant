const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--proxy-server=http://localhost:13128',
      '--proxy-bypass-list=<-loopback>'
    ]
  });
  
  const page = await browser.newPage();
  
  // 访问同花顺
  await page.goto('https://stockpage.10jqka.com.cn/600519/', {
    timeout: 30000,
    waitUntil: 'domcontentloaded'
  });
  
  // 等待
  await page.waitForTimeout(3000);
  
  const data = await page.evaluate(() => {
    return {
      title: document.title,
      price: document.getElementById('hexm_curPrice')?.innerText
    };
  });
  
  console.log('标题:', data.title);
  console.log('价格:', data.price);
  
  await browser.close();
})();
