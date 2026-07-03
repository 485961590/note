# CURL

cURL 是一个支持多种协议（HTTP、HTTPS、FTP 等）的命令行工具，用于发送和接收数据。

## 基本语法

```bash
curl [选项] [URL]
```

## 常用选项速查

| 选项 | 说明 |
|------|------|
| `-X, --request <METHOD>` | 指定请求方法（GET / POST / PUT / DELETE...） |
| `-H, --header <HEADER>` | 添加请求头 |
| `-A, --user-agent <STR>` | 设置 User-Agent |
| `-d, --data <DATA>` | 发送 POST 数据 |
| `--compressed` | 请求压缩响应 |
| `-F, --form <name=content>` | 上传文件（multipart/form-data） |
| `-o, --output <FILE>` | 保存到指定文件 |
| `-O, --remote-name` | 保存为远程文件名 |
| `-i, --include` | 输出包含响应头 |
| `-I, --head` | 仅获取响应头（HEAD 请求） |
| `-v, --verbose` | 详细输出 |
| `-s, --silent` | 静默模式 |
| `-S, --show-error` | 静默时仍显示错误 |
| `-f, --fail` | HTTP 错误时返回非零退出码 |
| `-k, --insecure` | 忽略 SSL 证书验证 |
| `--cacert <FILE>` | 指定 CA 证书 |
| `-L, --location` | 跟随重定向 |
| `-u, --user <user:password>` | 基本认证 |
| `--digest` | Digest 认证 |
| `-b, --cookie <data>` | 发送 Cookie |
| `-c, --cookie-jar <FILE>` | 保存 Cookie 到文件 |
| `-x, --proxy <[protocol://]host:port>` | 使用代理 |
| `--resolve <host:port:addr>` | 自定义 DNS 解析 |
| `-w, --write-out <FORMAT>` | 自定义输出格式 |
| `--connect-timeout <SEC>` | 连接超时时间 |
| `--max-time <SEC>` | 整个请求的最大时长 |
| `--retry <NUM>` | 失败重试次数 |
| `--retry-delay <SEC>` | 重试间隔时间 |
| `--retry-max-time <SEC>` | 重试总时长上限 |
| `--retry-connrefused` | 连接拒绝时也重试 |
| `-C, --continue-at <OFFSET>` | 断点续传 |
| `--limit-rate <SPEED>` | 限速下载 |

## 分类用法

### 1. 请求方法

```bash
curl http://example.com                       # GET 请求（默认）
curl -X POST http://example.com               # POST 请求
curl -X PUT http://example.com                # PUT 请求
curl -X DELETE http://example.com             # DELETE 请求
curl -I http://example.com                    # 仅获取响应头
```

### 2. 请求头与认证

```bash
curl -H "Content-Type: application/json" http://example.com
curl -H "Authorization: Bearer <token>" http://example.com
curl -u username:password http://example.com            # 基本认证
curl -b "name=value" http://example.com                 # 发送 Cookie
curl -c cookies.txt http://example.com                  # 保存 Cookie 到文件
curl -b cookies.txt http://example.com                  # 从文件加载 Cookie
```

### 3. 提交数据

```bash
curl -d "name=value" http://example.com                              # 表单数据
curl -d @data.json http://example.com                                # 从文件读取数据
curl -d '{"key":"value"}' -H "Content-Type: application/json" http://example.com  # JSON
curl -F "file=@test.txt" http://example.com                          # 文件上传
```

### 4. 文件下载

```bash
curl -O http://example.com/file.txt                  # 保存为原文件名
curl -o newname.txt http://example.com/file.txt      # 指定文件名
curl -O http://example.com/file[1-5].txt             # 批量下载
curl -C - -O http://example.com/large.zip            # 断点续传
curl --limit-rate 100k http://example.com/file.zip   # 限速下载
```

### 5. 输出控制

```bash
curl -s http://example.com                                        # 静默模式（无进度条）
curl -v http://example.com                                        # 详细输出（含请求/响应头）
curl -i http://example.com                                        # 响应包含头部
curl -w "\n状态码: %{http_code}\n" http://example.com              # 自定义输出格式
curl -o /dev/null -s -w "%{http_code}" http://example.com         # 仅输出状态码

# 静默但显示错误（脚本调试必备）
curl -s -S http://example.com

# HTTP 错误时返回非零退出码（脚本中判断成功/失败）
curl -f http://example.com/notfound

# 组合：静默 + 出错退出（自动化脚本标准写法）
curl -f -s -S -o /dev/null http://example.com/api
```

### 6. 连接与代理

```bash
curl -L http://example.com                              # 跟随重定向
curl -k https://self-signed.example.com                 # 忽略证书错误
curl -x http://127.0.0.1:8080 http://example.com        # HTTP 代理
curl -x socks5://127.0.0.1:1080 http://example.com      # SOCKS5 代理
curl --connect-timeout 10 http://example.com            # 连接超时 10 秒
```

### 7. 重试与容错

```bash
# 最多重试 3 次，每次间隔 2 秒
curl --retry 3 --retry-delay 2 http://unstable.example.com/api

# 重试总时间不超过 30 秒（防止无限重试）
curl --retry 5 --retry-max-time 30 http://unstable.example.com/api

# 连接拒绝也重试（默认 --retry 不重试 connection refused）
curl --retry 3 --retry-connrefused http://example.com

# 设置总超时 + 失败静默退出（脚本友好的健壮请求）
curl --max-time 10 -f -s -S http://example.com
```

### 8. SSL/TLS

```bash
# 指定 CA 证书验证服务器（自建 CA 或企业内网）
curl --cacert /path/to/ca-cert.pem https://example.com

# 客户端证书认证（双向 TLS / mTLS）
curl --cert client.pem --key client-key.pem https://example.com

# 指定最低 TLS 版本（禁用旧协议）
curl --tlsv1.2 https://example.com

# 忽略证书验证（仅测试用，生产环境禁用）
curl -k https://self-signed.example.com
```

## 实用场景

### API 测试

```bash
# GET API
curl -s http://api.example.com/users | jq .

# POST API（JSON）
curl -X POST http://api.example.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 携带 Token 访问
curl -H "Authorization: Bearer eyJhbG..." http://api.example.com/profile
```

### 调试与排查

```bash
# 查看完整请求/响应过程
curl -v http://example.com

# 分析各阶段耗时
curl -w "DNS: %{time_namelookup}s | TCP: %{time_connect}s | TLS: %{time_appconnect}s | TTFB: %{time_starttransfer}s | 总耗时: %{time_total}s\n" \
  -o /dev/null -s http://example.com

# 查看 HTTPS 证书信息
curl -vI https://example.com 2>&1 | grep -E "SSL|subject|expire"
```

### Web 安全测试

```bash
# 命令注入探测
curl "http://target.com/?cmd=ls"
curl "http://target.com/?cmd=cat%20/etc/passwd"

# 路径遍历探测
curl "http://target.com/?file=../../../etc/passwd"

# 枚举 HTTP 方法
curl -X OPTIONS -v http://target.com
```

### 安全下载脚本

```bash
# 先检查再执行
curl http://example.com/script.sh -o check.sh
cat check.sh        # 检查内容
bash check.sh       # 确认安全后执行

# 或直接管道查看
curl -s http://example.com/script.sh | less
```

## `-w` 常用格式化变量

| 变量 | 说明 |
|------|------|
| `%{http_code}` | HTTP 状态码 |
| `%{url_effective}` | 最终请求的 URL（跟随重定向后） |
| `%{time_total}` | 总耗时（秒） |
| `%{time_namelookup}` | DNS 解析耗时 |
| `%{time_connect}` | TCP 连接耗时 |
| `%{time_appconnect}` | TLS/SSL 握手耗时 |
| `%{time_starttransfer}` | 首字节时间（TTFB） |
| `%{size_download}` | 下载字节数 |
| `%{content_type}` | 响应 Content-Type |
| `%{http_version}` | HTTP 协议版本 |
| `%{num_redirects}` | 重定向次数 |
| `%{redirect_url}` | 重定向目标 URL |
| `%{ssl_verify_result}` | SSL 证书校验结果（0=成功） |
