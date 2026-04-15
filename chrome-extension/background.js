// 小红书助手 - 后台服务

// 定时任务检查
chrome.runtime.onInstalled.addListener(function() {
    console.log('小红书助手已安装');
    
    // 初始化存储
    chrome.storage.local.set({
        stats: {
            views: 0,
            likes: 0,
            comments: 0
        }
    });
});

// 定时任务
chrome.alarms.create('checkSchedule', { periodInMinutes: 1 });

chrome.alarms.onAlarm.addListener(function(alarm) {
    if (alarm.name === 'checkSchedule') {
        checkScheduledPosts();
    }
});

// 检查定时发布任务
async function checkScheduledPosts() {
    chrome.storage.local.get(['scheduleTask'], async function(result) {
        const task = result.scheduleTask;
        
        if (!task) return;
        
        const now = new Date();
        const scheduledTime = new Date(task.time);
        
        if (now >= scheduledTime) {
            // 执行发布
            await publishPost(task.title, task.content);
            
            // 清除任务
            chrome.storage.local.remove('scheduleTask');
        }
    });
}

// 发布笔记
async function publishPost(title, content) {
    try {
        const response = await fetch('http://localhost:18060/api/v1/publish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ 定时发布成功');
            
            // 更新统计
            chrome.storage.local.get(['stats'], function(result) {
                const stats = result.stats || { views: 0, likes: 0, comments: 0 };
                stats.likes++;
                chrome.storage.local.set({ stats });
            });
        }
    } catch (error) {
        console.log('❌ 定时发布失败:', error);
    }
}

// 消息监听
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'generate') {
        generateContent(request.title).then(content => {
            sendResponse({ success: true, content });
        });
        return true; // 异步响应
    }
    
    if (request.action === 'publish') {
        publishPost(request.title, request.content).then(() => {
            sendResponse({ success: true });
        });
        return true;
    }
});

// AI 内容生成
async function generateContent(title) {
    try {
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
        return data.content || generateLocalContent(title);
    } catch (error) {
        return generateLocalContent(title);
    }
}

// 本地内容生成
function generateLocalContent(title) {
    return `📍 ${title}\n\n💡 分享理由\n\n【核心内容】\n\n【使用体验】\n\n👭 姐妹们有什么想问的？\n评论区告诉我！\n\n#小红书 #${title}`;
}
