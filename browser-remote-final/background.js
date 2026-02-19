// OpenClaw Remote - Background Service
// 接收命令并执行

let commandQueue = [];
let lastCommandId = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'execute') {
        executeCommand(request.command)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }
    
    if (request.action === 'getStatus') {
        sendResponse({ success: true, queueLength: commandQueue.length });
        return true;
    }
    
    if (request.action === 'getCommand') {
        // 返回最早的命令
        const cmd = commandQueue.shift();
        sendResponse(cmd);
        return true;
    }
    
    if (request.action === 'reportResult') {
        // 报告结果（通过storage同步）
        chrome.storage.local.set({ 
            'openclaw_result': request.result,
            'openclaw_result_time': Date.now()
        });
        sendResponse({ success: true });
        return true;
    }
});

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
            case 'getStockData':
                return await getStockData();
            case 'getPageInfo':
                return await getPageInfo();
            case 'evaluate':
                return await evaluate(params.code);
            default:
                return { success: false, error: '未知命令: ' + type };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function navigate(url) {
    if (url === 'current') {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        await chrome.tabs.reload(tab.id);
        return { success: true, action: 'reloaded' };
    }
    const [tab] = await chrome.tabs.create({ url, active: true });
    return { success: true, tabId: tab.id, url };
}

async function click(selector) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector) => {
            const el = document.querySelector(selector);
            if (!el) return { success: false, error: '元素未找到: ' + selector };
            el.click();
            return { success: true };
        },
        args: [selector]
    });
    return results[0]?.result || { success: false };
}

async function type(selector, text) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector, text) => {
            const el = document.querySelector(selector);
            if (!el) return { success: false, error: '元素未找到' };
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            return { success: true };
        },
        args: [selector, text]
    });
    return results[0]?.result || { success: false };
}

async function scroll(direction, amount) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (direction, amount) => {
            const directions = { up: [0, -amount], down: [0, amount], top: [0, 0], bottom: [0, -999999] };
            const [x, y] = directions[direction] || directions.down;
            window.scrollTo(x, y);
            return { success: true };
        },
        args: [direction, amount || 500]
    });
    return results[0]?.result || { success: false };
}

async function getStockData() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            const data = { timestamp: new Date().toISOString(), url: location.href };
            const priceSel = '.stock-price .price, #quotation-entry .price, .current-price';
            const changeSel = '.stock-change .change, #quotation-entry .change';
            const priceEl = document.querySelector(priceSel);
            const changeEl = document.querySelector(changeSel);
            data.price = priceEl?.innerText?.trim() || '未找到';
            data.change = changeEl?.innerText?.trim() || '未找到';
            return data;
        }
    });
    return results[0]?.result || { success: false };
}

async function getPageInfo() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return { success: true, title: tab.title, url: tab.url };
}

async function evaluate(code) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (code) => {
            try {
                return { success: true, result: String(eval(code)) };
            } catch (e) {
                return { success: false, error: e.message };
            }
        },
        args: [code]
    });
    return results[0]?.result || { success: false };
}
