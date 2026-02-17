# 微信公众号发布器

发布文章到微信公众平台 (mp.weixin.qq.com)

## 功能

- 发布图文消息到公众号
- 上传图片素材
- 管理草稿箱
- 自动生成摘要

## 配置

需要以下环境变量：

- `WECHAT_APPID` - 微信公众平台 AppID
- `WECHAT_APPSECRET` - 微信公众平台 AppSecret
- `WECHAT_TEMPLATE_ID` - 模板消息 ID（可选）

## 使用方法

### 1. 配置账号信息

```bash
export WECHAT_APPID="your_appid"
export WECHAT_APPSECRET="your_appsecret"
```

### 2. 发布文章

```python
from wechat_mp_publisher import Publisher

publisher = Publisher()

# 发布文章
result = publisher.publish(
    title="文章标题",
    content="文章正文内容",
    thumb_path="/path/to/cover.jpg",  # 封面图片路径
    digest="摘要内容",  # 可选
    source_url="原文链接"  # 可选
)

if result['success']:
    print(f"发布成功! Media ID: {result['media_id']}")
```

### 3. 上传图片

```python
# 上传图片素材
result = publisher.upload_image(
    image_path="/path/to/image.jpg",
    name="图片名称",
    digest="图片描述"
)
```

## 注意事项

1. **账号类型**
   - 订阅号：每天可发送1条消息
   - 服务号：每月可发送4条消息

2. **内容规范**
   - 标题：64字符以内
   - 摘要：120字符以内
   - 正文：支持 HTML 格式

3. **图片要求**
   - 封面：900x500 像素，5MB 以内
   - 正文图片：10MB 以内

4. **接口限制**
   - 每天最多上传10个图片素材
   - 每月最多发布12篇文章（订阅号）

## 常见问题

Q: 提示 "access_token 过期"
A: 重新获取 access_token，SDK 会自动刷新

Q: 发布失败怎么办
A: 检查网络连接，确认账号权限

## 依赖

- requests
- python-dateutil

