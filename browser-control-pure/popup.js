// OpenClaw Browser Control - Popup脚本

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initButtons();
    updateStatus();
    updatePageInfo();
});

// Tab切换
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        this.classList.add('active');
        document.getElementById(this.dataset.tab + '-panel').classList.add('active');
    });
});

// 按钮事件
function initButtons() {
    // 导航
    document.getElementById('navigate-btn').addEventListener('click', () => {
        const url = document.getElementById('url-input').value;
        if (url) execute({ type: 'navigate', url });
    });
    
    // 快捷链接
    document.querySelectorAll('.quick-link').forEach(link => {
        link.addEventListener('click', function() {
            const url = this.dataset.url;
            document.getElementById('url-input').value = url;
            execute({ type: 'navigate', url });
        });
    });
    
    // 刷新
    document.getElementById('refresh-btn').addEventListener('click', () => {
        execute({ type: 'navigate', url: 'current' });
    });
    
    // 点击
    document.getElementById('click-btn').addEventListener('click', () => {
        const selector = document.getElementById('click-selector').value;
        if (selector) execute({ type: 'click', selector });
    });
    
    // 输入
    document.getElementById('type-btn').addEventListener('click', () => {
        const selector = document.getElementById('type-selector').value;
        const text = document.getElementById('type-text').value;
        if (selector && text) execute({ type: 'type', selector, text });
    });
    
    // 滚动
    document.querySelectorAll('[data-scroll]').forEach(btn => {
        btn.addEventListener('click', function() {
            execute({ type: 'scroll', direction: this.dataset.scroll, amount: 500 });
        });
    });
    
    // 股票数据
    document.getElementById('stock-btn').addEventListener('click', () => {
        execute({ type: 'getStockData' });
    });
    
    // 提取价格
    document.getElementById('extract-btn').addEventListener('click', () => {
        const selector = prompt('输入CSS选择器（如 .price, #quotation-entry）', '.price');
        if (selector) execute({ type: 'extractData', selector });
    });
    
    // 执行代码
    document.getElementById('eval-btn').addEventListener('click', () => {
        const code = document.getElementById('eval-code').value;
        if (code) execute({ type: 'evaluate', code });
    });
}

// 执行命令
async function execute(command) {
    showResult('执行中...', 'info');
    
    try {
        const response = await chrome.runtime.sendMessage({
            action: 'execute',
            command: command
        });
        
        if (response.success) {
            showResult(formatResult(response), 'success');
            updatePageInfo();
        } else {
            showResult('失败: ' + response.error, 'error');
        }
    } catch (error) {
        showResult('错误: ' + error.message, 'error');
    }
}

// 格式化结果
function formatResult(response) {
    const result = response.result || response;
    
    if (result === null || result === undefined) {
        return '✅ 执行成功 (无返回值)';
    }
    
    if (typeof result === 'object') {
        return JSON.stringify(result, null, 2);
    }
    
    return String(result);
}

// 显示结果
function showResult(text, type = 'info') {
    const el = document.getElementById('result');
    const time = new Date().toLocaleTimeString();
    el.textContent = `[${time}] ${text}`;
    el.className = 'result ' + type;
}

// 更新状态
async function updateStatus() {
    try {
        const response = await chrome.runtime.sendMessage({ action: 'getStatus' });
        const statusEl = document.getElementById('status');
        if (response.success) {
            statusEl.className = 'status connected';
            statusEl.textContent = '🟢 已连接';
        } else {
            statusEl.className = 'status';
            statusEl.textContent = '🔴 未连接';
        }
    } catch (error) {
        document.getElementById('status').textContent = '🔴 错误';
    }
}

// 更新页面信息
async function updatePageInfo() {
    try {
        const response = await chrome.runtime.sendMessage({
            action: 'execute',
            command: { type: 'getPageInfo' }
        });
        
        if (response.success) {
            const info = response.result;
            document.getElementById('page-info').innerHTML = `
                <strong>标题:</strong> ${info.title?.substring(0, 30) || '未知'}<br>
                <strong>URL:</strong> ${info.url?.substring(0, 40) || '未知'}
            `;
            document.getElementById('url-input').value = info.url || '';
        }
    } catch (error) {
        console.error('获取页面信息失败:', error);
    }
}
