# dirsearch

### 参数

```
-h, --help 查看帮助
-u URL, --url=URL 设置url
-L URLLIST, --url-list=URLLIST 设置url列表
-e EXTENSIONS, --extensions=EXTENSIONS 网站脚本类型
-w WORDLIST, --wordlist=WORDLIST 设置字典
-l, --lowercase 小写
-f, --force-extensions 强制扩展字典里的每个词条
-s DELAY, --delay=DELAY 设置请求之间的延时
-r, --recursive Bruteforce recursively 递归地扫描
–scan-subdir=SCANSUBDIRS, --scan-subdirs=SCANSUBDIRS 扫描给定的url的子目录(用逗号隔开)
–exclude-subdir=EXCLUDESUBDIRS, --exclude-subdirs=EXCLUDESUBDIRS 在递归过程中排除指定的子目录扫描(用逗号隔开)
-t THREADSCOUNT, --threads=THREADSCOUNT 设置扫描线程
-x EXCLUDESTATUSCODES, --exclude-status=EXCLUDESTATUSCODES 排除指定的网站状态码(用逗号隔开)
-c COOKIE, --cookie=COOKIE 设置cookie
–ua=USERAGENT, --user-agent=USERAGENT 设置用户代理
-F, --follow-redirects 跟随地址重定向扫描
-H HEADERS, --header=HEADERS 设置请求头
–random-agents, --random-user-agents 设置随机代理
–timeout=TIMEOUT 设置超时时间
–ip=IP 设置代理IP地址
–proxy=HTTPPROXY, --http-proxy=HTTPPROXY 设置http代理。例如127.0.0.1:8080
–max-retries=MAXRETRIES 设置最大的重试次数
-b, --request-by-hostname 通过主机名请求速度，默认通过IP
–simple-report=SIMPLEOUTPUTFILE 保存结果，发现的路径
–plain-text-report=PLAINTEXTOUTPUTFILE 保存结果，发现的路径和状态码
–json-report=JSONOUTPUTFILE 以json格式保存结果
```

### 2最简单的命令，只需要指定一个目标 URL（`-u` 或 `--url`）：

```
python3 dirsearch.py -u http://example.com
```

这条命令会使用默认的字典对 `http://example.com` 进行扫描。

---

### 3. 常用选项和参数

`dirsearch` 的功能非常丰富，以下是一些最常用的选项：

#### **目标相关**

- `-u URL, --url=URL`： 指定目标 URL。
- `-l FILE, --url-list=FILE`： 从一个文件中读取多个目标 URL 进行批量扫描。
- `--stdin`： 从标准输入（例如管道）读取目标 URL。

#### **字典相关**

- `-w WORDLIST, --wordlist=WORDLIST`：**指定自定义字典文件**。这是最重要的参数之一。默认使用 `db/dicc.txt`。

`python3 dirsearch.py -u http://example.com -w /path/to/your/wordlist.txt`

- `-e EXTENSION, --extensions=EXTENSION`：**指定文件扩展名**。可以指定一个或多个（用逗号分隔）。这对于发现特定类型的文件（如 PHP, ASPX, JSP 等）非常有用。

```
    # 扫描 php 和 txt 文件
    python3 dirsearch.py -u http://example.com -e php,txt
    
    # 如果你不知道扩展名，或者想扫描所有带扩展名的路径，可以使用 `-f` 强制在每个条目后附加扩展名
    python3 dirsearch.py -u http://example.com -e php,html,js -f
```

#### **输出相关**

- `-o REPORT, --output=REPORT`：**将结果保存到文件**（支持 txt, json, xml, html, md 格式）。

`python3 dirsearch.py -u http://example.com -o /path/to/report.txt`

#### **连接和速率限制**

- `-t THREADS, --threads=THREADS`： 设置并发线程数（默认 25）。增加线程数会提高速度，但也可能被目标服务器封禁或导致请求不稳定。

`python3 dirsearch.py -u http://example.com -t 50`

- `--delay DELAY`： 在每个请求之间设置延迟（秒）。
- `--timeout=TIMEOUT`： 设置请求超时时间（默认 30 秒）。
- `--max-retries=RETRIES`： 设置请求失败时的最大重试次数。

#### **代理和匿名性**

- `--proxy=PROXY`： 使用代理服务器（支持 HTTP, HTTPS, SOCKS）。

`python3 dirsearch.py -u http://example.com --proxy http://127.0.0.1:8080`

- `--proxy-list=FILE`： 使用一个代理列表文件，轮流使用其中的代理。
- `--random-agent`： 使用随机的 User-Agent 头，增加隐蔽性。
- `-H HEADER, --header=HEADER`： 添加自定义请求头（例如 Cookie、Authorization）。可以多次使用此参数来添加多个头。

```
    # 例如，携带 Cookie 进行扫描（用于扫描需要登录的区域）
    python3 dirsearch.py -u http://example.com -H "Cookie: session=your_session_value"
```

#### **过滤和匹配**

- `--exclude-status CODES`： **排除特定的 HTTP 状态码**。例如，不想看到 404 的结果。

`python3 dirsearch.py -u http://example.com --exclude-status 403,404`

- `--status-codes=CODES`： **只显示特定的 HTTP 状态码**。例如，只关注 200 和 302。

`python3 dirsearch.py -u http://example.com --status-codes 200,302,403`

- `--skip-on-status=CODES`： 如果遇到这些状态码，则跳过对该目标的扫描。

#### **递归扫描**

- `-r, --recursive`： 对发现的目录进行递归扫描。
- `--recursion-depth=DEPTH`： 设置最大递归深度（默认 0）。`-r` 相当于 `--recursion-depth=1`。

```
	# 递归扫描，深度为 2
    python3 dirsearch.py -u http://example.com -r --recursion-depth=2
```

#### **HTTP 方法**

- `-m METHOD, --http-method=METHOD`： 指定 HTTP 方法（GET, POST, HEAD, DELETE...），默认为 GET。

---

### 4. 实用命令示例

**1. 基础扫描，使用大字典和常见扩展名：**

```
python3 dirsearch.py -u http://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -e php,html,js,txt,bak,zip
```

**2. 扫描需要 Cookie 认证的路径：**

```
python3 dirsearch.py -u http://target.com/admin -H "Cookie: sessionid=1234567890" -e php
```

**3. 使用代理和随机 UA，避免被屏蔽：**

```
python3 dirsearch.py -u http://target.com --proxy socks5://127.0.0.1:9050 --random-agent
```

**4. 批量扫描目标列表，只显示状态码为 200 和 403 的结果，并保存报告：**

`python3 dirsearch.py -l targets.txt --status-codes 200,403 -o scan_results.json`

**5. 递归扫描，并设置延迟以避免触发 WAF：**

`python3 dirsearch.py -u http://target.com -r --delay 1`

---

### 5. 结果解读

扫描结束后，`dirsearch` 会在控制台以彩色表格形式输出结果。主要关注以下几列：

- **Status**： HTTP 状态码。
    - `200` (绿色)： 成功，页面存在。
    - `301`, `302` (蓝色)： 重定向，通常也表示资源存在。
    - `403` (黄色)： 禁止访问，路径存在但无权限查看。
    - `401` (黄色)： 需要认证。
    - `500` (红色)： 服务器内部错误，可能存在但脚本有错误。
    - `404` (灰色)： 未找到。
- **Size**： 响应体的大小。即使状态码相同，大小不同也可能意味着页面内容不同。
- **Redirect**： 重定向的位置（如果有）。
- **Content**： 响应头的 Content-Type。

### 针对一个ASP.NET目标，使用中型字典，绕过轻度WAF，检查备份文件，并将结果导入其他工具

==下面的\是linux中的换行但实际不影响命令，只是让输出美观==

```bash
python3 dirsearch.py \
  -u http://target.com \
  -w /path/to/wordlists/common-medium.txt \
  -e aspx,ashx,asmx,config,cs,bak,zip \ # 针对ASP.NET的扩展名
  -t 20 \ # 中等线程数
  --delay 0.5 \ # 每个请求延迟0.5秒
  --random-agent \
  -H "X-Forwarded-For: 127.0.0.1" \ # 尝试绕过IP限制
  --skip-on-status 429,500 \ # 遇到429（太多请求）或500错误就跳过
  --status-codes 200,403,301,302 \ # 只关注这些状态码
  -o json -o report.json # 输出JSON报告

# 然后使用 jq 快速提取所有发现的200状态码URL
jq -r '.results[] | select(.status == 200) | .url' report.json
```