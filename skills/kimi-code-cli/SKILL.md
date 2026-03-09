# Kimi Code CLI 技能

本技能提供 Kimi Code CLI 的调用能力，让 Agent 可以使用 Kimi 进行代码开发。

## 命令行工具

路径：`/root/.local/bin/kimi`

## 可用命令

### 1. 交互式编程（term）
```bash
kimi term
```

### 2. ACP 服务器模式
```bash
# 启动 ACP 服务器
kimi acp

# 或者使用 MCP 模式
kimi mcp add kimi-code
kimi mcp start kimi-code
```

### 3. 登录/登出
```bash
kimi login   # 登录 Kimi 账号
kimi logout  # 登出
```

### 4. 查看信息
```bash
kimi info    # 版本和协议信息
```

## MCP 模式配置

如果需要通过 MCP 调用，可以使用：

```json
{
  "mcpServers": {
    "kimi-code": {
      "command": "/root/.local/bin/kimi",
      "args": ["mcp", "start", "kimi-code"]
    }
  }
}
```

## 直接调用示例

```python
import subprocess

# 调用 Kimi CLI 执行代码任务
result = subprocess.run(
    ["/root/.local/bin/kimi", "term"],
    input="帮我写一个 Python Hello World 程序",
    capture_output=True,
    text=True
)
print(result.stdout)
```

## 注意事项

- 需要先登录 Kimi 账号：`kimi login`
- ACP 模式会启动一个本地服务器
- MCP 模式需要额外配置
