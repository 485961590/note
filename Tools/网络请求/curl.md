# curl 使用指南

`curl` 用于从命令行发送和接收网络数据，最常见的用途是请求 HTTP/HTTPS 接口、查看响应、提交数据、上传和下载文件。

以下命令默认在 Linux/macOS 终端执行，`URL` 表示目标地址，`FILE` 表示本地文件。涉及账号、Token 或 Cookie 的命令只应在已授权的环境中使用。

## 1. 先确认版本

```bash
curl --version
curl --help
```

不同版本支持的参数可能略有区别。遇到 `unknown option` 时，先以本机 `curl --help` 为准。

## 2. 常用参数

| 参数                      | 作用                              |
| ----------------------- | ------------------------------- |
| `-sS`                   | 不显示进度条，但保留错误信息                  |
| `-v`                    | 显示请求和响应的详细过程                    |
| `-i`                    | 在响应正文前显示响应头                     |
| `-I`                    | 只请求响应头，常用于快速查看状态                |
| `-f`                    | HTTP 返回 4xx/5xx 时以失败退出          |
| `-L`                    | 跟随重定向                           |
| `-X METHOD`             | 指定请求方法；只有确实需要时使用                |
| `-H`                    | 添加请求头                           |
| `-d`                    | 发送请求数据，默认使用 POST                |
| `-F`                    | 以 multipart/form-data 形式提交表单或文件 |
| `-o FILE`               | 将响应保存到指定文件                      |
| `-O`                    | 按 URL 中的文件名保存                   |
| `-u USER:PASSWORD`      | 使用 HTTP Basic 认证                |
| `-b DATA`               | 发送 Cookie                       |
| `-c FILE`               | 将 Cookie 保存到文件                  |
| `-x PROXY`              | 通过代理访问                          |
| `--connect-timeout SEC` | 设置建立连接的超时时间                     |
| `--max-time SEC`        | 设置整个请求的最大时间                     |
| `--retry NUM`           | 失败时重试指定次数                       |
| `-k`                    | 跳过 HTTPS 证书校验，仅适合临时测试           |

### 复杂请求常用参数

| 参数                        | 作用                               |
| ------------------------- | -------------------------------- |
| `--compressed`            | 请求压缩响应，并自动解压 gzip、deflate 等响应    |
| `--data-raw DATA`         | 原样发送文本，不把开头的 `@` 当作文件读取          |
| `--data-urlencode DATA`   | 发送前对字段值进行 URL 编码                 |
| `--data-binary @FILE`     | 按原始字节发送文件，保留换行和内容格式              |
| `-G`                      | 把 `-d`/`--data-*` 数据放到 URL 查询字符串 |
| `-D FILE`                 | 将响应头保存到文件，正文仍输出到终端               |
| `--globoff`               | 禁用 URL 中 `[]`、`{}` 的通配展开         |
| `--http1.0` / `--http1.1` | 强制使用指定 HTTP 版本                   |
| `--trace-ascii FILE`      | 将详细收发内容写入文件，适合离线排查               |

## 3. 最基本的请求

GET 请求是默认行为：

```bash
curl https://example.com
```

只看响应头：

```bash
curl -I https://example.com
```

同时查看响应头和正文：

```bash
curl -i https://example.com
```

安静输出，但仍显示错误：

```bash
curl -sS https://example.com
```

URL 中包含 `&`、`?` 或空格时建议加引号：

```bash
curl 'https://example.com/search?q=curl&page=1'
```

## 4. 还原复杂 HTTP 请求

抓包或浏览器开发者工具复制出的请求，通常由 URL、请求头和请求体三部分组成。curl 可以重复使用多个 `-H`，请求体较复杂时使用 `--data-raw` 或 `--data-urlencode`。

下面是授权靶场中的请求构造示例：

```bash
curl --compressed -i -sS -X POST \
  'http://192.168.230.143:8080/index.php?s=captcha' \
  -H 'Host: localhost' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en' \
  -H 'User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)' \
  -H 'Connection: close' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw '_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=id'
```

各部分作用：

| 部分 | 作用 |
| --- | --- |
| `--compressed` | 告诉服务端客户端支持压缩响应，并由 curl 自动解压响应正文 |
| `-i` | 把 HTTP 响应头和正文一起输出，便于观察状态码、Cookie 和 Content-Type |
| `-sS` | 隐藏进度条，但保留网络错误 |
| `-X POST` | 明确指定 POST 方法；有请求体时也可以依靠 `--data-raw` 自动使用 POST |
| URL 中的 `?s=captcha` | 发送名为 `s` 的查询参数，和 POST 请求体是两组不同的数据 |
| 多个 `-H` | 分别添加请求头；同名请求头重复出现时要注意服务端的处理方式 |
| `Content-Type` | 告诉服务端请求体是 URL 编码表单格式 |
| `--data-raw` | 原样发送后面的字符串，不将开头的 `@` 解释为文件名 |
| `filter[]`、`server[REQUEST_METHOD]` | 表单字段名本身包含方括号，curl 会按原样发送 |

终端中应使用普通 URL，不要保留聊天或 Markdown 生成的链接格式。下面这些写法是转义或展示残留，不能直接照抄：

```text
[http://example.com](http://example.com)
\--data-raw
\_method
```

对应的终端写法是：

```text
http://example.com
--data-raw
_method
```

复杂请求也可以先写成一行，确认无误后再换成多行：

```bash
curl --compressed -i -sS -X POST 'http://192.168.230.143:8080/index.php?s=captcha' -H 'Host: localhost' -H 'Accept: */*' -H 'Accept-Language: en' -H 'User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)' -H 'Connection: close' -H 'Content-Type: application/x-www-form-urlencoded' --data-raw '_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=id'
```

### 请求体参数的选择

普通表单字段：

```bash
curl -X POST https://example.com/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw 'username=alice&remember=1'
```

让 curl 对字段值自动编码，适合值中含空格、`&` 或中文的情况：

```bash
curl -X POST https://example.com/search \
  --data-urlencode 'q=hello world'
```

从文件发送 JSON 或其他原始内容：

```bash
curl -X POST https://example.com/api \
  -H 'Content-Type: application/json' \
  --data-binary @request.json
```

`-d`、`--data-raw` 和 `--data-binary` 都可以发送请求体，但用途不同：`-d` 适合普通文本，`--data-raw` 适合不希望 `@` 被解释的文本，`--data-binary` 适合必须保留原始换行和字节内容的文件。

### 查询参数和请求体的区别

使用 `-G` 时，数据会追加到 URL，而不是放入请求体：

```bash
curl -G https://example.com/search \
  --data-urlencode 'q=hello world' \
  --data-urlencode 'page=1'
```

这相当于请求 `https://example.com/search?q=hello+world&page=1`。

### URL 中包含方括号或花括号

curl 默认可能把 URL 中的 `[]`、`{}` 当作批量请求的通配语法。需要发送字面量时加 `--globoff`：

```bash
curl --globoff 'https://example.com/api/items[id]'
```

## 5. 查看请求是否成功

curl 默认不会因为 HTTP 404 或 500 自动报错。脚本中应配合 `-f` 和 `-sS`：

```bash
curl -fsS https://example.com/api/health
```

只输出状态码：

```bash
curl -o /dev/null -sS -w '%{http_code}\n' https://example.com
```

输出状态码和最终 URL：

```bash
curl -o /dev/null -sS -L -w 'code=%{http_code} url=%{url_effective}\n' https://example.com
```

排查连接、重定向或 TLS 问题时使用详细模式：

```bash
curl -v https://example.com
```

## 6. 提交表单和 JSON

提交普通表单数据：

```bash
curl -d 'username=alice&password=example' https://example.com/login
```

提交 JSON：

```bash
curl https://example.com/api/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"alice","role":"user"}'
```

从文件读取 JSON：

```bash
curl https://example.com/api/users \
  -H 'Content-Type: application/json' \
  --data-binary @data.json
```

指定 PUT 或 DELETE 请求：

```bash
curl -X PUT https://example.com/api/users/1 \
  -H 'Content-Type: application/json' \
  -d '{"role":"admin"}'

curl -X DELETE https://example.com/api/users/1
```

`-d` 已经会将请求改为 POST，因此普通 POST 不需要再写 `-X POST`。使用 `-X` 时要确认服务确实要求该方法。

## 7. 请求头、认证和 Cookie

添加常见请求头：

```bash
curl https://example.com/api/profile \
  -H 'Accept: application/json' \
  -H 'User-Agent: my-client/1.0'
```

使用 Bearer Token：

```bash
curl https://example.com/api/profile \
  -H 'Authorization: Bearer TOKEN'
```

使用 Basic 认证：

```bash
curl -u 'USERNAME:PASSWORD' https://example.com/protected
```

直接发送 Cookie：

```bash
curl -b 'session=VALUE' https://example.com/dashboard
```

保存并复用服务端 Cookie：

```bash
curl -c cookies.txt -d 'username=alice&password=example' https://example.com/login
curl -b cookies.txt https://example.com/dashboard
```

不要把真实密码、Token 或 Cookie 直接提交到公共终端记录、脚本仓库或聊天记录中。

## 8. 文件下载和上传

指定保存路径：

```bash
curl -o output.zip https://example.com/file.zip
```

按远程文件名保存：

```bash
curl -O https://example.com/file.zip
```

跟随重定向并保存：

```bash
curl -L -o output.zip https://example.com/download
```

网络中断后继续下载：

```bash
curl -C - -O https://example.com/large-file.zip
```

上传文件：

```bash
curl -F 'file=@report.txt' https://example.com/upload
```

上传文件并附带其他表单字段：

```bash
curl -F 'file=@report.txt' -F 'description=test' https://example.com/upload
```

下载脚本或可执行文件时，先保存到本地检查内容和来源，不要直接把远程内容管道给 shell 执行。

## 9. 重定向、代理和 HTTPS

跟随 301/302 等重定向：

```bash
curl -L https://example.com
```

通过 HTTP 代理访问：

```bash
curl -x http://127.0.0.1:8080 https://example.com
```

通过 SOCKS5 代理访问：

```bash
curl -x socks5h://127.0.0.1:1080 https://example.com
```

设置连接和总超时：

```bash
curl --connect-timeout 5 --max-time 20 https://example.com
```

临时测试自签名证书：

```bash
curl -k https://internal.example.com
```

`-k` 会跳过证书校验，只适合明确的测试场景。生产环境应修复证书链或使用正确的 CA 证书，不要长期依赖 `-k`。

## 10. 重试和脚本写法

网络不稳定时重试：

```bash
curl --retry 3 --retry-delay 2 --connect-timeout 5 --max-time 30 \
  -fsS https://example.com/api/health
```

适合脚本判断成功或失败的写法：

```bash
curl -fsS -o response.json https://example.com/api/data
```

请求成功时响应写入 `response.json`，连接失败或 HTTP 返回 4xx/5xx 时返回非零退出码。

## 11. 常见问题

### 返回 301 或 302，但没有看到目标页面

添加 `-L` 跟随重定向：

```bash
curl -L https://example.com
```

### 返回 404/500，但命令仍显示成功

curl 默认只负责完成 HTTP 交换，不会把 HTTP 错误当作命令失败。使用 `-f`：

```bash
curl -fsS https://example.com/not-found
```

### JSON 请求被服务端拒绝

检查 JSON 格式，并确认添加了正确的 `Content-Type`：

```bash
curl https://example.com/api \
  -H 'Content-Type: application/json' \
  -d '{"key":"value"}'
```

在 shell 中，JSON 外层推荐使用单引号，避免双引号被 shell 先解析。

### HTTPS 证书错误

先用 `-v` 查看证书和握手信息。只有在明确是测试环境的自签名证书时，才临时使用 `-k`。

### 请求一直不结束

同时设置连接超时和总超时：

```bash
curl --connect-timeout 5 --max-time 20 -v https://example.com
```

## 快速记忆

- 普通请求：`curl URL`
- 调试请求：`curl -v URL`
- 只看状态：`curl -o /dev/null -sS -w '%{http_code}\n' URL`
- 脚本请求：`curl -fsS URL`
- JSON 请求：`curl URL -H 'Content-Type: application/json' -d '{"key":"value"}'`
- 下载文件：`curl -L -o FILE URL`
- 上传文件：`curl -F 'file=@FILE' URL`
