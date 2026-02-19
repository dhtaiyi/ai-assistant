// OpenClaw 浏览器控制 - Popup脚本

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initButtons();
    updateStatus();
    updatePageInfo();
});

// Tab切换
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(this.dataset.tab + '-panel').classList.add('active');
        });
    });
}

// 初始化按钮
function initButtons() {
    // 导航
    document.getElementById('navigate-btn').addEventListener('click', () => {
        const url = document.getElementById('url-input').value;
        if (url) execute({ type: 'navigate', url });
    });
    
    // 刷新
    document.getElementById('refresh-btn')?.addEventListener('click', () => {
        execute({ type: 'navigate', url: 'current' });
    });
    
    // 页面信息
    document.getElementById('page-info-btn').addEventListener('click', () => {
        execute({ type: 'getPageInfo' });
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
    
    // 股票数据
    document.getElementById('stock-btn').addEventListener('click', () => {
        execute({ type: 'getStockData' });
    });
    
    // 所有文本
    document.getElementById('all-text-btn').addEventListener('click', () => {
        execute({ type: 'getAllText' });
    });
    
    // 查找元素
    document.getElementById('find-btn').addEventListener('click', () => {
        const selector = document.getElementById('find-selector').value;
        if (selector) execute({ type: 'findElements', selector });
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
            const result = response.result || response;
            showResult(formatResult(result), 'success');
            
            // 更新页面信息
            if (command.type === 'navigate' || command.type === 'getPageInfo') {
                updatePageInfo();
            }
        } else {
            showResult('失败: ' + (response.error || '未知错误'), 'error');
        }
    } catch (error) {
        showResult('错误: ' + error.message, 'error');
    }
}

// 格式化结果
function formatResult(result) {
    if (result === null || result === undefined) {
        return '✅ 执行成功 (无返回值)';
    }
    
    if (typeof result === 'object') {
        // 股票数据特殊处理
        if (result.prices && result.prices.length > 0) {
            let text = '📊 股票数据:\n\n';
            result.prices.slice(0, 5).forEach((p, i) => {
                text += `${i + 1}. ${p.value || p.text || p}\n`;
            });
            if (result.change) text += `\n涨跌: ${result.change}`;
            text += `\n\n时间: ${result.timestamp?.split('T')[1]?.split('.')[0] || ''}`;
            return text;
        }
        
        // 其他对象
        return JSON.stringify(result, null, 2);
    }
    
    return String(result);
}

// 显示结果
function showResult(text, type = 'info') {
    const el = document.getElementById('result');
    const time = new Date().toLocaleTimeString();
    
    let className = 'result';
    if (type === 'error') className += ' error';
    if (type === 'success') className += ' success';
    
    el.className = className;
    el.textContent = `[${time}]\n${text}`;
}

// 更新状态
async function updateStatus() {
    try {
        const response = await chrome.runtime.sendMessage({ action: 'getStatus' });
        const statusEl = document.getElementById('status');
        
        if (response?.success) {
            statusEl.className = 'status';
            statusEl.textContent = '🟢 已就绪';
        } else {
            statusEl.className = 'status';
            statusEl.textContent = '🔴 异常';
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
        
        if (response?.success) {
            const info = response.result || {};
            document.getElementById('page-info').innerHTML = `
                <span><strong>标题:</strong> ${(info.title || '未知').substring(0, 30)}</span>
                <span><strong>URL:</strong> ${(info.url || '未知').substring(0, 40)}</span>
            `;
            document.getElementById('url-input').value = info.url || '';
        }
    } catch (error) {
        console.error('获取页面信息失败:', error);
    }
}

// 全局函数
function go(url) {
    document.getElementById('url-input').value = url;
    execute({ type: 'navigate', url });
}

function refresh() {
    execute({ type: 'navigate', url: 'current' });
}

function scroll(direction) {
    execute({ type: 'scroll', direction, amount: 500 });
}
