// OpenClaw 远程控制 - 弹出窗口脚本

let isConnected = false;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initButtons();
    addLog('系统已启动', 'info');
    checkStatus();
});

// Tab切换
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.panel');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(this.dataset.tab + '-panel').classList.add('active');
        });
    });
}

// 按钮事件
function initButtons() {
    // 快速命令
    document.querySelectorAll('.command-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const cmd = JSON.parse(this.dataset.cmd);
            executeCommand(cmd);
        });
    });
    
    // 刷新
    document.getElementById('refresh-btn').addEventListener('click', () => {
        executeCommand({ type: 'navigate', url: 'current' });
    });
    
    // 后退/前进
    document.getElementById('back-btn').addEventListener('click', () => {
        chrome.tabs.goBack();
    });
    
    document.getElementById('forward-btn').addEventListener('click', () => {
        chrome.tabs.goForward();
    });
    
    // 导航
    document.getElementById('navigate-btn').addEventListener('click', () => {
        const url = document.getElementById('url-input').value;
        if (url) {
            executeCommand({ type: 'navigate', url });
        }
    });
    
    // 点击
    document.getElementById('click-btn').addEventListener('click', () => {
        const selector = document.getElementById('click-selector').value;
        if (selector) {
            executeCommand({ type: 'click', selector });
        }
    });
    
    // 输入
    document.getElementById('type-btn').addEventListener('click', () => {
        const selector = document.getElementById('type-selector').value;
        const text = document.getElementById('type-text').value;
        if (selector && text) {
            executeCommand({ type: 'type', selector, text });
        }
    });
    
    // 查找
    document.getElementById('find-btn').addEventListener('click', () => {
        const selector = document.getElementById('find-selector').value;
        if (selector) {
            executeCommand({ type: 'findElement', selector });
        }
    });
    
    // 执行代码
    document.getElementById('execute-btn').addEventListener('click', () => {
        const code = document.getElementById('code-input').value;
        if (code) {
            executeCommand({ type: 'evaluate', script: code });
        }
    });
    
    // 清除日志
    document.getElementById('clear-log').addEventListener('click', () => {
        document.getElementById('log-container').innerHTML = '';
    });
}

// 执行命令
async function executeCommand(command) {
    addLog('执行命令: ' + command.type, 'info');
    
    try {
        const response = await chrome.runtime.sendMessage({
            action: 'execute',
            command: command
        });
        
        if (response.success) {
            addLog('✓ 成功: ' + JSON.stringify(response.result), 'success');
            updatePageInfo();
        } else {
            addLog('✗ 失败: ' + response.error, 'error');
        }
    } catch (error) {
        addLog('✗ 错误: ' + error.message, 'error');
    }
}

// 检查状态
async function checkStatus() {
    try {
        const response = await chrome.runtime.sendMessage({ action: 'getStatus' });
        updateStatus(response);
    } catch (error) {
        updateStatus({ isRunning: false });
    }
}

// 更新状态
function updateStatus(status) {
    const statusEl = document.getElementById('status');
    if (status.isRunning) {
        statusEl.className = 'status connected';
        statusEl.textContent = '🟢 已连接 - 端口9999';
        isConnected = true;
    } else {
        statusEl.className = 'status disconnected';
        statusEl.textContent = '🔴 未连接 - 点击连接';
        isConnected = false;
    }
}

// 添加日志
function addLog(message, type = 'info') {
    const container = document.getElementById('log-container');
    const entry = document.createElement('div');
    entry.className = 'log-entry ' + type;
    
    const time = new Date().toLocaleTimeString();
    entry.textContent = `[${time}] ${message}`;
    
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
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
                <strong>标题:</strong> ${info.title}<br>
                <strong>URL:</strong> ${info.url}<br>
                <strong>状态:</strong> ${info.readyState}
            `;
            document.getElementById('url-input').value = info.url || '';
        }
    } catch (error) {
        console.error('获取页面信息失败:', error);
    }
}
