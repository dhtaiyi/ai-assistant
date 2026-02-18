const { chromium } = require('playwright');

async function crawlTonghuashun(stockCode) {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    const page = await context.newPage();
    
    try {
        // 访问同花顺个股页面
        const url = `https://quote.tushare.cn/quote/stock_detail?symbol=${stockCode}`;
        console.log(`📊 正在抓取 ${stockCode}...`);
        
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
        
        // 等待页面加载
        await page.waitForTimeout(3000);
        
        // 获取股票名称
        const name = await page.title();
        
        // 获取价格信息
        const price = await page.$eval('.stock-price .price', el => el.textContent).catch(() => 'N/A');
        
        // 获取涨跌幅
        const change = await page.$eval('.stock-price .change', el => el.textContent).catch(() => 'N/A');
        
        console.log(`\n✅ 获取成功!`);
        console.log(`股票: ${name}`);
        console.log(`价格: ${price}`);
        console.log(`涨跌: ${change}`);
        
    } catch (error) {
        console.log(`❌ 抓取失败: ${error.message}`);
    } finally {
        await browser.close();
    }
}

// 如果直接运行
const stockCode = process.argv[2] || '600519';
crawlTonghuashun(stockCode);
