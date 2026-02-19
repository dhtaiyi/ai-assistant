// OpenClaw Browser Control - 后台服务
// 处理来自popup和control-panel的浏览器控制命令

let currentTab = null;
let commandQueue = [];

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // 来自popup或control-panel
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
    
    if (request.action === 'executeOnTab') {
        // control-panel请求在指定标签页执行
        executeCommandOnTab(request.tabId, request.command)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }
});

// 获取状态
function getStatus() {
    return {
        success: true,
        tabId: currentTab?.id,
        url: currentTab?.url,
        title: currentTab?.title,
        queueLength: commandQueue.length,
        timestamp: Date.now()
    };
}

// 在指定标签页执行命令
async function executeCommandOnTab(tabId, command) {
    const results = await chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: (cmd) => {
            // 在页面中执行的命令
            const { type, ...params } = cmd;
            
            if (type === 'getHTML') {
                return { success: true, html: document.body.innerHTML.substring(0, 50000) };
            }
            
            if (type === 'getText') {
                const el = document.querySelector(params.selector);
                return { success: true, text: el?.innerText?.trim() || '' };
            }
            
            if (type === 'getStockData') {
                const selectors = {
                    price: '.stock-price .price, #quotation-entry .price, .current-price',
                    change: '.stock-change .change, #quotation-entry .change'
                };
                const priceEl = document.querySelector(selectors.price);
                const changeEl = document.querySelector(selectors.change);
                return {
                    success: true,
                    data: {
                        timestamp: new Date().toISOString(),
                        price: priceEl?.innerText?.trim() || '未找到',
                        change: changeEl?.innerText?.trim() || '未找到'
                    }
                };
            }
            
            if (type === 'evaluate') {
                try {
                    return { success: true, result: String(eval(params.code)) };
                } catch (e) {
                    return { success: false, error: e.message };
                }
            }
            
            return { success: false, error: '未知命令: ' + type };
        },
        args: [command]
    });
    
    return results[0]?.result || { success: false, error: '执行失败' };
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
            case 'evaluate':
                return await evaluate(params.code);
            case 'getPageInfo':
                return await getPageInfo();
            case 'extractData':
                return await extractData(params.selector);
            case 'getStockData':
                return await getStockData();
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
        // 刷新当前页面
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
    return results[0]?.result || { success: false, error: '执行失败' };
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
    return results[0]?.result || { success: false, error: '执行失败' };
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
                'bottom': [0, document.body.scrollHeight]
            };
            const [x, y] = directions[direction] || directions['down'];
            window.scrollTo(x, y);
            return { success: true, direction, amount };
        },
        args: [direction, amount]
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
        func: () => document.body.innerHTML.substring(0, 100000)
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
    return results[0]?.result || { success: false, error: '执行失败' };
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
    return results[0]?.result || { success: false, error: '执行失败' };
}

// 获取页面信息
async function getPageInfo() {
    const tab = await getActiveTab();
    return {
        success: true,
        title: tab.title,
        url: tab.url,
        id: tab.id
    };
}

// 提取数据
async function extractData(selector) {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector) => {
            const elements = document.querySelectorAll(selector);
            const data = [];
            elements.forEach((el, i) => {
                if (i < 50) {
                    data.push({
                        index: i,
                        tagName: el.tagName,
                        text: el.innerText?.substring(0, 200) || '',
                        className: el.className?.substring(0, 100) || ''
                    });
                }
            });
            return data;
        },
        args: [selector]
    });
    return { success: true, data: results[0]?.result || [] };
}

// 获取股票数据
async function getStockData() {
    const tab = await getActiveTab();
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            const data = { timestamp: new Date().toISOString() };
            
            // 价格选择器
            const priceSel = '.stock-price .price, #quotation-entry .price, .current-price, .stock-current .price, .hq-price .price';
            // 涨跌幅选择器
            const changeSel = '.stock-change .change, #quotation-entry .change, .change-percent, .stock-current .change, .hq-change';
            
            const priceEl = document.querySelector(priceSel);
            const changeEl = document.querySelector(changeSel);
            
            data.price = priceEl?.innerText?.trim() || '未找到';
            data.change = changeEl?.innerText?.trim() || '未找到';
            
            // 查找所有数字（可能是价格）
            const allNumbers = [];
            document.querySelectorAll('span, div, td').forEach(el => {
                const text = el.innerText?.trim();
                if (text && /^\d+\.?\d*$/.test(text) && text.length < 15) {
                    allNumbers.push({ value: text, tag: el.tagName });
                }
            });
            data.allNumbers = allNumbers.slice(0, 30);
            
            return data;
        }
    });
    return results[0]?.result || { success: false, error: '获取失败' };
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
