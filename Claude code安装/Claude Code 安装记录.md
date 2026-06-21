# Claude Code 安装记录

## 环境信息

- **操作系统**: Windows 11 Home China
- **Node.js**: 已预装（可通过 `node --version` 验证）
- **网络环境**: 中国大陆，无法直连 `api.anthropic.com`

---

## 安装步骤

### 1. 安装 Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. 遇到的问题

首次启动时遇到连接错误：

```
Unable to connect to Anthropic services
Failed to connect to api.anthropic.com
```

原因：国内网络无法访问 Anthropic 的 API 服务。

### 3. 跳过首次引导流程

创建 `C:\Users\48596\.claude.json` 文件，写入以下内容以跳过引导流程：

```json
{"hasCompletedOnboarding":true}
```

验证是否生效：

```bash
type %USERPROFILE%\.claude.json
```

应输出：`{"hasCompletedOnboarding":true}`

### 4. 配置国内大模型 API

编辑 `C:\Users\48596\.claude\settings.json`，配置 DeepSeek 的 API 地址和模型：

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash"
  },
  "includeCoAuthoredBy": false,
  "model": "sonnet",
  "autoUpdatesChannel": "latest"
}
```

|配置项|说明|
|---|---|
|`ANTHROPIC_API_KEY`|DeepSeek 提供的 API 密钥|
|`ANTHROPIC_BASE_URL`|兼容 Anthropic API 的国内代理地址|
|`ANTHROPIC_DEFAULT_OPUS_MODEL`|对应 Opus 级别模型（deepseek-v4-pro）|
|`ANTHROPIC_DEFAULT_SONNET_MODEL`|对应 Sonnet 级别模型（deepseek-v4-flash）|
|`ANTHROPIC_DEFAULT_HAIKU_MODEL`|对应 Haiku 级别模型（deepseek-v4-flash）|

### 5. 验证安装

在终端中运行 `claude` 命令，如果可以正常进入交互界面，则安装成功。

---

## 配置参考

### 文件路径说明

|文件|路径|
|---|---|
|跳过引导配置文件|`%USERPROFILE%\.claude.json`|
|Claude Code 设置文件|`%USERPROFILE%\.claude\settings.json`|

### settings.json 格式参考

```json
{
  "autoUpdatesChannel": "latest",
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "你的令牌",
    "ANTHROPIC_BASE_URL": "你的地址",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "大模型1",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "大模型2",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "大模型3",
  },
  "includeCoAuthoredBy": false
}
```

> 注：`ANTHROPIC_AUTH_TOKEN` 与 `ANTHROPIC_API_KEY` 作用类似，根据服务商要求选择其一即可。

---

## 总结

在国内使用 Claude Code 的关键两步：

1. **跳过引导** - 创建 `.claude.json` 标记引导已完成
2. **配置 API** - 修改 `settings.json`，将 API 地址指向国内可访问的兼容服务（如 DeepSeek）