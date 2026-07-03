# curl 练习测试清单

基于本项目的 20 个 API 端点，从零开始逐步掌握 curl。

---

## 第一阶段：基础入门

### 1.1 最简单的 GET 请求

```bash
curl http://localhost:5000/api/echo
```

学到的知识点：
- [ ] curl 默认发 GET 请求
- [ ] 不加任何参数时，curl 把响应体直接输出到终端

### 1.2 查看完整响应（含状态码和响应头）

```bash
curl -i http://localhost:5000/api/echo
curl -i http://localhost:5000/api/status/404
curl -i http://localhost:5000/api/status/500
```

学到的知识点：
- [ ] `-i` 显示响应头和状态行
- [ ] 第一行是 `HTTP/1.1 200 OK` 或 `HTTP/1.1 404 NOT FOUND`

### 1.3 只看响应头

```bash
curl -I http://localhost:5000/api/echo
```

学到的知识点：
- [ ] `-I` 发送 HEAD 请求，只获取响应头
- [ ] 和 `-i` 的区别：`-I` 不下载 body

### 1.4 静默模式

```bash
curl -s http://localhost:5000/api/echo
curl -s -o /dev/null http://localhost:5000/api/echo
```

学到的知识点：
- [ ] `-s` 隐藏进度条和错误信息
- [ ] `-o /dev/null` 丢弃响应体，只看状态码时常用

---

## 第二阶段：HTTP 方法

### 2.1 POST 请求

```bash
curl -X POST http://localhost:5000/api/methods
```

学到的知识点：
- [ ] `-X` 指定 HTTP 方法

### 2.2 所有方法都试一遍

```bash
curl -X GET     http://localhost:5000/api/methods
curl -X POST    http://localhost:5000/api/methods
curl -X PUT     http://localhost:5000/api/methods
curl -X DELETE  http://localhost:5000/api/methods
curl -X PATCH   http://localhost:5000/api/methods
curl -X OPTIONS http://localhost:5000/api/methods
curl -X HEAD    http://localhost:5000/api/methods
```

学到的知识点：
- [ ] GET 是默认方法，不加 `-X` 也是 GET
- [ ] HEAD 返回空 body

### 2.3 OPTIONS 的特殊性

```bash
curl -i -X OPTIONS http://localhost:5000/api/methods
curl -i -X OPTIONS http://localhost:5000/api/cors -H "Origin: https://example.com"
```

学到的知识点：
- [ ] OPTIONS 用于 CORS 预检，返回 `Allow` 头
- [ ] `-H` 添加自定义请求头

---

## 第三阶段：请求头与请求体

### 3.1 自定义请求头

```bash
curl -H "User-Agent: MyBrowser/1.0" http://localhost:5000/api/echo
curl -H "Authorization: Bearer mytoken123" http://localhost:5000/api/echo
curl -H "X-Debug: true" -H "Accept-Language: zh-CN" http://localhost:5000/api/echo
```

学到的知识点：
- [ ] `-H` 设置请求头，可重复使用多次
- [ ] 用 `/api/echo` 查看你发送的请求头是否如预期

### 3.2 发送 JSON 数据

```bash
curl -X POST http://localhost:5000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"name": "curl", "version": 1.0}'
```

学到的知识点：
- [ ] `-d` 发送请求体
- [ ] 必须配合 `Content-Type` 头告诉服务器数据格式

### 3.3 发送表单数据

```bash
curl -X POST http://localhost:5000/api/echo \
  -d "username=admin" -d "password=secret123"
```

```bash
curl -X POST http://localhost:5000/api/echo \
  --data-urlencode "name=hello world" --data-urlencode "q=curl tutorial"
```

学到的知识点：
- [ ] 不加 Content-Type 时默认 `application/x-www-form-urlencoded`
- [ ] `--data-urlencode` 自动对特殊字符进行 URL 编码

### 3.4 发送原始二进制数据

```bash
echo "Hello, curl!" | curl -X POST http://localhost:5000/api/size -d @-
```

```bash
curl -X POST http://localhost:5000/api/size -d @- <<< "测试 stdin 输入"
```

学到的知识点：
- [ ] `-d @-` 从标准输入读取数据
- [ ] 管道和重定向与 curl 结合使用

### 3.5 测量请求体大小

```bash
curl -X POST http://localhost:5000/api/size -d "Hello, HTTP!"
curl -X POST http://localhost:5000/api/size \
  -H "Content-Type: application/json" \
  -d '{"data": [1,2,3,4,5]}'
```

学到的知识点：
- [ ] 对比 `Content-Length` 请求头和实际 body 大小
- [ ] 不同编码方式下 body 大小的差异

---

## 第四阶段：URL 与参数

### 4.1 URL 查询参数

```bash
curl "http://localhost:5000/api/echo?name=curl&version=1.0"
curl "http://localhost:5000/api/custom-headers?X-Token=abc123&X-Debug=true"
```

学到的知识点：
- [ ] URL 中的 `?key=value` 是查询参数
- [ ] 用引号包裹 URL 防止 shell 对 `&` 的特殊解释

### 4.2 URL 编码

```bash
curl --get --data-urlencode "q=curl 教程" --data-urlencode "lang=zh-CN" \
  http://localhost:5000/api/echo
```

学到的知识点：
- [ ] `--get` 将 `-d` 参数转为 URL 查询参数
- [ ] `--data-urlencode` 自动编码中文和特殊字符

### 4.3 路径参数

```bash
curl http://localhost:5000/api/status/200
curl http://localhost:5000/api/status/301
curl http://localhost:5000/api/status/404
curl http://localhost:5000/api/status/500
curl http://localhost:5000/api/delay/3
```

学到的知识点：
- [ ] RESTful API 路径中可以包含可变部分

### 4.4 内容类型参数

```bash
curl http://localhost:5000/api/content-type/json
curl http://localhost:5000/api/content-type/xml
curl http://localhost:5000/api/content-type/html
curl http://localhost:5000/api/content-type/csv
```

学到的知识点：
- [ ] 同一个 URL 路径可以返回不同格式的响应

---

## 第五阶段：重定向

### 5.1 观察重定向过程

```bash
curl -i http://localhost:5000/api/redirect?type=301
curl -i http://localhost:5000/api/redirect?type=302
```

学到的知识点：
- [ ] 301/302 响应中有 `Location` 头指示新地址
- [ ] 默认 curl 不跟随重定向

### 5.2 跟随重定向

```bash
curl -L http://localhost:5000/api/redirect?type=301
curl -L http://localhost:5000/api/redirect?type=302
```

学到的知识点：
- [ ] `-L` 自动跟随重定向

### 5.3 不同类型重定向的区别

```bash
curl -L -i http://localhost:5000/api/redirect?type=301&to=/api/echo
curl -L -i http://localhost:5000/api/redirect?type=302&to=/api/echo
curl -L -i http://localhost:5000/api/redirect?type=307&to=/api/echo
curl -L -i http://localhost:5000/api/redirect?type=308&to=/api/echo
```

学到的知识点：
- [ ] 301/308 永久重定向，302/303/307 临时重定向
- [ ] 307/308 保持原始 HTTP 方法不变
- [ ] 用 `-i` 可以看到每次跳转的响应

### 5.4 链式重定向

```bash
curl -L -i http://localhost:5000/api/redirect?n=3&to=/api/echo
```

学到的知识点：
- [ ] 最多允许 5 次链式跳转
- [ ] `--max-redirs` 限制最大跳转次数

---

## 第六阶段：Cookie

### 6.1 服务器设置 Cookie

```bash
curl -i http://localhost:5000/api/cookie/set?name=session&value=abc123
```

学到的知识点：
- [ ] `Set-Cookie` 响应头让浏览器保存 cookie

### 6.2 保存 Cookie

```bash
curl -c cookies.txt http://localhost:5000/api/cookie/set?name=session&value=abc123
cat cookies.txt
```

学到的知识点：
- [ ] `-c` 将 cookie 保存到文件
- [ ] 查看 cookie 文件的格式（domain, flag, path, secure, expiry, name, value）

### 6.3 发送 Cookie

```bash
curl -b cookies.txt http://localhost:5000/api/cookie/get
```

学到的知识点：
- [ ] `-b` 从文件读取 cookie 并发送

### 6.4 手动发送 Cookie

```bash
curl -H "Cookie: session=abc123; theme=dark" http://localhost:5000/api/cookie/get
```

学到的知识点：
- [ ] Cookie 本质就是 `Cookie` 请求头
- [ ] 多个 cookie 用 `; ` 分隔

### 6.5 Cookie 属性测试

```bash
curl -c cookies.txt -i "http://localhost:5000/api/cookie/set?name=test&value=123&http_only=1&max_age=3600&secure=1&same_site=Lax"
cat cookies.txt
```

学到的知识点：
- [ ] HttpOnly：JS 无法读取，防 XSS
- [ ] Secure：仅 HTTPS 下发送
- [ ] SameSite：防 CSRF

---

## 第七阶段：认证

### 7.1 Basic 认证 — 未认证时

```bash
curl -i http://localhost:5000/api/basic-auth
```

学到的知识点：
- [ ] 401 状态码 + `WWW-Authenticate` 挑战头

### 7.2 Basic 认证 — 手动构造

```bash
echo -n "admin:secret123" | base64
curl -i -H "Authorization: Basic $(echo -n admin:secret123 | base64)" http://localhost:5000/api/basic-auth
```

学到的知识点：
- [ ] Basic 认证格式：`Basic base64(username:password)`
- [ ] base64 是可逆的，不是加密！

### 7.3 Basic 认证 — 简写

```bash
curl -u admin:secret123 http://localhost:5000/api/basic-auth
curl -u wrong:password http://localhost:5000/api/basic-auth
```

学到的知识点：
- [ ] `-u` 是 Basic 认证的快捷方式
- [ ] curl 会自动计算 base64

### 7.4 Digest 认证 — 自动协商

```bash
curl -i --digest -u admin:secret123 http://localhost:5000/api/digest-auth
```

学到的知识点：
- [ ] Digest 认证不会在第一次请求时发送密码
- [ ] 服务器先返回 401 + 挑战（nonce、realm 等）
- [ ] curl 计算哈希响应并重试
- [ ] `--digest` 告诉 curl 使用 Digest 方式

### 7.5 Digest 认证过程拆解

```bash
# 第一步：看服务器发来的挑战
curl -i http://localhost:5000/api/digest-auth

# 第二步：看完整认证过程
curl -i --digest -u admin:secret123 http://localhost:5000/api/digest-auth -v
```

学到的知识点：
- [ ] `-v` 显示通信的每个步骤
- [ ] 对比 Basic Auth（一步）和 Digest Auth（两步握手）
- [ ] Digest 比 Basic 更安全（不传输明文密码）

---

## 第八阶段：HTTP 高级特性

### 8.1 压缩

```bash
# 不加 --compressed，收到未压缩的原始内容
curl -i http://localhost:5000/api/compress

# 加 --compressed，请求 gzip 压缩
curl -i --compressed http://localhost:5000/api/compress
```

学到的知识点：
- [ ] `--compressed` 设置 `Accept-Encoding: gzip` 并自动解压
- [ ] 对比两次的响应大小和 `Content-Encoding` 头

### 8.2 条件请求 (ETag / 304)

```bash
# 第一次请求，获取 ETag
curl -i http://localhost:5000/api/etag

# 复制输出的 ETag 值（例如 "abc123..."），然后：
ETAG='"8101b6fdc79e87ecf00f92d8b136a107680a57a6bb619ff50b322a2900024505"'
curl -i -H "If-None-Match: $ETAG" http://localhost:5000/api/etag
```

学到的知识点：
- [ ] ETag 是内容的指纹/版本号
- [ ] `If-None-Match` 告诉服务器：如果内容没变就别发 body
- [ ] `304 Not Modified` 响应节省带宽

### 8.3 范围请求 (断点续传)

```bash
# 先看完整文件大小
curl -i http://localhost:5000/api/range | head -20

# 请求前 100 字节
curl -i -H "Range: bytes=0-99" http://localhost:5000/api/range

# 请求中间的一段
curl -i -H "Range: bytes=1000-1999" http://localhost:5000/api/range

# 请求最后 50 字节
curl -i -H "Range: bytes=-50" http://localhost:5000/api/range
```

学到的知识点：
- [ ] `206 Partial Content` 部分内容响应
- [ ] `Content-Range` 指示返回的字节范围
- [ ] `Range: bytes=-50` 后缀范围，取最后 N 字节

### 8.4 curl 断点续传

```bash
# 从第 200 字节开始下载
curl -C 200 http://localhost:5000/api/range
```

学到的知识点：
- [ ] `-C` 自动设置 `Range` 头实现断点续传
- [ ] 对比手动设置 `Range: bytes=200-` 的效果

### 8.5 CORS 跨域

```bash
# 简单请求
curl -i http://localhost:5000/api/cors -H "Origin: https://myapp.com"

# 预检请求
curl -i -X OPTIONS http://localhost:5000/api/cors \
  -H "Origin: https://myapp.com" \
  -H "Access-Control-Request-Method: POST"
```

学到的知识点：
- [ ] `Access-Control-Allow-Origin` 决定哪些域可以跨域访问
- [ ] 浏览器的 CORS 检查和服务器返回的 CORS 头
- [ ] 预检请求先飞 OPTIONS，再飞实际请求

### 8.6 自定义响应头

```bash
curl -i "http://localhost:5000/api/custom-headers?X-Custom-Token=abc123&X-Rate-Limit=100"
```

学到的知识点：
- [ ] 响应头可以是自定义的（`X-` 前缀是约定）
- [ ] 用 curl 验证你的 API 是否返回了正确的头

### 8.7 JSONP

```bash
curl "http://localhost:5000/api/jsonp?callback=myFunction"
```

学到的知识点：
- [ ] JSONP 返回的不是纯 JSON，而是函数调用
- [ ] 用于跨域数据加载（CORS 出现前的老方法）

### 8.8 速率限制

```bash
# 连续请求 7 次，看第 6、7 次被限
for i in {1..7}; do
  echo "--- Request $i ---"
  curl -i -s "http://localhost:5000/api/rate-limit?limit=5" | grep -E "HTTP|remaining|error"
done
```

学到的知识点：
- [ ] `X-RateLimit-Remaining` 剩余次数
- [ ] `429 Too Many Requests` 状态码
- [ ] `Retry-After` 建议等待时间
- [ ] 用脚本模拟高并发请求

---

## 第九阶段：文件操作

### 9.1 下载文件

```bash
curl -o output.txt http://localhost:5000/api/content-type/plain
curl -o data.json http://localhost:5000/api/content-type/json
```

学到的知识点：
- [ ] `-o` 指定输出文件名

### 9.2 使用远程文件名保存

```bash
curl -O http://localhost:5000/api/content-type/csv
```

学到的知识点：
- [ ] `-O` 使用 URL 末尾部分作为文件名

### 9.3 上传文件

```bash
# 创建一个测试文件
echo "Hello, this is a test file for upload" > test_upload.txt

# 上传
curl -F "file=@test_upload.txt" http://localhost:5000/api/upload

# 上传多个文件
curl -F "file1=@test_upload.txt" -F "file2=@test_upload.txt" http://localhost:5000/api/upload

# 清理
rm test_upload.txt
```

学到的知识点：
- [ ] `-F` 发送 multipart/form-data（文件上传）
- [ ] `@` 前缀表示从文件读取内容
- [ ] 对比 `-d`（URL 编码）和 `-F`（multipart）的区别

### 9.4 上传大文件（测试限制）

```bash
# 创建一个大于 1MB 的文件
dd if=/dev/zero of=large_file.bin bs=1024 count=1500 2>/dev/null

# 上传，应该返回 413
curl -i -F "file=@large_file.bin" http://localhost:5000/api/upload

rm large_file.bin
```

学到的知识点：
- [ ] `413 Payload Too Large` 状态码
- [ ] 服务器有文件大小限制

---

## 第十阶段：超时与性能

### 10.1 超时控制

```bash
# 请求一个 5 秒后才响应的接口，但 2 秒就放弃
curl --max-time 2 http://localhost:5000/api/delay/5
```

学到的知识点：
- [ ] `--max-time` 整个请求的最长等待时间
- [ ] 超时显示 `curl: (28) Connection timed out`

### 10.2 连接超时 vs 总超时

```bash
# --connect-timeout 只限制连接阶段
curl --connect-timeout 3 http://localhost:5000/api/delay/5
```

学到的知识点：
- [ ] `--connect-timeout` 连接超时 vs `--max-time` 总超时
- [ ] 连接成功后仍会等待响应完成

### 10.3 测量响应时间

```bash
curl -w "\n\n--- 时间统计 ---\n\
  连接时间: %{time_connect}s\n\
  TLS 握手: %{time_appconnect}s\n\
  首字节时间: %{time_starttransfer}s\n\
  总时间: %{time_total}s\n\
  下载大小: %{size_download} bytes\n" \
  -o /dev/null -s http://localhost:5000/api/delay/1
```

学到的知识点：
- [ ] `-w` 自定义输出格式
- [ ] 理解 HTTP 请求各个阶段的时间

### 10.4 速率限制

```bash
# 限制下载速度（模拟慢速网络）
curl --limit-rate 1k http://localhost:5000/api/compress -o /dev/null
```

学到的知识点：
- [ ] `--limit-rate` 限制下载速度，单位 K/M/G

---

## 第十一阶段：查看与调试

### 11.1 详细输出

```bash
curl -v http://localhost:5000/api/echo
```

学到的知识点：
- [ ] `-v` 显示请求头和响应头、TLS 握手细节
- [ ] `>` 开头的行是发出去的请求头
- [ ] `<` 开头的行是收到的响应头

### 11.2 只看请求头（不发送）

```bash
curl -v --request-target http://localhost:5000/api/echo
```

### 11.3 跟踪重定向过程

```bash
curl -v -L http://localhost:5000/api/redirect?n=3&to=/api/echo 2>&1
```

学到的知识点：
- [ ] 用 `-v` 可以看到 curl 自动跟随重定向的每一步

### 11.4 写到文件同时打印到终端

```bash
curl -o saved.txt -v http://localhost:5000/api/echo
cat saved.txt
```

---

## 第十二阶段：综合练习

### 12.1 模拟浏览器请求

```bash
curl -v \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: text/html,application/json,*/*" \
  -H "Accept-Language: zh-CN,en;q=0.9" \
  http://localhost:5000/api/echo
```

### 12.2 完整的 API 调用（认证 + 数据 + 处理结果）

```bash
# 登录获取 token（简化版）
TOKEN=$(echo -n admin:secret123 | base64)

# 使用 token 获取数据
curl -s -H "Authorization: Basic $TOKEN" http://localhost:5000/api/echo | python3 -m json.tool

# 带数据处理
curl -s http://localhost:5000/api/check?url=https://example.com | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'检查结果: {data[\"present_count\"]}/{data[\"total\"]} 个安全头已配置')
for r in data['results']:
    status = 'OK' if r['present'] else 'MISSING'
    print(f'  [{status}] {r[\"header\"]}')
"
```

### 12.3 从文件读取请求体

```bash
cat > request.json << 'EOF'
{"name": "curl练习", "difficulty": "入门到进阶"}
EOF

curl -X POST -H "Content-Type: application/json" -d @request.json \
  http://localhost:5000/api/echo

rm request.json
```

### 12.4 写一个监控脚本

```bash
#!/bin/bash
# 每分钟检查一次安全头，状态变化时告警
while true; do
  result=$(curl -s "http://localhost:5000/api/check?url=https://example.com")
  passed=$(echo "$result" | python3 -c "import sys,json;print(json.load(sys.stdin)['present_count'])")
  date_str=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$date_str] 安全头已配置: $passed/7"
  sleep 60
done
```

---

## 练习清单汇总

| 阶段 | 技能点 | 完成 |
|------|--------|------|
| 1.基础 | `-i` 看响应头 | [ ] |
| 1.基础 | `-I` 只看头 | [ ] |
| 1.基础 | `-s` 静默 | [ ] |
| 1.基础 | `-o` 保存到文件 | [ ] |
| 2.方法 | `-X` 指定方法 | [ ] |
| 2.方法 | OPTIONS 与 Allow | [ ] |
| 3.请求头 | `-H` 自定义头 | [ ] |
| 3.请求体 | `-d` 发送数据 | [ ] |
| 3.请求体 | `--data-urlencode` | [ ] |
| 3.请求体 | `-d @-` stdin 输入 | [ ] |
| 3.请求体 | `Content-Type` 控制 | [ ] |
| 4.参数 | URL 查询参数 | [ ] |
| 4.参数 | `--get` 参数转查询 | [ ] |
| 4.参数 | 路径参数 | [ ] |
| 5.重定向 | `-L` 跟随 | [ ] |
| 5.重定向 | 301/302/307/308 区别 | [ ] |
| 5.重定向 | 链式跳转 | [ ] |
| 6.Cookie | `-c` 保存 | [ ] |
| 6.Cookie | `-b` 发送 | [ ] |
| 6.Cookie | HttpOnly/Secure/SameSite | [ ] |
| 7.认证 | `-u` Basic Auth | [ ] |
| 7.认证 | 手动构造 `Authorization` 头 | [ ] |
| 7.认证 | `--digest` Digest 认证 | [ ] |
| 7.认证 | `-v` 观察握手过程 | [ ] |
| 8.压缩 | `--compressed` | [ ] |
| 8.ETag | `If-None-Match` + 304 | [ ] |
| 8.Range | `Range` 头 + 206 | [ ] |
| 8.Range | `-C` 断点续传 | [ ] |
| 8.CORS | 预检 OPTIONS | [ ] |
| 8.JSONP | callback 格式 | [ ] |
| 8.限流 | 429 / Retry-After | [ ] |
| 9.文件 | `-O` 下载 | [ ] |
| 9.文件 | `-F` 上传 multipart | [ ] |
| 9.文件 | 413 大小限制 | [ ] |
| 10.超时 | `--max-time` | [ ] |
| 10.超时 | `--connect-timeout` | [ ] |
| 10.性能 | `-w` 自定义输出 | [ ] |
| 10.性能 | `--limit-rate` 限速 | [ ] |
| 11.调试 | `-v` 详细输出 | [ ] |
| 11.调试 | 跟踪重定向 | [ ] |
| 12.综合 | 模拟浏览器 | [ ] |
| 12.综合 | 管道 + Python 处理 | [ ] |
| 12.综合 | `-d @file` 从文件读取 | [ ] |

---

## 快速参考卡片

```bash
# ---- 最常用 ----
curl -i URL          # 看响应头和 body
curl -I URL          # 只看响应头
curl -s URL          # 静默
curl -v URL          # 调试模式
curl -L URL          # 跟随重定向
curl -o file URL     # 保存到文件
curl -u user:pass    # Basic 认证
curl -H "K: v"       # 自定义头
curl -d "data"       # POST 数据
curl -F "f=@file"    # 上传文件
curl --compressed    # 请求压缩
curl -c jar          # 保存 cookie
curl -b jar          # 发送 cookie
```

---

> **项目端点速查**：浏览器打开 http://localhost:5000/ 可查看所有 20 个端点及示例命令。
