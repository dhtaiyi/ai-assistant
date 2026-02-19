// OpenClaw 远程浏览器控制 - 后台服务
// 处理来自OpenClaw的命令

const API_PORT = 9999;
let server = null;
let isRunning = false;

// 命令队列
const commandQueue = [];
let currentTab = null;

// 初始化
chrome.runtime.onInstalled.addListener(() => {
    console.log('OpenClaw 远程控制已安装');
    startServer();
});

// 启动HTTP服务器
function startServer() {
    if (isRunning) return;
    
    // 通知用户服务器已启动
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'OpenClaw 远程控制',
        message: '服务器已启动，监听端口: ' + API_PORT
    });
    
    isRunning = true;
    console.log('OpenClaw服务器已启动，端口:', API_PORT);
}

// 监听来自扩展的请求
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'execute') {
        executeCommand(request.command)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // 异步响应
    }
    
    if (request.action === 'getStatus') {
        sendResponse({
            success: true,
            tab: currentTab?.id,
            url: currentTab?.url,
            isRunning: isRunning
        });
        return true;
    }
    
    if (request.action === 'startServer') {
        startServer();
        sendResponse({ success: true });
        return true;
    }
});

// 执行命令
async function executeCommand(command) {
    const { type, ...params } = command;
    
    try {
        switch (type) {
            case 'navigate':
                return await navigate(params.url);
            case 'click':
                return await click(params.selector, params.index);
            case 'type':
                return await type(params.selector, params.text);
            case 'scroll':
                return await scroll(params.direction, params.amount);
            case 'wait':
                return await wait(params.duration);
            case 'screenshot':
                return await screenshot();
            case 'evaluate':
                return await evaluate(params.script);
            case 'getPageInfo':
                return await getPageInfo();
            case 'findElement':
                return await findElement(params.selector);
            case 'executeScript':
                return await executeScript(params.code);
            default:
                return { success: false, error: '未知命令: ' + type };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// 导航到URL
async function navigate({ url }) {
    const [tab] = await chrome.tabs.create({ url });
    currentTab = tab;
    return { success: true, tabId: tab.id, url };
}

// 点击元素
async function click(selector, index = 0) {
    const tab = await getActiveTab();
    if (!tab) throw new Error('没有活动标签页');
    
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector, index) => {
            const elements = document.querySelectorAll(selector);
            if (elements.length === 0) {
                throw new Error('未找到元素: ' + selector);
            }
            const el = elements[index] || elements[0];
            el.click();
            return { success: true, clicked: selector };
        },
        args: [selector, index]
    });
    
    return results[0]?.result || { success: false, error: '执行失败' };
}

// 输入文本
async function type(selector, text) {
    const tab = await getActiveTab();
    if (!tab) throw new Error('没有活动标签页');
    
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector, text) => {
            const el = document.querySelector(selector);
            if (!el) throw new Error('未找到元素: ' + selector);
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return { success: true, typed: selector };
        },
        args: [selector, text]
    });
    
    return results[0]?.result || { success: false, error: '执行失败' };
}

// 滚动页面
async function scroll(direction = 'down', amount = 500) {
    const tab = await getActiveTab();
    if (!tab) throw new Error('没有活动标签页');
    
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (direction, amount) => {
            if (direction === 'down') {
                window.scrollBy(0, amount);
            } else if (direction === 'up') {
                window.scrollBy(0, -amount);
            } else if (direction === 'top') {
                window.scrollTo(0, 0);
            } else if (direction === 'bottom') {
                window.scrollTo(0, document.body.scrollHeight);
            }
            return { success: true, direction, amount };
        },
        args: [direction, amount]
    });
    
    return results[0]?.result || { success: false, error: '执行失败' };
}

// 等待
async function wait(duration = 1000) {
    await new Promise(resolve => setTimeout(resolve, duration));
    return { success: true, waited: duration };
}

// 截图
async function screenshot() {
    const tab = await getActiveTab();
    if (!tab) throw new Error('没有活动标签页');
    
    // 使用 tabs.captureVisibleTab
    const dataUrl = await chrome.tabs.captureVisibleTab();
    return { success: true, screenshot: dataUrl };
}

// 执行JavaScript
async function evaluate(script) {
    const tab = await getActiveTab();
    if (!tab) throw new Error('没有活动标签页');
    
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (script) => {
            try {
                const result = eval(script);
                return { success: true, result: String(result) };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },
        args: [script]
    });
    
    return results[0]?.result || { success: false, error: '执行失败' };
}

// 执行脚本代码
async function executeScript(code) {
    const tab = await getActiveTab();
    if (!tab) throw new Error('没有活动标签页');
    
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        code: code
    });
    
    return { success: true, results: results[0]?.result };
}

// 获取页面信息
async function getPageInfo() {
    const tab = await getActiveTab();
    if (!tab) throw new Error('没有活动标签页');
    
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            return {
                title: document.title,
                url: window.location.href,
                body: document.body.innerHTML.substring(0, 10000),
                readyState: document.readyState
            };
        }
    });
    
    return results[0]?.result || { success: false, error: '获取失败' };
}

// 查找元素
async function findElement(selector) {
    const tab = await getActiveTab();
    if (!tab) throw new Error('没有活动标签页');
    
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (selector) => {
            const elements = document.querySelectorAll(selector);
            const found = [];
            elements.forEach((el, i) => {
                if (i < 10) { // 最多返回10个
                    found.push({
                        index: i,
                        tagName: el.tagName,
                        text: el.innerText?.substring(0, 100) || '',
                        visible: el.offsetParent !== null
                    });
                }
            });
            return found;
        },
        args: [selector]
    });
    
    return results[0]?.result || { success: false, error: '查找失败' };
}

// 获取活动标签页
async function getActiveTab() {
    if (currentTab && currentTab.id) {
        try {
            const tab = await chrome.tabs.get(currentTab.id);
            return tab;
        } catch (e) {
            // 标签页可能已关闭
        }
    }
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
        currentTab = tab;
    }
    return tab;
}
