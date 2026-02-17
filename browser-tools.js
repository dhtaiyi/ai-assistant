/**
 * 浏览器工具包 - Playwright
 * 支持: Chromium, Firefox
 * 功能: 截图, 采集, 登录, AI控制
 */

const { chromium, firefox } = require('playwright');
const stealth = require('playwright-stealth');

class BrowserTools {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
    }
    
    // 启动浏览器
    async launch(options = {}) {
        const { headless = true, browser = 'chromium' } = options;
        
        console.log(`🚀 启动 ${browser} 浏览器...`);
        
        if (browser === 'firefox') {
            this.browser = await firefox.launch({ headless });
        } else {
            this.browser = await chromium.launch({ 
                headless,
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            });
        }
        
        this.context = await this.browser.newContext({
            viewport: { width: 1280, height: 800 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        });
        
        // 应用 stealth
        this.context.addInitScript(() => {
            require('playwright-stealth').stealth();
        });
        
        this.page = await this.context.newPage();
        console.log('✅ 浏览器已启动');
    }
    
    // 截图
    async screenshot(url, filename = 'screenshot.png') {
        await this.page.goto(url, { waitUntil: 'networkidle' });
        await this.page.screenshot({ path: filename });
        console.log(`📸 截图已保存: ${filename}`);
    }
    
    // 获取页面内容
    async getContent(selector = 'body') {
        return await this.page.$eval(selector, el => el.innerText);
    }
    
    // 关闭
    async close() {
        if (this.browser) {
            await this.browser.close();
            console.log('🔒 浏览器已关闭');
        }
    }
    
    // 登录小红书
    async loginXiaohongshu() {
        console.log('🔐 打开小红书登录页...');
        await this.page.goto('https://creator.xiaohongshu.com/', { waitUntil: 'networkidle' });
    }
    
    // 滚动页面
    async scroll(direction = 'down', pixels = 500) {
        if (direction === 'down') {
            await this.page.evaluate(y => window.scrollBy(0, y), pixels);
        } else {
            await this.page.evaluate(y => window.scrollBy(0, -y), pixels);
        }
    }
    
    // 点击元素
    async click(selector) {
        await this.page.click(selector);
    }
    
    // 输入文本
    async type(selector, text) {
        await this.page.fill(selector, text);
    }
}

module.exports = BrowserTools;
