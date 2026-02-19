// Content Script - 注入到每个页面
// 监听来自control-panel的命令

(function() {
    if (window.__OpenClawContent) return;
    window.__OpenClawContent = true;

    // 监听来自background的命令
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.target === 'content') {
            executeCommand(request.command)
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;
        }
    });

    // 监听来自同页面window的消息（control-panel发送）
    window.addEventListener('message', async (event) => {
        if (event.data?.type === 'OPENCLAW_COMMAND') {
            const result = await executeCommand(event.data.command);
            event.source.postMessage({
                type: 'OPENCLAW_RESULT',
                id: event.data.id,
                result: result
            }, '*');
        }
    });

    // 执行命令
    async function executeCommand(command) {
        const { type, ...params } = command;

        try {
            switch (type) {
                case 'getHTML':
                    return { success: true, html: document.body.innerHTML.substring(0, 50000) };
                
                case 'getText':
                    const el = document.querySelector(params.selector);
                    return { success: true, text: el?.innerText?.trim() || '' };
                
                case 'getValue':
                    const input = document.querySelector(params.selector);
                    return { success: true, value: input?.value || '' };
                
                case 'getStockData':
                    return await getStockData();
                
                case 'getAllText':
                    return await getAllText();
                
                case 'evaluate':
                    return await evaluate(params.code);
                
                default:
                    return { success: false, error: '未知命令: ' + type };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // 获取股票数据
    async function getStockData() {
        const selectors = {
            price: '.stock-price .price, #quotation-entry .price, .current-price, .stock-current .price, .hq-price .price, [class*="price"]',
            change: '.stock-change .change, #quotation-entry .change, .change-percent, .stock-current .change, [class*="change"]'
        };

        const priceEl = document.querySelectorAll(selectors.price);
        const changeEl = document.querySelectorAll(selectors.change);

        return {
            success: true,
            data: {
                timestamp: new Date().toISOString(),
                url: window.location.href,
                price: priceEl[0]?.innerText?.trim() || '未找到',
                change: changeEl[0]?.innerText?.trim() || '未找到',
                allPrices: Array.from(priceEl).slice(0, 5).map(el => el.innerText.trim()),
                title: document.title
            }
        };
    }

    // 获取所有文本
    async function getAllText() {
        const texts = [];
        document.querySelectorAll('span, div, td, p').forEach(el => {
            const text = el.innerText?.trim();
            if (text && text.length > 0 && text.length < 20 && /[\d]/.test(text)) {
                texts.push(text);
            }
        });
        return {
            success: true,
            data: [...new Set(texts)].slice(0, 50)
        };
    }

    // 执行JS
    async function evaluate(code) {
        try {
            const result = eval(code);
            return { success: true, result: String(result) };
        } catch (e) {
            return { success: false, error: e.message };
        }
    }
})();
