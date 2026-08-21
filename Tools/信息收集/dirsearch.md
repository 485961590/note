# dirsearch

dirsearch 是一个基于 Python 的 Web 路径暴力扫描工具，用于发现 Web 服务器上的隐藏目录和文件，支持多线程、递归扫描与多种输出格式。

## 基本语法

```bash
dirsearch -u <URL> [选项]
```

## 一、参数速查

### 目标设置

| 选项                      | 说明                   |
| ----------------------- | -------------------- |
| `-u, --url <URL>`       | 目标 URL               |
| `-l, --url-list <FILE>` | 从文件读取目标 URL 列表（批量扫描） |

### 字典与扩展名

| 选项                       | 说明                        |
| ------------------------ | ------------------------- |
| `-w, --wordlist <FILE>`  | 自定义字典文件                   |
| `-e, --extensions <EXT>` | 文件扩展名，逗号分隔（`php,html,js`） |
| `-f, --force-extensions` | 在每个字典条目后强制附加扩展名           |

### 请求设置

| 选项 | 说明 |
|------|------|
| `-H, --header <HEADER>` | 自定义请求头（可多次使用） |
| `-c, --cookie <COOKIE>` | 设置 Cookie |
| `--user-agent <UA>` | 自定义 User-Agent |
| `--random-agent` | 随机 User-Agent |
| `--proxy <PROXY>` | 代理地址（http / https / socks5） |

### 线程与延迟

| 选项 | 说明 |
|------|------|
| `-t, --threads <N>` | 线程数，默认 25 |
| `-s, --delay <SEC>` | 每个请求间隔（秒） |
| `--timeout <SEC>` | 请求超时，默认 30 秒 |
| `--max-retries <N>` | 最大重试次数 |

### 过滤与递归

| 选项 | 说明 |
|------|------|
| `-x, --exclude-status <CODES>` | 排除指定状态码（如 `403,404`） |
| `-i, --status-codes <CODES>` | 仅显示指定状态码 |
| `-r, --recursive` | 对发现的目录递归扫描 |
| `-R, --recursion-depth <N>` | 最大递归深度（默认 0；`-r` = depth 1） |

### 输出

| 选项 | 说明 |
|------|------|
| `-o, --output <FILE>` | 保存报告（txt / json / xml / html / md） |

---

## 二、基础用法

```bash
# 1. 默认字典扫描
dirsearch -u http://target.com

# 2. 指定扩展名
dirsearch -u http://target.com -e php,html,txt,bak,zip

# 3. 自定义字典
dirsearch -u http://target.com -w custom.txt -e php

# 4. 递归扫描（发现目录后深入）
dirsearch -u http://target.com -e php -r

# 5. 排除无用状态码
dirsearch -u http://target.com -e php -x 404,403

# 6. 输出 JSON 报告
dirsearch -u http://target.com -e php -o result.json
```

---

## 三、高级用法（简述）

```bash
# 综合扫描：多扩展名 + 递归 + 伪装 + 输出
dirsearch -u http://target.com \
  -e php,html,txt,bak,zip,sql,conf \
  -r -R 3 -t 30 \
  --random-agent --delay=0.2 \
  -x 404,403 \
  -o full_result.json

# 实战示例：ASP.NET 目标（绕过 WAF、检查备份文件）
dirsearch -u http://target.com \
  -w common-medium.txt \
  -e aspx,ashx,asmx,config,cs,bak,zip \
  -t 20 --delay 0.5 --random-agent \
  -H "X-Forwarded-For: 127.0.0.1" \
  --skip-on-status 429,500 \
  --status-codes 200,403,301,302
```

提取 200 状态码的 URL：

```bash
jq -r '.results[] | select(.status == 200) | .url' result.json
```

其他特性：`-l` 加载目标列表配合 `--skip-on-status` 自动跳过无效目标做批量扫描；`--exclude-sizes` 过滤同尺寸误报。

---

## 实用技巧

- **绕过 WAF**：降低线程（`-t 5-10`）、增加延迟（`--delay 1-2`）、开启 `--random-agent`
- **提高速度**：增加线程（`-t 50-100`）、用 `--status-codes 200` 限制输出
- **缩小范围**：指定扩展名 + 状态码过滤，减少无用输出
- **批量扫描**：`-l` 加载目标列表，配合 `--skip-on-status` 自动跳过限速/异常目标
