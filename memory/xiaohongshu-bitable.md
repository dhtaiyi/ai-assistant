# 小红书自动化工作流 - 飞书多维表格

## 表格信息

- **表格名称**: 小红书自动化工作流
- **App Token**: INUtbOmLlahQyHsBRkkcuhjinHb
- **Table ID**: tblIIo7593yJJkAT
- **链接**: https://xcnniyql57u3.feishu.cn/base/INUtbOmLlahQyHsBRkkcuhjinHb

## 字段结构

| 字段名 | 字段ID | 类型 |
|--------|--------|------|
| 小红书自动化工作流 | fldALFp7Iz | 文本 (主键) |
| 选题来源 | fldzDt2hoZ | 文本 |
| 选题标题 | flddKf3Rt0 | 文本 |
| 话题标签 | fldYpsixU4 | 文本 |
| 生成标题 | fld8g0OWil | 文本 |
| 正文内容 | fldBLoAAYi | 文本 |
| 图片链接 | fldLsSNpWu | URL |
| 发布时间 | fldAMbj0mn | 日期时间 |
| 状态 | fldvGeWCW3 | 文本 |

## 当前状态

- 记录数: 11 条（目前均为空）

## 操作示例

### 读取记录
```python
feishu_bitable_list_records(
    app_token="INUtbOmLlahQyHsBRkkcuhjinHb",
    table_id="tblIIo7593yJJkAT"
)
```

### 创建记录
```python
feishu_bitable_create_record(
    app_token="INUtbOmLlahQyHsBRkkcuhjinHb",
    table_id="tblIIo7593yJJkAT",
    fields={
        "选题来源": "来源",
        "选题标题": "标题",
        "话题标签": "#标签",
        "生成标题": "生成的标题",
        "正文内容": "正文内容...",
        "图片链接": {"text": "图片", "link": "https://..."},
        "状态": "待发布"
    }
)
```
