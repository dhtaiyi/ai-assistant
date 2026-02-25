# TOOLS.md - Tool Configuration & Notes

> Document tool-specific configurations, gotchas, and credentials here.

---

## 🤖 代理配置

### 小 u (Kimi 代码助手)
- **位置**: `/root/.openclaw/agents/xiaoyu/`
- **CLI**: `@jacksontian/kimi-cli` v1.2.0
- **命令路径**: `/root/.nvm/versions/node/v22.22.0/bin/kimi`
- **默认模型**: `moonshot-v1-8k`
- **API Key**: 首次运行 `kimi` 命令时设置
- **配置指南**: `/root/.openclaw/agents/xiaoyu/agent/KIMI_SETUP.md`

---

## ⚠️ Config Modification Safety Rule

**Before editing any config file, ALWAYS backup first!**

```bash
# Step 1: Backup
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# Step 2: Edit
# ... make your changes ...

# Step 3: Verify & Test
# If something breaks:

# Step 4: Restore if needed
mv ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
```

This rule applies to all config files in `~/.openclaw/`.

---

## Credentials Location

All credentials stored in `.credentials/` (gitignored):
- `example-api.txt` — Example API key

---

## [Tool Name]

**Status:** ✅ Working | ⚠️ Issues | ❌ Not configured

**Configuration:**
```
Key details about how this tool is configured
```

**Gotchas:**
- Things that don't work as expected
- Workarounds discovered

**Common Operations:**
```bash
# Example command
tool-name --common-flag
```

---

## Writing Preferences

[Document any preferences about writing style, voice, etc.]

---

## What Goes Here

- Tool configurations and settings
- Credential locations (not the credentials themselves!)
- Gotchas and workarounds discovered
- Common commands and patterns
- Integration notes

## Why Separate?

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

---

*Add whatever helps you do your job. This is your cheat sheet.*
