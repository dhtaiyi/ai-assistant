// 小红书助手 - 弹出窗口脚本

document.addEventListener('DOMContentLoaded', function() {
    // 初始化
    initTabs();
    initButtons();
    loadStats();
    
    // 加载保存的数据
    loadSavedData();
});

// Tab 切换
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const panels = {
        'create': document.getElementById('create-panel'),
        'stats': document.getElementById('stats-panel'),
        'tools': document.getElementById('tools-panel')
    };
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // 切换 tab 样式
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // 切换面板
            Object.values(panels).forEach(p => p.classList.add('hidden'));
            panels[this.dataset.tab].classList.remove('hidden');
        });
    });
}

// 按钮事件
function initButtons() {
    // AI 创作
    document.getElementById('generate-btn').addEventListener('click', generateContent);
    
    // 发布
    document.getElementById('publish-btn').addEventListener('click', publishPost);
    
    // 快捷功能
    document.querySelectorAll('.quick-btn[data-action]').forEach(btn => {
        btn.addEventListener('click', function() {
            generateQuickContent(this.dataset.action);
        });
    });
    
    // 定时发布
    document.getElementById('schedule-btn').addEventListener('click', schedulePost);
    
    // 工具
    document.getElementById('clean-btn').addEventListener('click', cleanCache);
    document.getElementById('settings-btn').addEventListener('click', openSettings);
    document.getElementById('help-btn').addEventListener('click', openHelp);
}

// AI 生成内容
async function generateContent() {
    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content');
    
    if (!title) {
        alert('请先输入标题！');
        return;
    }
    
    // 显示加载状态
    content.value = '🤖 AI 正在创作中...';
    
    try {
        // 调用 OpenClaw API
        const response = await fetch('http://localhost:8080/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'xiaohongshu',
                title: title
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            content.value = data.content;
            saveData();
        } else {
            content.value = '❌ 生成失败，请重试';
        }
    } catch (error) {
        // 如果 OpenClaw 不可用，使用本地模板
        content.value = generateLocalContent(title);
    }
}

// 本地内容生成（备用）
function generateLocalContent(title) {
    const templates = {
        '效率': `\n💡 为什么推荐【主题】？\n\n【核心功能】\n✅ 功能1\n✅ 功能2\n✅ 功能3\n\n【使用体验】\n真实体验分享...\n\n👭 姐妹们有什么想问的？\n评论区告诉我！\n\n#效率工具 #职场技巧`,
        '护肤': `\n💡 为什么推荐【主题】？\n\n【使用感受】\n真实体验分享...\n\n【使用方法】\n1. 第一步\n2. 第二步\n3. 第三步\n\n⚠️ 注意事项\n\n👭 姐妹们还有什么问题？\n评论区告诉我！\n\n#护肤心得 #护肤打卡`,
        '美食': `\n📍 真实体验分享\n\n【店铺名称】\n\n💰 人均消费\n\n🍜 招牌推荐\n\n【环境氛围】\n\n📝 真实评价\n\n👭 姐妹们还有什么想吃的？\n评论区告诉我！\n\n#美食探店 #本地美食`,
        '旅游': `\n✈️ 【目的地】旅游攻略\n\n【行程安排】\nDay 1:\nDay 2:\nDay 3:\n\n【必去景点】\n\n【美食推荐】\n\n【避坑指南】\n\n💰 花费预算\n\n👭 姐妹们有什么想问的？\n评论区告诉我！\n\n#旅游攻略 #出行必备`
    };
    
    return `📍 ${title}\n\n` + templates['效率'];
}

// 快捷内容生成
function generateQuickContent(action) {
    const actions = {
        'efficiency': '效率工具推荐',
        'beauty': '护肤心得分享',
        'food': '美食探店打卡',
        'travel': '旅游攻略分享'
    };
    
    document.getElementById('post-title').value = actions[action];
    generateContent();
}

// 发布笔记
async function publishPost() {
    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content').value;
    
    if (!title || !content) {
        alert('请填写标题和内容！');
        return;
    }
    
    try {
        // 调用 MCP API 发布
        const response = await fetch('http://localhost:18060/api/v1/publish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ 发布成功！');
            saveData();
        } else {
            alert('❌ 发布失败：' + data.message);
        }
    } catch (error) {
        // 如果 MCP 不可用，保存到本地
        saveData();
        alert('✅ 已保存到草稿，请在APP中发布');
    }
}

// 定时发布
function schedulePost() {
    const time = document.getElementById('schedule-time').value;
    
    if (!time) {
        alert('请选择发布时间！');
        return;
    }
    
    // 保存定时任务
    const task = {
        title: document.getElementById('post-title').value,
        content: document.getElementById('post-content').value,
        time: time
    };
    
    chrome.storage.local.set({ scheduleTask: task }, function() {
        alert('⏰ 已设置定时发布！');
    });
}

// 统计数据
async function loadStats() {
    // 从本地存储加载
    chrome.storage.local.get(['stats'], function(result) {
        const stats = result.stats || {
            views: Math.floor(Math.random() * 1000),
            likes: Math.floor(Math.random() * 100),
            comments: Math.floor(Math.random() * 20)
        };
        
        document.getElementById('stat-views').textContent = stats.views;
        document.getElementById('stat-likes').textContent = stats.likes;
        document.getElementById('stat-comments').textContent = stats.comments;
    });
}

// 工具函数
function cleanCache() {
    chrome.storage.local.clear(function() {
        alert('🧹 缓存已清除！');
    });
}

function openSettings() {
    alert('⚙️ 设置功能开发中...');
}

function openHelp() {
    alert('📖 使用帮助：\n\n1. 输入标题和内容\n2. 点击"AI帮我写"生成内容\n3. 点击"发布到小红书"\n\n有问题请联系客服！');
}

// 数据保存
function saveData() {
    const data = {
        title: document.getElementById('post-title').value,
        content: document.getElementById('post-content').value,
        lastUpdate: new Date().toISOString()
    };
    
    chrome.storage.local.set({ draft: data });
}

function loadSavedData() {
    chrome.storage.local.get(['draft'], function(result) {
        if (result.draft) {
            document.getElementById('post-title').value = result.draft.title || '';
            document.getElementById('post-content').value = result.draft.content || '';
        }
    });
}
