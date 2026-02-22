// ==UserScript==
// @name         OpenClaw Dashboard 翻译
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  将OpenClaw Dashboard翻译为中文
// @author       小雨
// @match        http://*:*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const translations = {
        // 顶部导航
        'Dashboard': '仪表盘',
        'Sessions': '会话',
        'Skills': '技能',
        'Plugins': '插件',
        'Settings': '设置',
        'Help': '帮助',

        // 仪表盘
        'Overview': '概览',
        'Status': '状态',
        'Running': '运行中',
        'Stopped': '已停止',
        'Uptime': '运行时间',
        'Memory': '内存',
        'CPU': 'CPU',
        'Sessions': '会话',
        'Active': '活跃',
        'Gateway': '网关',
        'Agent': '代理',

        // 会话
        'New Session': '新建会话',
        'Chat': '聊天',
        'History': '历史',
        'Delete': '删除',
        'Rename': '重命名',
        'Clone': '克隆',

        // 技能
        'Install': '安装',
        'Update': '更新',
        'Remove': '移除',
        'Enabled': '已启用',
        'Disabled': '已禁用',

        // 设置
        'General': '通用',
        'Security': '安全',
        'Network': '网络',
        'Save': '保存',
        'Cancel': '取消',
        'Reset': '重置',
        'Apply': '应用',

        // 状态
        'Online': '在线',
        'Offline': '离线',
        'Connected': '已连接',
        'Disconnected': '已断开',
        'Error': '错误',
        'Warning': '警告',
        'Success': '成功',
        'Loading': '加载中...',

        // 按钮
        'Start': '启动',
        'Stop': '停止',
        'Restart': '重启',
        'Refresh': '刷新',
        'Close': '关闭',
        'Back': '返回',
        'Next': '下一步',
        'Previous': '上一步',
        'Submit': '提交',
        'Confirm': '确认',

        // 常见词汇
        'Name': '名称',
        'Type': '类型',
        'Date': '日期',
        'Time': '时间',
        'Size': '大小',
        'Status': '状态',
        'Actions': '操作',
        'Search': '搜索',
        'Filter': '筛选',
        'Sort': '排序',
        'Order': '顺序',
        'Ascending': '升序',
        'Descending': '降序',
        'Clear': '清除',
        'Copy': '复制',
        'Paste': '粘贴',
        'Cut': '剪切',
        'Undo': '撤销',
        'Redo': '重做',

        // 配置相关
        'Port': '端口',
        'Host': '主机',
        'URL': '网址',
        'Token': '令牌',
        'Password': '密码',
        'Username': '用户名',
        'Enable': '启用',
        'Disable': '禁用',
        'Required': '必填',
        'Optional': '选填',

        // 错误消息
        'Error': '错误',
        'Failed': '失败',
        'Success': '成功',
        'Timeout': '超时',
        'Not Found': '未找到',
        'Unauthorized': '未授权',
        'Forbidden': '禁止访问',
        'Internal Error': '内部错误',
        'Network Error': '网络错误',
        'Connection Refused': '连接被拒绝',

        // 其他
        'Open': '打开',
        'Create': '创建',
        'Edit': '编辑',
        'View': '查看',
        'Download': '下载',
        'Upload': '上传',
        'Export': '导出',
        'Import': '导入',
        'Expand': '展开',
        'Collapse': '折叠',
        'More': '更多',
        'Less': '更少',
        'All': '全部',
        'None': '无',
        'Yes': '是',
        'No': '否',
        'OK': '确定',
        'Ready': '就绪',
    };

    // 翻译函数
    function translatePage() {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let node;
        while (node = walker.nextNode()) {
            const text = node.textContent.trim();
            if (text && translations[text]) {
                node.textContent = translations[text];
            }
        }
    }

    // 监听DOM变化
    const observer = new MutationObserver((mutations) => {
        translatePage();
    });

    // 启动翻译
    setTimeout(translatePage, 1000);
    observer.observe(document.body, { childList: true, subtree: true });

    console.log('🌸 OpenClaw 翻译已加载');
})();
