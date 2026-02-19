// OpenClaw 浏览器控制 - 后台服务
// 处理所有浏览器控制命令

let currentTab = null;

// 监听popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'execute') {
        executeCommand(request.command)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }
    
    if (request.action === 'getStatus') {
        sendResponse(getStatus());
        return true;
    }
});

// 获取状态
function getStatus() {
    return {
        success: true,
        tabId: currentTab?.id,
        url: currentTab?.url,
        title: currentTab?.title
    };
}

// 执行命令
async function executeCommand(command) {
    const { type, ...params } = command;
    
    try {
        switch (type) {
            case 'navigate':
                return await navigate(params.url);
            case 'click':
                return await click(params.selector);
            case 'type':
                return await type(params.selector, params.text);
            case 'scroll':
                return await scroll(params.direction, params.amount);
            case 'wait':
                return await wait(params.duration);
            case 'getHTML':
                return await getHTML();
            case 'getText':
                return await getText(params.selector);
            case 'getStockData':
                return await getStockData();
            case 'evaluate':
                return await evaluate(params.code);
            case 'getPageInfo':
                return await getPageInfo();
            case 'findElements':
                return await findElements(params.selector);
            case 'getAllText':
                return await getAllText();
            case 'getScreenshot':
                return await getScreenshot();
            case 'getCookies':
                return await getCookies();
            default:
                return { success: false, error: '未知命令: ' + type };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// 导航
async function navigate(url) {
    if (url === 'current') {
        const tab = await getActiveTab();
        await chrome.tabs.reload(tab.id);
        currentTab = tab;
        return { success: true, action: 'reloaded', url: tab.url };
    }
    
    const [tab] = await chrome.tabs.create({ url, active: true });
    currentTab = tab;
    return { success: true, action: 'navigated', tabId: tab.id, url };
}

// 点击
async function click(selector) {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector) => {
            const el = document.querySelector(selector);
            if (!el) return { success: false, error: '元素未找到: ' + selector };
            el.click();
            return { success: true, clicked: selector };
        },
        args: [selector]
    });
    return results[0]?.result || { success: false };
}

// 输入
async function type(selector, text) {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector, text) => {
            const el = document.querySelector(selector);
            if (!el) return { success: false, error: '元素未找到: ' + selector };
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return { success: true, typed: selector };
        },
        args: [selector, text]
    });
    return results[0]?.result || { success: false };
}

// 滚动
async function scroll(direction, amount) {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (direction, amount) => {
            const directions = {
                'up': [0, -amount],
                'down': [0, amount],
                'top': [0, 0],
                'bottom': [0, -999999]
            };
            const [x, y] = directions[direction] || directions.down;
            window.scrollTo(x, y);
            return { success: true };
        },
        args: [direction, amount || 500]
    });
    return results[0]?.result || { success: false };
}

// 等待
async function wait(duration) {
    await new Promise(r => setTimeout(r, duration));
    return { success: true, waited: duration };
}

// 获取HTML
async function getHTML() {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.body.innerHTML.substring(0, 50000)
    });
    return { success: true, html: results[0]?.result || '' };
}

// 获取文本
async function getText(selector) {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector) => {
            const el = document.querySelector(selector);
            if (!el) return { success: false, error: '元素未找到' };
            return { success: true, text: el.innerText.trim(), html: el.innerHTML.trim() };
        },
        args: [selector]
    });
    return results[0]?.result || { success: false };
}

// 获取股票数据（同花顺）
async function getStockData() {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            const data = {
                timestamp: new Date().toISOString(),
                url: location.href,
                title: document.title,
                prices: []
            };
            
            // 价格选择器列表
            const priceSelectors = [
                '.stock-price .price',
                '#quotation-entry .price',
                '.current-price',
                '.stock-current .price',
                '.hq-price .price',
                '.stock-info .price',
                '[class*="price"]',
                '.quote-price',
                '.stock-summary .price'
            ];
            
            // 涨跌幅选择器列表
            const changeSelectors = [
                '.stock-change .change',
                '#quotation-entry .change',
                '.change-percent',
                '.stock-current .change',
                '.hq-change',
                '[class*="change"]'
            ];
            
            // 查找价格
            for (const sel of priceSelectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText.trim()) {
                    data.prices.push({
                        selector: sel,
                        value: el.innerText.trim(),
                        tag: el.tagName
                    });
                }
            }
            
            // 查找涨跌幅
            for (const sel of changeSelectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText.trim()) {
                    data.change = el.innerText.trim();
                    data.changeSelector = sel;
                    break;
                }
            }
            
            // 如果没找到，尝试查找所有数字
            if (data.prices.length === 0) {
                document.querySelectorAll('span, div, td').forEach(el => {
                    const text = el.innerText?.trim();
                    if (text && /^\d+\.?\d*$/.test(text) && text.length < 15) {
                        data.prices.push({
                            value: text,
                            tag: el.tagName,
                            class: el.className?.substring(0, 30) || ''
                        });
                    }
                });
                data.prices = data.prices.slice(0, 10);
            }
            
            return data;
        }
    });
    return results[0]?.result || { success: false, error: '获取失败' };
}

// 执行JavaScript
async function evaluate(code) {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (code) => {
            try {
                const result = eval(code);
                return { success: true, result: String(result) };
            } catch (e) {
                return { success: false, error: e.message };
            }
        },
        args: [code]
    });
    return results[0]?.result || { success: false };
}

// 获取页面信息
async function getPageInfo() {
    const tab = await getActiveTab();
    return { success: true, title: tab.title, url: tab.url, id: tab.id };
}

// 查找元素
async function findElements(selector) {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector) => {
            const elements = document.querySelectorAll(selector);
            const found = [];
            elements.forEach((el, i) => {
                if (i < 20) {
                    found.push({
                        index: i,
                        tagName: el.tagName,
                        text: el.innerText?.substring(0, 100) || '',
                        className: el.className?.substring(0, 50) || '',
                        id: el.id || '',
                        visible: el.offsetParent !== null
                    });
                }
            });
            return found;
        },
        args: [selector]
    });
    return { success: true, elements: results[0]?.result || [] };
}

// 获取所有文本
async function getAllText() {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            const texts = [];
            document.querySelectorAll('span, div, td, p, h1, h2, h3, h4, h5, h6').forEach(el => {
                const text = el.innerText?.trim();
                if (text && text.length > 0 && text.length < 50) {
                    texts.push({
                        text: text,
                        tag: el.tagName
                    });
                }
            });
            return texts.slice(0, 100);
        }
    });
    return { success: true, texts: results[0]?.result || [] };
}

// 截图
async function getScreenshot() {
    const tab = await getActiveTab();
    const dataUrl = await chrome.tabs.captureVisibleTab();
    return { success: true, screenshot: dataUrl.substring(0, 100) + '...[base64]' };
}

// 获取Cookies
async function getCookies() {
    const tab = await getActiveTab();
    const url = new URL(tab.url);
    const cookies = await chrome.cookies.getAll({ url: url.origin });
    return { success: true, cookies };
}

// 获取活动标签页
async function getActiveTab() {
    try {
        if (currentTab?.id) {
            return await chrome.tabs.get(currentTab.id);
        }
    } catch (e) {}
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) currentTab = tab;
    return tab;
}
