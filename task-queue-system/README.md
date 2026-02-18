# 任务队列管理系统

## 概述

基于 Taskr、Cron-Scheduling 和 Reminder 的任务队列管理系统。

## 组成部分

### 1. Taskr - 任务跟踪
- 网址: https://taskr.one
- 功能: 任务创建、状态更新、进度跟踪
- 特点: 实时可视化、支持Web和移动端

### 2. Cron-Scheduling - 定时调度
- 功能: 定时任务、周期性执行
- 位置: /root/.openclaw/workspace/skills/cron-scheduling/

### 3. Reminder - 提醒系统
- 功能: 自然语言提醒、Telegram通知
- 特点: 24h/1h/10m提前提醒

---

## 任务类型

### A. 即时任务
- 立即执行
- 通过 Taskr 跟踪
- 完成后通知

### B. 定时任务
- 固定时间执行
- 使用 Cron 调度
- 失败重试机制

### C. 周期性任务
- 每天/每周/每月执行
- 自动记录日志
- 异常告警

---

## 任务队列设计

### 1. 待办队列 (Todo Queue)
- 存储位置: /root/.openclaw/workspace/task-queue-system/todo/
- 文件格式: JSON
- 包含: 任务ID、创建时间、优先级、状态

### 2. 执行队列 (Execution Queue)
- 存储位置: /root/.openclaw/workspace/task-queue-system/executing/
- 状态: 运行中
- 记录: 开始时间、执行进程

### 3. 完成队列 (Done Queue)
- 存储位置: /root/.openclaw/workspace/task-queue-system/done/
- 记录: 完成时间、输出结果
- 保留期限: 30天

### 4. 失败队列 (Failed Queue)
- 存储位置: /root/.openclaw/workspace/task-queue-system/failed/
- 记录: 失败原因、重试次数
- 手动处理或自动重试

---

## 使用场景

### 小红书运营任务

#### 每日任务
```
时间: 每天 9:00
任务:
1. 检查昨晚数据
2. 回复评论
3. 今日内容规划
```

#### 每周任务
```
时间: 每周一 10:00
任务:
1. 上周数据总结
2. 本周发布计划
3. 素材收集
```

#### 每月任务
```
时间: 每月1日 9:00
任务:
1. 上月数据报告
2. 本月目标设定
3. 策略调整

---

## 任务优先级

### P0 - 紧急 (立即执行)
- 系统告警
- 关键任务失败
- 紧急发布

### P1 - 高 (24小时内)
- 高优先级内容
- 重要数据监控
- 计划内任务

### P2 - 中 (本周内)
- 常规内容创作
- 数据分析
- 优化任务

### P3 - 低 (本月内)
- 学习新技能
- 系统维护
- 文档更新

---

## 监控和告警

### 任务状态监控
- 成功/失败/超时
- 执行时间统计
- 队列堆积检测

### 告警规则
- 任务失败: 即时通知
- 执行超时: 24h阈值
- 队列堆积: >100个待执行

### 通知渠道
- Telegram (主要)
- 企业微信 (备选)
- 邮件 (汇总)

---

## 使用方法

### 1. 添加任务
```bash
# 添加即时任务
echo '{"id": "001", "type": "content", "priority": 2, "content": "创建小红书笔记"}' \
  >> /root/.openclaw/workspace/task-queue-system/todo/queue.json
```

### 2. 查看任务
```bash
# 查看待办队列
cat /root/.openclaw/workspace/task-queue-system/todo/queue.json
```

### 3. 任务执行
```bash
# 手动执行队列任务
bash /root/.openclaw/workspace/task-queue-system/run-queue.sh
```

---

## 集成 Taskr

### 配置 Taskr
1. 获取 API Key: https://taskr.one
2. 配置环境变量
3. 创建项目

### 使用 Taskr
```bash
# 创建任务
tools/create_task --title "创建小红书笔记" --priority high

# 更新状态
tools/update_task --id <task-id> --status done

# 查看进度
tools/get_tasks --project "小红书运营"
```

---

## 最佳实践

1. **任务分解**
   - 大任务拆分为小任务
   - 每个任务有明确产出

2. **进度更新**
   - 定期更新任务状态
   - 记录关键进展

3. **异常处理**
   - 记录失败原因
   - 设置重试机制

4. **定期回顾**
   - 每周回顾任务完成情况
   - 优化任务流程

---

## 相关文件

- /root/.openclaw/workspace/task-queue-system/
  - README.md - 本文档
  - todo/ - 待办队列
  - executing/ - 执行队列
  - done/ - 完成队列
  - failed/ - 失败队列
  - scripts/
    - add-task.sh - 添加任务
    - run-queue.sh - 执行队列
    - check-status.sh - 检查状态
    - cleanup.sh - 清理旧任务

