// OpenClaw Remote Control - 完整远程控制版
// 连接Python服务器，接收并执行命令

let serverUrl = null;
let socket = null;
let reconnectInterval = null;
let commandQueue = [];

// 从storage加载配置
async function loadConfig() {
    const config = await chrome.storage.local.get(['serverUrl', 'apiKey']);
    return config;
}

// 连接到服务器
async function connect() {
    const config = await loadConfig();
    if (!config.serverUrl) {
        console.log('未配置服务器地址');
        return;
    }
    
    serverUrl = config.serverUrl;
    
    // 使用WebSocket或轮询
    if (serverUrl.includes('ws://') || serverUrl.includes('wss://')) {
        connectWebSocket();
    } else {
        startPolling();
    }
}

// WebSocket连接
function connectWebSocket() {
    try {
        socket = new WebSocket(serverUrl);
        
        socket.onopen = () => {
            console.log('✅ 已连接到服务器');
            showNotification('已连接到OpenClaw');
            sendHeartbeat();
        };
        
        socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'command') {
                const result = await executeCommand(data.command);
                sendResult(data.id, result);
            }
        };
        
        socket.onclose = () => {
            console.log('连接断开，5秒后重连...');
            setTimeout(connectWebSocket, 5000);
        };
        
        socket.onerror = (error) => {
            console.error('WebSocket错误:', error);
        };
    } catch (e) {
        console.error('连接失败:', e);
        setTimeout(connectWebSocket, 5000);
    }
}

// 轮询模式
function startPolling() {
    if (reconnectInterval) clearInterval(reconnectInterval);
    
    reconnectInterval = setInterval(async () => {
        try {
            const response = await fetch(`${serverUrl}/poll`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.command) {
                const result = await executeCommand(data.command);
                
                // 发送结果
                await fetch(`${serverUrl}/result`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: data.id,
                        result: result
                    })
                });
            }
        } catch (e) {
            console.error('轮询错误:', e);
        }
    }, 1000); // 每秒轮询
}

// 发送心跳
function sendHeartbeat() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'heartbeat' }));
    }
    setTimeout(sendHeartbeat, 30000);
}

// 发送结果
async function sendResult(id, result) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'result', id, result }));
    }
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
            case 'getStockData':
                return await getStockData();
            case 'evaluate':
                return await evaluate(params.code);
            case 'getPageInfo':
                return await getPageInfo();
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

// 命令实现
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
            return { success: true, clicked: selector };
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
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return { success: true };
        },
        args: [selector, text]
    });
    return results[0]?.result || { success: false };
}

async function scroll(direction, amount) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const directions = { up: [0, -amount], down: [0, amount], top: [0, 0], bottom: [0, -999999] };
    const [x, y] = directions[direction] || directions.down;
    
    await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (x, y) => window.scrollTo(x, y),
        args: [x, y]
    });
    return { success: true, direction, amount };
}

async function wait(duration) {
    await new Promise(r => setTimeout(r, duration));
    return { success: true, waited: duration };
}

async function getHTML() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.body.innerHTML.substring(0, 100000)
    });
    return { success: true, html: results[0]?.result || '' };
}

async function getStockData() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            const data = { timestamp: new Date().toISOString(), url: location.href };
            const priceSel = '.stock-price .price, #quotation-entry .price, .current-price';
            const changeSel = '.stock-change .change, #quotation-entry .change, .change-percent';
            const priceEl = document.querySelector(priceSel);
            const changeEl = document.querySelector(changeSel);
            data.price = priceEl?.innerText?.trim() || '未找到';
            data.change = changeEl?.innerText?.trim() || '未找到';
            return data;
        }
    });
    return results[0]?.result || { success: false };
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

async function getPageInfo() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return { success: true, title: tab.title, url: tab.url, id: tab.id };
}

async function getScreenshot() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const dataUrl = await chrome.tabs.captureVisibleTab();
    return { success: true, screenshot: dataUrl.substring(0, 100) + '...[base64]' };
}

async function getCookies() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = new URL(tab.url);
    const cookies = await chrome.cookies.getAll({ url: url.origin });
    return { success: true, cookies };
}

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'execute') {
        executeCommand(request.command)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }
    
    if (request.action === 'connect') {
        chrome.storage.local.set({ serverUrl: request.url });
        serverUrl = request.url;
        connect();
        sendResponse({ success: true });
        return true;
    }
    
    if (request.action === 'disconnect') {
        if (socket) socket.close();
        if (reconnectInterval) clearInterval(reconnectInterval);
        chrome.storage.local.remove('serverUrl');
        sendResponse({ success: true });
        return true;
    }
    
    if (request.action === 'getStatus') {
        sendResponse({ 
            success: true, 
            connected: !!serverUrl,
            serverUrl: serverUrl 
        });
        return true;
    }
});

// 启动连接
connect();
