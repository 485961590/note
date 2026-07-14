# dirsearch

dirsearch 是一个 Web 路径暴力扫描工具，用于发现 Web 服务器上的隐藏目录和文件。

## 基本语法

```bash
python3 dirsearch.py -u <URL> [选项]
# 或直接调用（取决于安装方式）
dirsearch -u <URL> [选项]
```

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

| 选项                    | 说明             |
| --------------------- | -------------- |
| `-u, --url=URL`       | 目标 URL         |
| `-l, --url-list=FILE` | 从文件读取目标 URL 列表 |
| `--stdin`             | 从标准输入读取目标 URL  |

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

| 选项                         | 说明                          |
| -------------------------- | --------------------------- |
| `-r, --recursive`          | 对发现的目录递归扫描                  |
| `-R` `--recursion-depth=N` | 最大递归深度（默认 0；`-r` = depth 1） |
| `--scan-subdirs=DIRS`      | 递归时扫描指定子目录（逗号分隔）            |
| `--exclude-subdirs=DIRS`   | 递归时排除指定子目录                  |

### 输出

| 选项 | 说明 |
|------|------|
| `-o, --output=FILE` | 保存报告（支持 txt / json / xml / html / md） |
| `--simple-report=FILE` | 仅保存发现的路径 |
| `--plain-text-report=FILE` | 保存路径和状态码 |
| `--json-report=FILE` | JSON 格式输出 |

## 常用示例

### 一、基础扫描

```bash
# 1. 最简单的扫描（内置默认字典）
dirsearch -u http://192.168.230.128

# 2. 指定 PHP 扩展名
dirsearch -u http://192.168.230.128 -e php

# 3. 指定多个扩展名
dirsearch -u http://192.168.230.128 -e php,html,txt,zip,bak,old

# 4. 自定义线程数（默认 25）
dirsearch -u http://192.168.230.128 -e php -t 50
```

### 二、字典选择

```bash
# 5. 使用更大的字典
dirsearch -u http://192.168.230.128 -e php -w /usr/share/dirsearch/db/dicc.txt

# 6. 查看内置字典列表（字典路径/usr/lib/python3/dist-packages/dirsearch/db/）
dirsearch --wordlists 

# 7. 创建自己的小字典来测试 API 路径
echo -e "admin\nbackup\nconfig\napi\nv1\nv2\ndocs\ntest\ndev" > custom.txt
dirsearch -u http://192.168.230.128 -w custom.txt -e php
```

### 三、递归扫描

```bash
# 8. 递归扫描（发现目录后深入扫描）
dirsearch -u http://192.168.230.128 -e php -r

# 9. 限制递归深度
dirsearch -u http://192.168.230.128 -e php -R 2
```

### 四、过滤输出

```bash
# 10. 排除无用状态码，只看有价值的
dirsearch -u http://192.168.230.128 -e php -x 404,403,400

# 11. 只显示特定状态码
dirsearch -u http://192.168.230.128 -e php -i 200,302,301,401

# 12. 排除不同大小的 200 误报（bWAPP 很多页面返回 200 报错页）
dirsearch -u http://192.168.230.128 -e php --exclude-sizes=0B
```

### 五、伪装与绕过

```bash
# 13. 随机 User-Agent
dirsearch -u http://192.168.230.128 -e php --random-agent

# 14. 自定义 User-Agent（伪装 Google 爬虫）
dirsearch -u http://192.168.230.128 -e php --user-agent="Mozilla/5.0 (compatible; Googlebot/2.1)"

# 15. 请求延迟（避免触发速率限制）
dirsearch -u http://192.168.230.128 -e php --delay=0.3

# 16. 使用 Cookie（bWAPP 登录后有些页面需要 session）
dirsearch -u http://192.168.230.128 -e php --cookie="security_level=0; PHPSESSID=your_session_id"
```

### 六、输出保存

```bash
# 17. 输出为纯文本报告
dirsearch -u http://192.168.230.128 -e php -o bWAPP_scan.txt

# 18. 输出为 JSON（方便后续脚本处理）
dirsearch -u http://192.168.230.128 -e php -o bWAPP_scan.json --format=json

# 19. 同时输出多种格式
dirsearch -u http://192.168.230.128 -e php --format=json -o results.json
```

### 七、高级组合

```bash
# 20. 综合扫描（大字典 + 递归 + 多扩展名 + 伪装 + 输出）
dirsearch -u http://192.168.230.128 \
  -e php,html,txt,bak,zip,sql,inc,conf \
  -r -R 3 \
  -t 30 \
  --random-agent \
  --delay=0.2 \
  -x 404,403 \
  -o bWAPP_full.json --format=json
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
