# 🎯 小红书发贴完整指南

## ✅ 当前状态

**Cookie已保存！** 创作者Cookie已保存，可以正常访问创作者平台。

---

## 📊 验证结果

```
✅ 用户名: 困困困
✅ 创作者Cookie: 18个
✅ 访问权限: 正常
✅ 发贴页面: 可以访问
```

---

## 🚀 发贴步骤

### 方法1：使用脚本发贴（推荐）

脚本已创建：
- `/root/.openclaw/workspace/xiaohongshu-creator-post.py`
- `/root/.openclaw/workspace/xiaohongshu-upload-text.py`

运行发贴：
```bash
python3 /root/.openclaw/workspace/xiaohongshu-creator-post.py
```

### 方法2：手动发贴（最可靠）

由于服务器环境限制，建议手动发贴：

1. **打开浏览器**
   ```
   https://creator.xiaohongshu.com/publish/publish
   ```

2. **登录创作者平台**
   - 应该已自动登录（Cookie已配置）
   - 如果需要登录，用手机扫码

3. **点击"上传图文"或"写长文"**

4. **填写内容**

5. **发布**

---

## 📝 发贴内容模板

### 新人报道（已准备好）

**标题：**
```
新人报道｜终于找到我的生活好物清单🛍️
```

**内容：**
```text
哈喽～我是新人博主！🎉

✨ 关于我：
• 刚开始分享生活好物
• 喜欢发掘实用小物件
• 每天分享1-2个心水好物

🌟 为什么开始：
之前刷小红书看到好多生活好物分享，
自己也忍不住想分享一下！

📦 近期新入的好物：
- 收纳神器
- 桌面整理
- 日常小物

💕 希望能在这里交到志同道合的朋友！

#新人报道 #生活好物 #好物分享 #新人博主 #日常分享
```

---

## 🔧 常见问题

### Q1: 需要手动登录吗？

看情况：
- 如果Cookie有效，直接进入发贴页
- 如果需要登录，用创作者平台的登录方式

### Q2: Cookie在哪里？

创作者Cookie已保存到：
```
/root/.openclaw/workspace/xiaohongshu-creator-cookies.json
```

### Q3: 如何更新Cookie？

如果Cookie失效：
1. 浏览器访问创作者平台
2. F12 → Console
3. 粘贴：
```javascript
copy(document.cookie);
```
4. 保存：
```bash
python3 /root/.openclaw/workspace/xiaohongshu-tool.py save "粘贴的Cookie"
```

---

## 📂 相关文件

| 文件 | 说明 |
|------|------|
| `xiaohongshu-creator-cookies.json` | 创作者Cookie |
| `xiaohongshu-creator-post.py` | 发贴脚本 |
| `xiaohongshu-upload-text.py` | 图文发贴脚本 |

---

## 💡 发贴建议

### 内容方面
- 标题要吸引眼球
- 内容要有价值
- 配图要精美
- 话题标签要相关

### 频率方面
- 起步期：每天1篇
- 稳定后：每天2-3篇

### 时间方面
- 早7-9点
- 午12-14点
- 晚20-22点

---

## ✅ 成功标准

- [ ] 能访问创作者平台
- [ ] 找到发贴入口
- [ ] 填写内容
- [ ] 点击发布
- [ ] 发布成功

---

**下一步**：打开浏览器访问创作者平台，开始发贴吧！ 🎉
