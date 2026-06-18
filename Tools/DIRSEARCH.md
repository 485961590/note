# dirsearch

dirsearch 是一个 Web 路径暴力扫描工具，用于发现 Web 服务器上的隐藏目录和文件。

## 快速开始

```bash
# 基本扫描
python3 dirsearch.py -u http://target.com

# 指定字典和扩展名
python3 dirsearch.py -u http://target.com -w /path/to/wordlist.txt -e php,html,js

# 批量扫描，输出 JSON 报告
python3 dirsearch.py -l targets.txt -o report.json
```

## 选项速查

### 目标设置

| 选项 | 说明 |
|------|------|
| `-u, --url=URL` | 目标 URL |
| `-l, --url-list=FILE` | 从文件读取目标 URL 列表 |
| `--stdin` | 从标准输入读取目标 URL |

### 字典与扩展名

| 选项 | 说明 |
|------|------|
| `-w, --wordlist=FILE` | 自定义字典文件 |
| `-e, --extensions=EXT` | 文件扩展名，逗号分隔（`php,html,js`） |
| `-f, --force-extensions` | 在每个字典条目后强制附加扩展名 |
| `-l, --lowercase` | 字典条目转为小写 |

### 请求配置

| 选项 | 说明 |
|------|------|
| `-m, --http-method=METHOD` | HTTP 方法（GET / POST / HEAD...），默认 GET |
| `-H, --header=HEADER` | 自定义请求头（可多次使用） |
| `-c, --cookie=COOKIE` | 设置 Cookie |
| `--user-agent=UA` | 自定义 User-Agent |
| `--random-agent` | 随机 User-Agent |
| `-F, --follow-redirects` | 跟随重定向 |
| `-b, --request-by-hostname` | 通过主机名请求（默认通过 IP） |

### 速率与性能

| 选项 | 说明 |
|------|------|
| `-t, --threads=N` | 线程数，默认 25 |
| `-s, --delay=SEC` | 每个请求间隔（秒） |
| `--timeout=SEC` | 请求超时，默认 30 秒 |
| `--max-retries=N` | 最大重试次数 |

### 代理

| 选项 | 说明 |
|------|------|
| `--proxy=PROXY` | 代理地址（http / https / socks5） |
| `--proxy-list=FILE` | 代理列表文件 |
| `--ip=IP` | 代理 IP 地址 |

### 过滤与匹配

| 选项 | 说明 |
|------|------|
| `-x, --exclude-status=CODES` | 排除指定状态码（如 `403,404`） |
| `--status-codes=CODES` | 仅显示指定状态码 |
| `--skip-on-status=CODES` | 遇到这些状态码时跳过该目标 |

### 递归扫描

| 选项 | 说明 |
|------|------|
| `-r, --recursive` | 对发现的目录递归扫描 |
| `--recursion-depth=N` | 最大递归深度（默认 0；`-r` = depth 1） |
| `--scan-subdirs=DIRS` | 递归时扫描指定子目录（逗号分隔） |
| `--exclude-subdirs=DIRS` | 递归时排除指定子目录 |

### 输出

| 选项 | 说明 |
|------|------|
| `-o, --output=FILE` | 保存报告（支持 txt / json / xml / html / md） |
| `--simple-report=FILE` | 仅保存发现的路径 |
| `--plain-text-report=FILE` | 保存路径和状态码 |
| `--json-report=FILE` | JSON 格式输出 |

## 常用示例

### 1. 基础扫描

```bash
# 默认字典 + 常见扩展名
python3 dirsearch.py -u http://target.com -e php,html,js,txt,bak,zip

# 使用大字典
python3 dirsearch.py -u http://target.com \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -e php,html,js
```

### 2. 带认证的扫描

```bash
# 携带 Cookie 扫描需要登录的路径
python3 dirsearch.py -u http://target.com/admin \
  -H "Cookie: sessionid=abc123" \
  -e php

# 携带多个请求头
python3 dirsearch.py -u http://target.com \
  -H "Authorization: Bearer token123" \
  -H "X-Custom: value"
```

### 3. 隐蔽扫描（避免被封）

```bash
# 代理 + 随机 UA + 低线程 + 延迟
python3 dirsearch.py -u http://target.com \
  --proxy socks5://127.0.0.1:9050 \
  --random-agent \
  --delay 0.5 \
  -t 10
```

### 4. 高级过滤

```bash
# 只看有效结果
python3 dirsearch.py -u http://target.com --status-codes 200,301,302,403

# 排除干扰
python3 dirsearch.py -u http://target.com --exclude-status 404,500,502

# 批量扫描，自动跳过被限速的目标
python3 dirsearch.py -l targets.txt --skip-on-status 429
```

### 5. 递归扫描（限速防 WAF）

```bash
python3 dirsearch.py -u http://target.com \
  -r --recursion-depth 2 \
  --delay 1 \
  --exclude-status 404
```

## 结果解读

| 状态码 | 颜色 | 含义 |
|--------|------|------|
| **200** | 绿色 | 成功，资源存在 |
| **301 / 302** | 蓝色 | 重定向，通常资源也存在 |
| **401** | 黄色 | 需要认证 |
| **403** | 黄色 | 禁止访问，路径存在但无权限 |
| **404** | 灰色 | 未找到 |
| **500** | 红色 | 服务器错误，可能存在但脚本报错 |

关键字段：
- **Status** — HTTP 状态码
- **Size** — 响应体大小；相同状态码不同大小可能意味着不同内容
- **Redirect** — 重定向目标（如有）
- **Content** — 响应 Content-Type

## 实战示例：ASP.NET 目标

针对 ASP.NET 站点，使用中型字典，绕过轻度 WAF，检查备份文件：

```bash
python3 dirsearch.py \
  -u http://target.com \
  -w /path/to/wordlists/common-medium.txt \
  -e aspx,ashx,asmx,config,cs,bak,zip \
  -t 20 \
  --delay 0.5 \
  --random-agent \
  -H "X-Forwarded-For: 127.0.0.1" \
  --skip-on-status 429,500 \
  --status-codes 200,403,301,302 \
  -o report.json
```

各参数说明：
| 参数 | 作用 |
|------|------|
| `-e aspx,ashx,...` | 针对 ASP.NET 的常见扩展名 |
| `-t 20` | 中等线程数，避免触发封禁 |
| `--delay 0.5` | 每个请求延迟 0.5 秒 |
| `-H "X-Forwarded-For: ..."` | 伪造请求来源，尝试绕过 IP 限制 |
| `--skip-on-status 429,500` | 遇到限速或服务器错误跳过目标 |
| `--status-codes ...` | 仅关注有意义的状态码 |

提取 200 状态码的 URL：

```bash
jq -r '.results[] | select(.status == 200) | .url' report.json
```

## 实用技巧

- **绕过 WAF**：降低线程 (`-t 5-10`)，增加延迟 (`--delay 1-2`)，开启 `--random-agent`
- **提高速度**：增加线程 (`-t 50-100`)，限制状态码 (`--status-codes 200`)
- **缩小范围**：指定扩展名 (`-e php`) + 状态码过滤，减少无用输出
- **批量扫描**：用 `-l` 加载目标列表，配合 `--skip-on-status` 自动跳过无效目标
