	# gobuster

gobuster 是基于 Go 编写的多模式暴力破解工具，一个二进制覆盖多种爆破场景：目录/文件爆破（`dir`）、DNS 子域名爆破（`dns`）、虚拟主机爆破（`vhost`）、S3 存储桶枚举（`s3`）、通用模糊测试（`fuzz`）。

## 基本语法

```bash
gobuster <模式> -u <目标> -w <字典> [选项]
```

- `dir` — 目录/文件枚举（最常用）
- `dns` — DNS 子域名爆破
- `vhost` — 虚拟主机枚举
- `s3` — S3 存储桶名枚举
- `fuzz` — 通用模糊，占位符为 `FUZZ`（无花括号）

---

## 一、参数速查（dir 模式）

### 目标与字典

| 选项                        | 说明                           |
| ------------------------- | ---------------------------- |
| `-u, --url <URL>`         | 目标 URL                       |
| `-w, --wordlist <FILE>`   | 字典文件                         |
| `-x, --extensions <EXT>`  | 文件扩展名，逗号分隔（如 `php,html,bak`） |
| `--exclude-length <SIZE>` | 排除指定响应长度（去伪 404）             |
| `--wildcard`              | 强制检测通配符响应                    |
|                           |                              |

### 请求设置

| 选项 | 说明 |
|------|------|
| `-t, --threads <N>` | 线程数，默认 10 |
| `-k, --no-tls-validation` | 跳过 TLS 证书校验 |
| `-c, --cookies <STR>` | 设置 Cookie |
| `-H, --headers <STR>` | 自定义请求头 |
| `-a, --useragent <UA>` | 自定义 User-Agent |
| `--random-agent` | 随机 User-Agent |
| `--proxy <PROXY>` | 代理地址（无短形式） |
| `-r, --follow-redirect` | 跟随重定向 |
| `--delay <DUR>` | 请求间隔（如 `500ms`） |
| `--timeout <DUR>` | 请求超时 |
| `-U, --username <USER>` | Basic 认证用户名 |
| `-P, --password <PASS>` | Basic 认证密码（配合 `-U`） |

### 状态码过滤

| 选项 | 说明 |
|------|------|
| `-s, --status-codes <CODES>` | 显示指定状态码，默认 `200,204,301,302,307,401,403` |
| `-b, --status-codes-blacklist <CODES>` | 排除（黑名单）指定状态码 |

### 输出

| 选项 | 说明 |
|------|------|
| `-o, --output <FILE>` | 输出到文件 |
| `-q, --quiet` | 静默模式 |
| `-z, --no-progress` | 不显示进度条 |
| `--expanded` | 输出完整 URL |
| `-n, --no-error` | 不显示错误信息 |

---

## 二、基础用法

```bash
# 1. 目录扫描
gobuster dir -u http://target.com -w directory-list-2.3-medium.txt

# 2. 指定扩展名（找备份/源码文件）
gobuster dir -u http://target.com -w wordlist.txt -x php,html,txt,bak,zip

# 3. 只看指定状态码，排除 404
gobuster dir -u http://target.com -w wordlist.txt -s 200,301,302,403 -b 404

# 4. HTTPS 跳过证书校验 + 多线程
gobuster dir -u https://target.com -w wordlist.txt -k -t 50

# 5. 输出到文件
gobuster dir -u http://target.com -w wordlist.txt -o result.txt
```

---

## 三、其他模式

```bash
# DNS 子域名爆破
gobuster dns -d target.com -w subdomains.txt -t 50

# 虚拟主机枚举（--append-domain 自动拼接主域名）
gobuster vhost -u http://target.com -w vhosts.txt -k --append-domain

# S3 存储桶枚举
gobuster s3 -w bucketnames.txt
```

---

## 四、高级用法

### 1. fuzz 模式：任意位置模糊

`FUZZ` 关键字可放在 URL、请求头、请求体中，用 `-d` 携带 POST 数据、`-H` 自定义请求头：

```bash
# 参数值模糊
gobuster fuzz -u "http://target.com/?parameter=FUZZ" -w wordlist.txt

# 参数名模糊（观察不同响应，定位可被后端处理的参数）
gobuster fuzz -u "http://target.com/api?FUZZ=1" -w params.txt

# POST 数据模糊（-d 指定数据体）
gobuster fuzz -u http://target.com/login -w payloads.txt \
  -d "username=FUZZ&password=admin"

# 请求头模糊（伪造来源 IP / Host）
gobuster fuzz -u http://target.com/admin -w payloads.txt \
  -H "X-Forwarded-For: FUZZ"

# 输出到文件便于后续对比（-q -z 去掉横幅与进度条）
gobuster fuzz -u "http://target.com/?id=FUZZ" -w ids.txt -o fuzz_result.txt -q -z
```

### 2. dir 模式进阶

```bash
# Basic 认证（Authorization 头）
gobuster dir -u http://target.com -w wordlist.txt \
  -H "Authorization: Basic $(echo -n admin:secret | base64)"

# Cookie / 自定义头
gobuster dir -u http://target.com -w wordlist.txt -c "session=abc123"
gobuster dir -u http://target.com -w wordlist.txt -H "X-Forwarded-For: 127.0.0.1"

# 多扩展名 + 追加斜杠 + 输出含响应长度
gobuster dir -u http://target.com -w wordlist.txt -x php,bak,txt -f -l

# 目标对所有不存在路径都返回 200 时，先识别通配符响应
gobuster dir -u http://target.com -w wordlist.txt --wildcard

# 命中文件后自动探测备份（-d）
gobuster dir -u http://target.com -w wordlist.txt -x php -d

# 排除固定响应长度 + 隐藏长度列 + 输出完整 URL
gobuster dir -u http://target.com -w wordlist.txt --exclude-length 4096 --hide-length --expanded

# 代理 + 请求间隔
gobuster dir -u http://target.com -w wordlist.txt --proxy http://127.0.0.1:8080 --delay 200ms

# 断点续扫（从字典第 N 行继续）
gobuster dir -u http://target.com -w wordlist.txt --wordlist-offset 5000
```

### 3. vhost 模式进阶

```bash
# 默认：字典每行直接作为 Host 头值
gobuster vhost -u http://target.com -w vhosts.txt

# 字典只写前缀，自动拼接主域名
gobuster vhost -u http://target.com -w vhosts.txt --append-domain

# HTTPS 自签 + 排除默认站点响应长度（区分真实 vhost）
gobuster vhost -u https://target.com -w vhosts.txt -k --exclude-length 1234
```

> 原理：vhost 模式把每个候选 Host 的响应与默认 Host 响应对比，长度相同的大多是无效 vhost，用 `--exclude-length` 排除即可。

### 4. dns 模式进阶

```bash
# 自定义 DNS 解析器（绕开被污染/通配的本地 DNS）
gobuster dns -d target.com -w subdomains.txt -r 8.8.8.8

# 显示解析出的 IP 与 CNAME
gobuster dns -d target.com -w subdomains.txt -i -c

# 前缀字典自动拼到域名前 + 强制处理通配 DNS
gobuster dns -d target.com -w prefixes.txt --wildcard
```

### 5. 输出与管道处理

```bash
# 干净输出，便于 grep / awk 继续提取
gobuster dir -u http://target.com -w wordlist.txt -q -z --no-error

# 只提取命中的完整 URL（--expanded 输出完整路径）
gobuster dir -u http://target.com -w wordlist.txt -q -z --expanded | awk '{print $1}'

# 写入文件供后续处理
gobuster dir -u http://target.com -w wordlist.txt -o result.txt -z
```

### 与 ffuf 的取舍

- gobuster 默认线程 10，节奏更保守，适合快速路径枚举与低噪音场景
- ffuf 更快，匹配/过滤更精细（正则、区间、`-mmode/-fmode`），支持递归扫描（`--recursive`/`--recursion-depth`）、JSON 输出与断点续扫
- 两者对同一目标的命中通常可互相验证；追求隐蔽或跑大字典时优先 ffuf

---

## 实用技巧

- **模式切换**：一个工具覆盖目录、子域名、虚拟主机三类爆破，无需安装多个工具
- **vhost 用 `--append-domain`**：字典只写前缀（如 `admin`），自动拼成 `admin.target.com`
- **先测 `--wildcard`**：目标对所有不存在路径都返回 200 时，先识别通配符响应再过滤
- **结果管道处理**：配合 `-q -n` 输出可直接 `grep` / `awk` 继续提取
